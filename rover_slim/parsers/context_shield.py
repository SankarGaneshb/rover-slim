from typing import List, Set, Tuple, Dict, Any
import os

STANDARD_IGNORE_PATTERNS = [
    "# Version control & metadata",
    ".git",
    ".gitignore",
    ".github",
    ".gitlab-ci.yml",
    ".vscode",
    ".idea",
    "",
    "# Python byte-code & virtualenvs",
    "__pycache__/",
    "*.py[cod]",
    "*$py.class",
    ".venv",
    "venv/",
    "env/",
    "ENV/",
    "*.egg-info/",
    ".eggs/",
    "dist/",
    "build/",
    "",
    "# Testing, coverage & linting",
    "tests/",
    "test/",
    ".pytest_cache/",
    ".coverage",
    "htmlcov/",
    ".tox/",
    ".nox/",
    ".mypy_cache/",
    ".ruff_cache/",
    "",
    "# Local secrets, logs & scratch",
    ".env",
    ".env.*",
    "*.log",
    "scratch/",
    ".rover-slim/",
    "",
    "# Node / frontend artifacts",
    "node_modules/",
    "npm-debug.log*",
    "yarn-debug.log*",
    "yarn-error.log*",
    "",
    "# Documentation & raw data",
    "docs/",
    "*.md",
    "!README.md",
    "*.ipynb",
    ".ipynb_checkpoints"
]

class ContextShield:
    """Detects leaked directories in Docker build context and generates hardened .dockerignore."""

    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)

    def get_directory_size_mb(self, path: str) -> float:
        total_size = 0
        if not os.path.exists(path):
            return 0.0
        if os.path.isfile(path):
            return os.path.getsize(path) / (1024 * 1024)
        for root, _, files in os.walk(path):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    total_size += os.path.getsize(fp)
                except (OSError, FileNotFoundError):
                    pass
        return total_size / (1024 * 1024)

    def audit_context_leakage(self) -> Dict[str, Any]:
        """Calculates total build context size and potential savings from ignoring heavy dirs."""
        heavy_dirs = [".git", "node_modules", "venv", ".venv", "tests", ".pytest_cache", ".coverage", "docs"]
        leakage: Dict[str, float] = {}
        total_context_size = self.get_directory_size_mb(self.root_dir)

        for item in heavy_dirs:
            p = os.path.join(self.root_dir, item)
            if os.path.exists(p):
                sz = self.get_directory_size_mb(p)
                if sz >= 0.0:
                    leakage[item] = round(sz, 4)

        has_ignore = os.path.exists(os.path.join(self.root_dir, ".dockerignore"))
        
        return {
            "has_dockerignore": has_ignore,
            "total_raw_context_mb": round(total_context_size, 2),
            "leaked_directories": leakage,
            "potential_leakage_savings_mb": round(sum(leakage.values()), 2)
        }

    def generate_dockerignore(self, custom_ignores: List[str] = None) -> str:
        """Synthesizes a hardened .dockerignore file content."""
        lines = list(STANDARD_IGNORE_PATTERNS)
        if custom_ignores:
            lines.append("")
            lines.append("# Custom User Ignores")
            lines.extend(custom_ignores)
        return "\n".join(lines) + "\n"

    def write_dockerignore(self, output_path: str = None, force: bool = False) -> Tuple[str, bool]:
        """Writes .dockerignore to project root."""
        target = output_path or os.path.join(self.root_dir, ".dockerignore")
        existed = os.path.exists(target)
        if existed and not force:
            return target, False
        content = self.generate_dockerignore()
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
        return target, True
