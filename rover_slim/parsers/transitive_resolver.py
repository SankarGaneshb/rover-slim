import importlib.metadata
import re
from typing import Set, Dict, List, Optional

# Static fallback dependency trees for popular Python libraries
KNOWN_TRANSITIVE_MAP: Dict[str, Set[str]] = {
    "fastapi": {"starlette", "pydantic", "pydantic-core", "typing-extensions", "annotated-types"},
    "uvicorn": {"h11", "websockets", "httptools", "click", "uvloop", "colorama", "watchfiles"},
    "pandas": {"numpy", "python-dateutil", "pytz", "tzdata"},
    "scipy": {"numpy"},
    "scikit-learn": {"numpy", "scipy", "joblib", "threadpoolctl"},
    "sqlalchemy": {"typing-extensions", "greenlet"},
    "alembic": {"sqlalchemy", "mako", "typing-extensions"},
    "requests": {"urllib3", "certifi", "idna", "charset-normalizer"},
    "httpx": {"httpcore", "sniffio", "certifi", "idna", "anyio", "h11"},
    "aiohttp": {"multidict", "yarl", "frozenlist", "aiosignal", "attrs", "async-timeout"},
    "celery": {"kombu", "billiard", "vine", "click-didyoumean", "click-repl", "amqp"},
    "redis": {"async-timeout"},
    "pydantic": {"annotated-types", "pydantic-core", "typing-extensions"},
    "pydantic-settings": {"pydantic", "python-dotenv"},
    "torch": {"typing-extensions", "filelock", "networkx", "jinja2", "fsspec", "sympy"},
    "transformers": {"huggingface-hub", "tokenizers", "safetensors", "regex", "requests", "tqdm", "numpy", "packaging"},
    "matplotlib": {"numpy", "pillow", "cycler", "fonttools", "kiwisolver", "packaging", "pyparsing", "python-dateutil"},
    "seaborn": {"matplotlib", "numpy", "pandas"}
}

class TransitiveDependencyResolver:
    """Resolves direct and transitive sub-dependencies to prevent breaking production runtime."""

    def __init__(self):
        pass

    def get_transitive_deps(self, package_name: str) -> Set[str]:
        """Discovers sub-dependencies via local environment metadata or static knowledge base."""
        normalized = package_name.strip().lower().replace("_", "-")
        deps: Set[str] = set()

        # 1. Check local installed package metadata
        try:
            reqs = importlib.metadata.requires(normalized)
            if reqs:
                for r in reqs:
                    # Filter out optional extras like `extra == 'test'`
                    if "extra ==" in r:
                        continue
                    match = re.match(r"^([a-zA-Z0-9_\-\.]+)", r)
                    if match:
                        sub_name = match.group(1).lower().replace("_", "-")
                        deps.add(sub_name)
        except Exception:
            pass

        # 2. Augment with curated knowledge base
        if normalized in KNOWN_TRANSITIVE_MAP:
            deps.update(KNOWN_TRANSITIVE_MAP[normalized])

        return deps

    def expand_production_packages(self, root_production_packages: Set[str], max_iterations: int = 250) -> Set[str]:
        """Recursively expands a set of production packages with all transitive sub-dependencies."""
        expanded: Set[str] = set(root_production_packages)
        queue = list(root_production_packages)
        visited = set()
        iterations = 0

        while queue and iterations < max_iterations:
            iterations += 1
            current = queue.pop(0)
            norm = current.lower().replace("_", "-")
            if norm in visited:
                continue
            visited.add(norm)

            sub_deps = self.get_transitive_deps(norm)
            for sub in sub_deps:
                if sub not in expanded:
                    expanded.add(sub)
                    queue.append(sub)

        return expanded
