import ast
import os
import re
from typing import Set, Dict, List, Optional, Any
from rover_slim.models import ProbeConfig
from rover_slim.parsers.ast_parser import STDLIB_MODULES, IMPORT_TO_PACKAGE_MAP

class FrameworkDetector:
    """Detects web framework, entrypoint file, and API routes via AST inspection."""

    FRAMEWORK_PATTERNS = {
        "fastapi": ["FastAPI", "APIRouter"],
        "flask": ["Flask", "Blueprint"],
        "django": ["django.core.wsgi", "get_wsgi_application"],
        "streamlit": ["st.", "streamlit"],
        "tornado": ["tornado.web.Application"],
        "sanic": ["Sanic"]
    }

    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)

    def analyze_repository(self) -> Dict[str, Any]:
        detected_frameworks = set()
        discovered_routes = []
        entrypoint_candidates = []
        default_port = 8080

        for root, dirs, files in os.walk(self.root_dir, followlinks=False):
            dirs[:] = [
                d for d in dirs
                if not d.startswith(".") and d not in [
                    "tests", "test", "venv", ".venv", "env", ".env", "docs",
                    "node_modules", "build", "dist", "scratch", ".rover-slim", ".pytest_cache"
                ]
            ]
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.root_dir)
                    
                    if file in ["server.py", "app.py", "main.py", "wsgi.py", "asgi.py", "api.py"]:
                        entrypoint_candidates.append(rel_path)

                    routes, frameworks = self._analyze_file_ast(full_path)
                    discovered_routes.extend(routes)
                    detected_frameworks.update(frameworks)

        if "streamlit" in detected_frameworks:
            default_port = 8501
        elif "django" in detected_frameworks:
            default_port = 8000
        elif "flask" in detected_frameworks:
            default_port = 5000
        else:
            default_port = 8080

        # Build auto-discovered probes
        probes: List[ProbeConfig] = []
        health_route = next(
            (r for r in discovered_routes if any(h in r for h in ["health", "status", "ping", "live"])),
            None
        )

        if health_route:
            probes.append(ProbeConfig(
                name=f"Auto-Discovered Health ({health_route})",
                type="http",
                path=health_route,
                port=default_port,
                expected_status=200,
                timeout_seconds=5
            ))
        elif discovered_routes:
            probes.append(ProbeConfig(
                name=f"Auto-Discovered Route ({discovered_routes[0]})",
                type="http",
                path=discovered_routes[0],
                port=default_port,
                expected_status=200,
                timeout_seconds=5
            ))
        else:
            probes.append(ProbeConfig(
                name="Standard HTTP Root Probe",
                type="http",
                path="/",
                port=default_port,
                expected_status=200,
                timeout_seconds=5
            ))

        return {
            "detected_frameworks": list(detected_frameworks),
            "discovered_routes": list(set(discovered_routes)),
            "entrypoint_candidates": entrypoint_candidates,
            "recommended_port": default_port,
            "recommended_probes": probes
        }

    def _analyze_file_ast(self, filepath: str) -> (List[str], Set[str]):
        routes = []
        frameworks = set()
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content, filename=filepath)

            # Framework string match
            for fw, patterns in self.FRAMEWORK_PATTERNS.items():
                if any(p in content for p in patterns):
                    frameworks.add(fw)

            # Route decorator extraction
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for decorator in node.decorator_list:
                        route = self._extract_route_from_decorator(decorator)
                        if route:
                            routes.append(route)
        except Exception:
            pass
        return routes, frameworks

    def _extract_route_from_decorator(self, node: ast.AST) -> Optional[str]:
        if isinstance(node, ast.Call):
            func = node.func
            # Match @app.get("/path"), @router.post("/path"), @app.route("/path")
            if isinstance(func, ast.Attribute) and func.attr in ["get", "post", "put", "delete", "route", "patch"]:
                if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                    path = node.args[0].value
                    if path.startswith("/"):
                        return path
        return None
