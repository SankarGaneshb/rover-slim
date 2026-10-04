import os
import json
import re
from typing import List, Tuple, Optional, Any, Dict
from rover_slim.languages.base import BaseLanguageAdapter
from rover_slim.models import PrunedPackage, ProbeConfig, RoverSlimConfig
from rover_slim.parsers.req_parser import RequirementEntry

class NodeLanguageAdapter(BaseLanguageAdapter):
    """
    Concrete language adapter for Node.js and TypeScript applications.
    Parses package.json, segregates devDependencies, discovers framework health routes,
    and synthesizes production-hardened Node multi-stage Dockerfiles.
    """

    DEV_TOOLING_PATTERNS = [
        r"^@types/",
        r"^eslint",
        r"^prettier",
        r"^jest",
        r"^vitest",
        r"^mocha",
        r"^chai",
        r"^cypress",
        r"^playwright",
        r"^typescript$",
        r"^ts-node",
        r"^nodemon",
        r"^webpack",
        r"^vite",
        r"^rollup",
        r"^esbuild",
        r"^babel",
        r"^turbo",
        r"^supertest"
    ]

    @property
    def name(self) -> str:
        return "nodejs"

    @property
    def display_name(self) -> str:
        return "Node.js / TypeScript"

    def detect(self, root_dir: str) -> bool:
        """Checks for package.json, package-lock.json, yarn.lock, pnpm-lock.yaml or JS/TS files."""
        root = os.path.abspath(root_dir)
        manifests = ["package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "tsconfig.json"]
        for m in manifests:
            if os.path.exists(os.path.join(root, m)):
                return True

        for r, dirs, files in os.walk(root, followlinks=False):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["node_modules", "dist", "build", "coverage", ".rover-slim"]]
            if any(f.endswith((".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx")) for f in files):
                return True
        return False

    def segregate_dependencies(
        self,
        root_dir: str,
        always_prod: Optional[List[str]] = None,
        always_dev: Optional[List[str]] = None
    ) -> Tuple[List[RequirementEntry], List[RequirementEntry], List[PrunedPackage]]:
        """Parses package.json to split production runtime dependencies from devDependencies."""
        root = os.path.abspath(root_dir)
        pkg_json_path = os.path.join(root, "package.json")
        
        prod_entries: List[RequirementEntry] = []
        dev_entries: List[RequirementEntry] = []
        pruned_packages: List[PrunedPackage] = []

        always_prod_set = set(p.lower() for p in (always_prod or []))
        always_dev_set = set(d.lower() for d in (always_dev or []))

        if not os.path.exists(pkg_json_path):
            return prod_entries, dev_entries, pruned_packages

        try:
            with open(pkg_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return prod_entries, dev_entries, pruned_packages

        deps = data.get("dependencies", {})
        dev_deps = data.get("devDependencies", {})

        # Process prod deps
        for name, ver in deps.items():
            name_lower = name.lower()
            is_dev_override = name_lower in always_dev_set
            
            # Check if matching dev tooling patterns
            matches_dev_tool = any(re.search(pat, name_lower) for pat in self.DEV_TOOLING_PATTERNS)

            if is_dev_override or (matches_dev_tool and name_lower not in always_prod_set):
                dev_entries.append(RequirementEntry(raw_line=f'"{name}": "{ver}"', name=name, specifier=str(ver)))
                pruned_packages.append(PrunedPackage(
                    package=f"{name}@{ver}",
                    action="MOVED_TO_DEV",
                    reason="Classified as dev/build tooling or TypeScript compiler",
                    estimated_size_mb=18.5
                ))
            else:
                prod_entries.append(RequirementEntry(raw_line=f'"{name}": "{ver}"', name=name, specifier=str(ver)))

        # Process declared devDeps
        for name, ver in dev_deps.items():
            name_lower = name.lower()
            if name_lower in always_prod_set:
                prod_entries.append(RequirementEntry(raw_line=f'"{name}": "{ver}"', name=name, specifier=str(ver)))
            else:
                dev_entries.append(RequirementEntry(raw_line=f'"{name}": "{ver}"', name=name, specifier=str(ver)))
                pruned_packages.append(PrunedPackage(
                    package=f"{name}@{ver}",
                    action="MOVED_TO_DEV",
                    reason="Declared in devDependencies and quarantined from runtime stage",
                    estimated_size_mb=14.0
                ))

        return prod_entries, dev_entries, pruned_packages

    def synthesize_dockerfile(
        self,
        config: RoverSlimConfig,
        root_dir: str,
        existing_dockerfile_path: Optional[str] = None
    ) -> str:
        """Synthesizes a 2-stage multi-stage Node.js Dockerfile with non-root appuser."""
        base_node = "node:20-slim"
        return f"""# Generated by Rover-Slim Polyglot Synthesizer for Node.js
# Stage 1: Build & Prune Dependencies
FROM {base_node} AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --include=dev
COPY . .
RUN if [ -f "tsconfig.json" ]; then npm run build --if-present; fi
RUN npm prune --omit=dev

# Stage 2: Production Minimal Runtime
FROM {base_node} AS runtime
WORKDIR /app
RUN groupadd -r appuser -g 10001 && useradd -r -g appuser -u 10001 appuser
ENV NODE_ENV=production
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/dist ./dist 2>/dev/null || COPY --from=builder /app ./
USER 10001
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 CMD node -e 'require("http").get("http://localhost:3000/health", (res) => process.exit(res.statusCode === 200 ? 0 : 1))' || exit 1
CMD ["npm", "start"]
"""

    def discover_health_probes(self, root_dir: str) -> List[ProbeConfig]:
        """Auto-discovers Express, Fastify, NestJS, or Next.js health routes."""
        probes: List[ProbeConfig] = []
        root = os.path.abspath(root_dir)
        
        common_paths = ["/health", "/api/health", "/healthz", "/status", "/live", "/"]
        detected_path = "/health"
        detected_port = 3000

        # Scan for port definitions or route registrations
        for r, dirs, files in os.walk(root, followlinks=False):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["node_modules", "dist", "coverage", ".rover-slim"]]
            for f in files:
                if f.endswith((".js", ".ts")):
                    full_p = os.path.join(r, f)
                    try:
                        with open(full_p, "r", encoding="utf-8", errors="ignore") as file_handle:
                            code = file_handle.read()
                            # Search for route like app.get('/health')
                            for cand in common_paths:
                                if f"'{cand}'" in code or f'"{cand}"' in code:
                                    detected_path = cand
                                    break
                            # Search for port like listen(3000) or listen(8080)
                            port_match = re.search(r"listen\(\s*(?:process\.env\.PORT\s*\|\|\s*)?(\d{4,5})", code)
                            if port_match:
                                detected_port = int(port_match.group(1))
                    except Exception:
                        pass

        probes.append(ProbeConfig(
            name="Node.js HTTP Health Probe",
            type="http",
            path=detected_path,
            port=detected_port,
            expected_status=200,
            timeout_seconds=5
        ))
        return probes
