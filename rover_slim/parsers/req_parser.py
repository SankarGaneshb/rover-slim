import os
import re
from typing import List, Dict, Set, Tuple, Optional
from rover_slim.models import PrunedPackage
from rover_slim.parsers.ast_parser import (
    ASTDependencyParser,
    KNOWN_DEV_PACKAGES,
    PACKAGE_SIZE_ESTIMATES,
    IMPORT_TO_PACKAGE_MAP
)
from rover_slim.parsers.transitive_resolver import TransitiveDependencyResolver

class RequirementEntry:
    def __init__(self, raw_line: str, name: str, specifier: str = ""):
        self.raw_line = raw_line.strip()
        self.name = name.strip()
        self.normalized_name = name.strip().lower().replace("_", "-")
        self.specifier = specifier.strip()

    def __repr__(self):
        return f"<Requirement {self.normalized_name} {self.specifier}>"

class RequirementsParser:
    """Parses requirements files and segregates production vs development dependencies."""

    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)
        self.ast_parser = ASTDependencyParser(self.root_dir)
        self.transitive_resolver = TransitiveDependencyResolver()

    def parse_requirement_line(self, line: str) -> Optional[RequirementEntry]:
        """Parses a single requirements line with robust support for comments, markers, and URLs."""
        clean_line = line.strip()
        if not clean_line or clean_line.startswith("#") or clean_line.startswith("-r "):
            return None

        # Handle options like -i or --extra-index-url
        if clean_line.startswith("--") or clean_line.startswith("-f "):
            return None

        # Extract editable package name if present: -e ...#egg=pkgname
        if clean_line.startswith("-e ") or clean_line.startswith("--editable "):
            egg_match = re.search(r"#egg=([a-zA-Z0-9_\-\.]+)", clean_line)
            if egg_match:
                pkg_name = egg_match.group(1)
                return RequirementEntry(clean_line, pkg_name, "")
            # Return raw if local path
            path_name = os.path.basename(clean_line.split()[-1].rstrip("/"))
            return RequirementEntry(clean_line, path_name or "local-pkg", "")

        # Strip inline comment
        content_part = clean_line.split("#")[0].strip()
        if not content_part:
            return None

        # Strip environment markers (e.g. ; python_version < '3.8')
        base_req = content_part.split(";")[0].strip()

        # Handle git/url #egg=pkgname
        if "#egg=" in base_req:
            egg_match = re.search(r"#egg=([a-zA-Z0-9_\-\.]+)", base_req)
            if egg_match:
                return RequirementEntry(clean_line, egg_match.group(1), "")

        # Match standard pip format: package>=1.0.0, package==2.0, package[extra]
        match = re.match(r"^([a-zA-Z0-9_\-\.]+)(?:\[[^\]]+\])?(.*)$", base_req)
        if match:
            pkg_name = match.group(1)
            specifier = match.group(2)
            return RequirementEntry(clean_line, pkg_name, specifier)

        return None

    def find_requirements_file(self) -> Optional[str]:
        """Discovers primary requirements file in project root."""
        candidates = [
            "requirements.txt",
            "requirements/base.txt",
            "requirements/prod.txt",
            "requirements/common.txt"
        ]
        for c in candidates:
            p = os.path.join(self.root_dir, c)
            if os.path.exists(p):
                return p
        return None

    def load_requirements(self, req_path: Optional[str] = None) -> List[RequirementEntry]:
        """Loads and parses requirement entries from file with IO error handling."""
        path = req_path or self.find_requirements_file()
        if not path or not os.path.exists(path):
            return []
        entries = []
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    parsed = self.parse_requirement_line(line)
                    if parsed:
                        entries.append(parsed)
        except UnicodeDecodeError:
            # Fallback for latin-1 or cp1252 encoded requirements files
            try:
                with open(path, "r", encoding="latin-1") as f:
                    for line in f:
                        parsed = self.parse_requirement_line(line)
                        if parsed:
                            entries.append(parsed)
            except Exception:
                pass
        except Exception:
            pass
        return entries

    def segregate_dependencies(
        self,
        req_entries: Optional[List[RequirementEntry]] = None,
        always_prod: Optional[List[str]] = None,
        always_dev: Optional[List[str]] = None
    ) -> Tuple[List[RequirementEntry], List[RequirementEntry], List[PrunedPackage]]:
        """
        Segregates requirements into (prod_entries, dev_entries, pruned_packages_info).
        Matches AST production code imports and expands transitive dependencies.
        """
        entries = req_entries if req_entries is not None else self.load_requirements()
        always_prod_set = {p.lower().replace("_", "-") for p in (always_prod or [])}
        always_dev_set = {p.lower().replace("_", "-") for p in (always_dev or [])}

        scanned_imports = self.ast_parser.scan_production_imports()
        scanned_packages = {
            self.ast_parser.map_import_to_package(imp)
            for imp in scanned_imports
        }
        scanned_packages.update({imp.lower().replace("_", "-") for imp in scanned_imports})

        # Expand production packages with transitive dependencies
        expanded_prod_packages = self.transitive_resolver.expand_production_packages(scanned_packages)

        prod_entries: List[RequirementEntry] = []
        dev_entries: List[RequirementEntry] = []
        pruned_packages: List[PrunedPackage] = []

        for entry in entries:
            norm = entry.normalized_name

            # Explicit overrides
            if norm in always_prod_set:
                prod_entries.append(entry)
                continue
            if norm in always_dev_set:
                dev_entries.append(entry)
                est_size = PACKAGE_SIZE_ESTIMATES.get(norm, 15.0)
                pruned_packages.append(PrunedPackage(
                    package=entry.raw_line,
                    action="MOVED_TO_DEV",
                    reason="Explicitly configured in always_development",
                    estimated_size_mb=est_size
                ))
                continue

            # Check if recognized as known dev/viz/test package
            if norm in KNOWN_DEV_PACKAGES or any(dev in norm for dev in ["pytest", "mock", "flake", "pylint", "black", "mypy", "ruff"]):
                dev_entries.append(entry)
                est_size = PACKAGE_SIZE_ESTIMATES.get(norm, 20.0)
                pruned_packages.append(PrunedPackage(
                    package=entry.raw_line,
                    action="MOVED_TO_DEV",
                    reason="Classified as dev/test/tooling dependency",
                    estimated_size_mb=est_size
                ))
                continue

            # Check if referenced in AST production code or in transitive dependency expansion
            if norm in expanded_prod_packages or entry.name.lower() in expanded_prod_packages:
                prod_entries.append(entry)
            else:
                # Package is in requirements.txt but zero imports found in production code or transitive trees
                dev_entries.append(entry)
                est_size = PACKAGE_SIZE_ESTIMATES.get(norm, 15.0)
                pruned_packages.append(PrunedPackage(
                    package=entry.raw_line,
                    action="MOVED_TO_DEV",
                    reason="Zero AST import or transitive references found in production source",
                    estimated_size_mb=est_size
                ))

        return prod_entries, dev_entries, pruned_packages

    def write_segregated_files(
        self,
        prod_entries: List[RequirementEntry],
        dev_entries: List[RequirementEntry],
        output_dir: Optional[str] = None
    ) -> Tuple[str, str]:
        """Writes requirements-prod.txt and requirements-dev.txt safely."""
        target_dir = output_dir or self.root_dir
        os.makedirs(target_dir, exist_ok=True)
        prod_path = os.path.join(target_dir, "requirements-prod.txt")
        dev_path = os.path.join(target_dir, "requirements-dev.txt")

        with open(prod_path, "w", encoding="utf-8") as f:
            f.write("# ========================================================\n")
            f.write("# Synthesized by Rover-Slim: Production Runtime Dependencies\n")
            f.write("# Zero dev/test/notebook bloat for minimal Docker images\n")
            f.write("# ========================================================\n\n")
            for p in prod_entries:
                f.write(f"{p.raw_line}\n")

        with open(dev_path, "w", encoding="utf-8") as f:
            f.write("# ========================================================\n")
            f.write("# Synthesized by Rover-Slim: Development & Test Dependencies\n")
            f.write("# ========================================================\n\n")
            f.write("-r requirements-prod.txt\n\n")
            for d in dev_entries:
                f.write(f"{d.raw_line}\n")

        return prod_path, dev_path
