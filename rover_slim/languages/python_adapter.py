import os
from typing import List, Tuple, Optional, Any
from rover_slim.languages.base import BaseLanguageAdapter
from rover_slim.models import PrunedPackage, ProbeConfig, RoverSlimConfig
from rover_slim.parsers.ast_parser import ASTDependencyParser
from rover_slim.parsers.req_parser import RequirementsParser, RequirementEntry
from rover_slim.parsers.ast_deep_analyzer import FrameworkDetector
from rover_slim.synthesizers.multistage import MultiStageSynthesizer

class PythonLanguageAdapter(BaseLanguageAdapter):
    """Concrete language adapter for Python applications."""

    @property
    def name(self) -> str:
        return "python"

    @property
    def display_name(self) -> str:
        return "Python 3.x (AST-Driven)"

    def detect(self, root_dir: str) -> bool:
        """Checks for Python signatures (pyproject.toml, requirements.txt, setup.py, or .py files)."""
        root = os.path.abspath(root_dir)
        indicators = ["pyproject.toml", "requirements.txt", "setup.py", "Pipfile", "poetry.lock"]
        for ind in indicators:
            if os.path.exists(os.path.join(root, ind)):
                return True

        # Check for any .py file in top levels
        for r, dirs, files in os.walk(root, followlinks=False):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["venv", ".venv", "tests", "test", "node_modules", ".rover-slim"]]
            if any(f.endswith(".py") for f in files):
                return True
        return False

    def segregate_dependencies(
        self,
        root_dir: str,
        always_prod: Optional[List[str]] = None,
        always_dev: Optional[List[str]] = None
    ) -> Tuple[List[RequirementEntry], List[RequirementEntry], List[PrunedPackage]]:
        parser = RequirementsParser(root_dir)
        return parser.segregate_dependencies(
            always_prod=always_prod,
            always_dev=always_dev
        )

    def synthesize_dockerfile(
        self,
        config: RoverSlimConfig,
        root_dir: str,
        existing_dockerfile_path: Optional[str] = None
    ) -> str:
        synthesizer = MultiStageSynthesizer(config)
        return synthesizer.synthesize(existing_dockerfile_path=existing_dockerfile_path)

    def discover_health_probes(self, root_dir: str) -> List[ProbeConfig]:
        detector = FrameworkDetector(root_dir)
        analysis = detector.analyze_repository()
        return analysis.get("recommended_probes", [])
