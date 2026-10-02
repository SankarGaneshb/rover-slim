import ast
import os
import sys
from typing import Set, List, Optional, Dict

# Standard library module names in Python 3.10+
STDLIB_MODULES = sys.stdlib_module_names if hasattr(sys, "stdlib_module_names") else {
    "abc", "argparse", "array", "ast", "asyncio", "base64", "builtins", "collections",
    "concurrent", "contextlib", "copy", "csv", "ctypes", "dataclasses", "datetime",
    "decimal", "difflib", "dis", "doctest", "email", "enum", "errno", "faulthandler",
    "fcntl", "fnmatch", "fractions", "functools", "gc", "getopt", "getpass", "gettext",
    "glob", "gzip", "hashlib", "heapq", "hmac", "html", "http", "idlelib", "imaplib",
    "imghdr", "importlib", "inspect", "io", "ipaddress", "itertools", "json", "keyword",
    "linecache", "locale", "logging", "lzma", "math", "mimetypes", "mmap", "modulefinder",
    "multiprocessing", "netrc", "numbers", "operator", "os", "pathlib", "pdb", "pickle",
    "pkgutil", "platform", "plistlib", "poplib", "posixpath", "pprint", "profile",
    "pstats", "pty", "pwd", "queue", "quopri", "random", "re", "readline", "resource",
    "rlcompleter", "runpy", "sched", "secrets", "select", "selectors", "shelve", "shlex",
    "shutil", "signal", "site", "smtpd", "smtplib", "sndhdr", "socket", "socketserver",
    "sqlite3", "ssl", "stat", "statistics", "string", "stringprep", "struct", "subprocess",
    "sunau", "symbol", "symtable", "sys", "sysconfig", "syslog", "tabnanny", "tarfile",
    "telnetlib", "tempfile", "termios", "test", "textwrap", "threading", "time", "timeit",
    "tkinter", "token", "tokenize", "trace", "traceback", "tracemalloc", "tty", "types",
    "typing", "unicodedata", "unittest", "urllib", "uu", "uuid", "venv", "warnings",
    "wave", "weakref", "webbrowser", "wsgiref", "xml", "xmlrpc", "zipapp", "zipfile",
    "zipimport", "zlib", "zoneinfo"
}

# Mapping of common top-level import names to PyPI package names
IMPORT_TO_PACKAGE_MAP: Dict[str, str] = {
    "yaml": "pyyaml",
    "PIL": "pillow",
    "cv2": "opencv-python",
    "sklearn": "scikit-learn",
    "dotenv": "python-dotenv",
    "jose": "python-jose",
    "bs4": "beautifulsoup4",
    "psycopg2": "psycopg2-binary",
    "dateutil": "python-dateutil",
    "jwt": "pyjwt",
    "pydantic_settings": "pydantic-settings",
    "fastapi": "fastapi",
    "starlette": "starlette",
    "uvicorn": "uvicorn",
    "sqlalchemy": "sqlalchemy",
    "alembic": "alembic",
    "requests": "requests",
    "httpx": "httpx",
    "aiohttp": "aiohttp",
    "rich": "rich",
    "typer": "typer",
    "click": "click",
    "jinja2": "jinja2",
    "docker": "docker",
    "mcp": "mcp",
    "pandas": "pandas",
    "numpy": "numpy",
    "scipy": "scipy",
    "torch": "torch",
    "transformers": "transformers",
    "redis": "redis",
    "celery": "celery"
}

# Packages typically reserved for development, testing, linting, or exploratory visualization
KNOWN_DEV_PACKAGES: Set[str] = {
    "pytest", "pytest_cov", "pytest-cov", "pytest_asyncio", "pytest-asyncio",
    "pytest_mock", "pytest-mock", "unittest", "mock", "black", "flake8", "mypy",
    "ruff", "isort", "pylint", "coverage", "tox", "nox",
    "streamlit", "matplotlib", "seaborn", "altair", "pydeck", "plotly", "bokeh",
    "ipython", "jupyter", "jupyterlab", "notebook", "ipywidgets", "tensorboard",
    "sphinx", "mkdocs"
}

# Rough size estimates (MB) for common heavy dev/viz packages for ROI reporting
PACKAGE_SIZE_ESTIMATES: Dict[str, float] = {
    "streamlit": 95.0,
    "matplotlib": 75.0,
    "seaborn": 35.0,
    "plotly": 65.0,
    "altair": 28.0,
    "pydeck": 45.0,
    "ipython": 40.0,
    "jupyter": 110.0,
    "jupyterlab": 130.0,
    "notebook": 85.0,
    "pytest": 18.0,
    "black": 22.0,
    "mypy": 30.0,
    "ruff": 25.0,
    "flake8": 12.0,
    "coverage": 8.0,
    "torch": 750.0,
    "transformers": 120.0,
    "scipy": 95.0,
    "pandas": 80.0,
    "numpy": 45.0
}


class ASTDependencyParser:
    """Extracts genuine Python imports across the production codebase via AST."""

    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)

    def extract_imports_from_file(self, filepath: str) -> Set[str]:
        """Parses a single python file with encoding fallback and returns top-level imported module names."""
        imports = set()
        content = None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(filepath, "r", encoding="latin-1") as f:
                    content = f.read()
            except Exception:
                return imports
        except Exception:
            return imports

        if not content:
            return imports

        try:
            tree = ast.parse(content, filename=filepath)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        top = alias.name.split(".")[0]
                        if top not in STDLIB_MODULES:
                            imports.add(top)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    top = node.module.split(".")[0]
                    if top not in STDLIB_MODULES:
                        imports.add(top)
                # Catch dynamic importlib.import_module("pkg") or __import__("pkg")
                elif isinstance(node, ast.Call):
                    func_name = ""
                    if isinstance(node.func, ast.Name):
                        func_name = node.func.id
                    elif isinstance(node.func, ast.Attribute):
                        func_name = node.func.attr
                    
                    if func_name in ["import_module", "__import__"]:
                        if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                            top = node.args[0].value.split(".")[0]
                            if top not in STDLIB_MODULES:
                                imports.add(top)
        except Exception:
            pass

        return imports

    def scan_production_imports(self, exclude_dirs: Optional[List[str]] = None) -> Set[str]:
        """Walks the repository and aggregates all top-level imports in production code."""
        excludes = set(exclude_dirs or [
            "tests", "test", "testing", "venv", ".venv", "env", ".env",
            "docs", "scripts", "build", "dist", ".git", ".github",
            "node_modules", "examples", "benchmarks", "__pycache__",
            ".rover-slim", ".pytest_cache", "scratch", "rover_slim.egg-info"
        ])
        production_imports = set()
        for root, dirs, files in os.walk(self.root_dir, followlinks=False):
            dirs[:] = [
                d for d in dirs
                if d not in excludes and not d.startswith(".") and not d.startswith("test")
            ]
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    production_imports.update(self.extract_imports_from_file(full_path))
        return production_imports

    def map_import_to_package(self, import_name: str) -> str:
        """Translates Python import name to normalized PyPI package name."""
        clean = import_name.strip().lower().replace("_", "-")
        return IMPORT_TO_PACKAGE_MAP.get(import_name, clean)
