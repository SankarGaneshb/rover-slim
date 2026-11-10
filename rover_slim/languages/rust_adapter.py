import os
from typing import Any, Dict, List, Optional, Tuple

import tomllib

from pydantic import BaseModel, Field

from rover_slim.languages.base import BaseLanguageAdapter
from rover_slim.models import PrunedPackage, ProbeConfig, RoverSlimConfig
from rover_slim.parsers.req_parser import RequirementEntry


class CargoDependency(BaseModel):
    """Normalized representation of a single Cargo dependency entry."""

    name: str
    version: str = ""
    scope: str = "runtime"  # "runtime" | "dev" | "build"
    features: List[str] = Field(default_factory=list)
    optional: bool = False
    path: Optional[str] = None
    git: Optional[str] = None

    def to_requirement_entry(self) -> RequirementEntry:
        raw_line = f'{self.name} = "{self.version}"' if self.version else self.name
        return RequirementEntry(raw_line=raw_line, name=self.name, specifier=self.version)

    def to_pruned_package(self, reason: str, estimated_size_mb: float) -> PrunedPackage:
        package = f"{self.name}@{self.version}" if self.version else self.name
        return PrunedPackage(
            package=package,
            action="MOVED_TO_DEV",
            reason=reason,
            estimated_size_mb=estimated_size_mb,
        )


class CargoManifest(BaseModel):
    """Parsed contents of a Cargo.toml relevant to dependency pruning."""

    manifest_file: str = "Cargo.toml"
    package_name: Optional[str] = None
    version: Optional[str] = None
    edition: Optional[str] = None
    dependencies: List[CargoDependency] = Field(default_factory=list)
    dev_dependencies: List[CargoDependency] = Field(default_factory=list)
    build_dependencies: List[CargoDependency] = Field(default_factory=list)

    @property
    def ecosystem(self) -> str:
        return "rust"

    def runtime_dependencies(self) -> List[CargoDependency]:
        return list(self.dependencies)

    def development_dependencies(self) -> List[CargoDependency]:
        return list(self.dev_dependencies) + list(self.build_dependencies)

    def to_dict(self) -> Dict[str, Any]:
        scoped = (
            [(dep, "runtime") for dep in self.dependencies]
            + [(dep, "dev") for dep in self.dev_dependencies]
            + [(dep, "build") for dep in self.build_dependencies]
        )
        return {
            "ecosystem": self.ecosystem,
            "manifest_file": self.manifest_file,
            "edition": self.edition,
            "package_name": self.package_name,
            "dependencies": [
                {
                    "name": dep.name,
                    "version": dep.version,
                    "scope": scope,
                    "features": list(dep.features),
                }
                for dep, scope in scoped
            ],
        }


class RustLanguageAdapter(BaseLanguageAdapter):
    """Language adapter for Rust projects using Cargo."""

    DEV_SIZE_ESTIMATE_MB: float = 12.0
    BUILD_SIZE_ESTIMATE_MB: float = 8.0

    @property
    def name(self) -> str:
        return "rust"

    @property
    def display_name(self) -> str:
        return "Rust"

    def detect(self, root_dir: str) -> bool:
        """Looks for Cargo.toml"""
        root = os.path.abspath(root_dir)
        manifests = ["Cargo.toml", "Cargo.lock", "build.rs"]
        for m in manifests:
            if os.path.exists(os.path.join(root, m)):
                return True

        return False

    def segregate_dependencies(
        self,
        root_dir: str,
        always_prod: Optional[List[str]] = None,
        always_dev: Optional[List[str]] = None
    ) -> Tuple[List[RequirementEntry], List[RequirementEntry], List[PrunedPackage]]:
        manifest_path = self._find_manifest(root_dir)
        if not manifest_path:
            return [], [], []

        manifest = self._load_manifest(manifest_path)
        if manifest is None:
            return [], [], []

        dependencies = (
            list(manifest.dependencies)
            + list(manifest.dev_dependencies)
            + list(manifest.build_dependencies)
        )
        return self._apply_overrides(dependencies, always_prod, always_dev)

    def _find_manifest(self, root_dir: str) -> Optional[str]:
        """Locate the Cargo.toml manifest for a project root."""
        raise NotImplementedError

    def _load_manifest(self, manifest_path: str) -> Optional[CargoManifest]:
        """Parse a Cargo.toml file into a CargoManifest."""
        raise NotImplementedError

    def _parse_dependency_spec(self, name: str, spec: Any, scope: str) -> CargoDependency:
        """Normalize a single dependency entry (version string or inline table)."""
        raise NotImplementedError

    def _parse_dependency_table(self, table: Dict[str, Any], scope: str) -> List[CargoDependency]:
        """Parse one dependency table (e.g. [dependencies]) into CargoDependency entries."""
        raise NotImplementedError

    def _parse_target_dependencies(self, data: Dict[str, Any]) -> List[CargoDependency]:
        """Parse all [target.*.dependencies] tables."""
        raise NotImplementedError

    def _parse_workspace_dependencies(self, data: Dict[str, Any]) -> List[CargoDependency]:
        """Parse [workspace.dependencies] for inherited dependencies."""
        raise NotImplementedError

    def _apply_overrides(
        self,
        dependencies: List[CargoDependency],
        always_prod: Optional[List[str]],
        always_dev: Optional[List[str]],
    ) -> Tuple[List[RequirementEntry], List[RequirementEntry], List[PrunedPackage]]:
        """Apply always_prod/always_dev overrides and build the final result tuple."""
        raise NotImplementedError

    def synthesize_dockerfile(
        self,
        config: RoverSlimConfig,
        root_dir: str,
        existing_dockerfile_path: Optional[str] = None,
    ) -> str:
        root = os.path.abspath(root_dir)
        binary_name = "app"

        manifest_path = os.path.join(root, "Cargo.toml")
        try:
            with open(manifest_path, "rb") as manifest_handle:
                data = tomllib.load(manifest_handle)
            binaries = data.get("bin") or []
            if isinstance(binaries, list) and binaries and isinstance(binaries[0], dict):
                binary_name = binaries[0].get("name") or binary_name
            else:
                package = data.get("package") or {}
                binary_name = package.get("name") or binary_name
        except Exception:
            pass

        lock_copy = "COPY Cargo.lock ./\n" if os.path.exists(os.path.join(root, "Cargo.lock")) else ""

        return f"""# Generated by Rover-Slim Polyglot Synthesizer for Rust
# Stage 1: Build
FROM rust:1.79-slim AS builder
WORKDIR /app
COPY Cargo.toml ./
{lock_copy}COPY . .
RUN cargo build --release

# Stage 2: Minimal Runtime
FROM debian:bookworm-slim AS runtime
WORKDIR /app
RUN apt-get update \\
    && apt-get install -y --no-install-recommends ca-certificates \\
    && rm -rf /var/lib/apt/lists/* \\
    && groupadd -r appuser -g 10001 \\
    && useradd -r -g appuser -u 10001 appuser
COPY --from=builder /app/target/release/{binary_name} /usr/local/bin/app
USER 10001
ENV RUST_BACKTRACE=1
CMD ["app"]
"""

    def discover_health_probes(self, root_dir: str) -> List[ProbeConfig]:
        pass
