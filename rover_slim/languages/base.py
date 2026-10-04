from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict, Any, Set
from rover_slim.models import PrunedPackage, ProbeConfig, RoverSlimConfig

class BaseLanguageAdapter(ABC):
    """
    Abstract interface for polyglot language adapters.
    Encapsulates language-specific dependency analysis, AST parsing,
    Dockerfile synthesis, and health probe discovery.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the language ecosystem (e.g., 'python', 'nodejs')."""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-friendly display name (e.g., 'Python 3.x', 'Node.js / TypeScript')."""
        pass

    @abstractmethod
    def detect(self, root_dir: str) -> bool:
        """Detects whether this project matches this language ecosystem."""
        pass

    @abstractmethod
    def segregate_dependencies(
        self,
        root_dir: str,
        always_prod: Optional[List[str]] = None,
        always_dev: Optional[List[str]] = None
    ) -> Tuple[List[Any], List[Any], List[PrunedPackage]]:
        """
        Analyzes source code AST and package manifests to segregate
        (production_dependencies, development_dependencies, pruned_packages).
        """
        pass

    @abstractmethod
    def synthesize_dockerfile(
        self,
        config: RoverSlimConfig,
        root_dir: str,
        existing_dockerfile_path: Optional[str] = None
    ) -> str:
        """Synthesizes a minimal multi-stage Dockerfile tailored for this runtime."""
        pass

    @abstractmethod
    def discover_health_probes(self, root_dir: str) -> List[ProbeConfig]:
        """Auto-discovers application routes and suggested health probes."""
        pass
