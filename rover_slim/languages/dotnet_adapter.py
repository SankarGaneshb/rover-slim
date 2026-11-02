import os
import re
import xml.etree.ElementTree as ET
from typing import List, Tuple, Optional, Any, Set
from rover_slim.languages.base import BaseLanguageAdapter
from rover_slim.models import PrunedPackage, ProbeConfig, RoverSlimConfig
from rover_slim.parsers.req_parser import RequirementEntry

class DotNetPackageEntry(RequirementEntry):
    """Represents a .NET NuGet package dependency entry."""
    def __init__(self, name: str, version: str = "", raw_line: str = ""):
        super().__init__(raw_line=raw_line or (f"{name} ({version})" if version else name), name=name, specifier=version)
        self.version = version

    def __str__(self) -> str:
        return f"{self.name}:{self.version}" if self.version else self.name


class DotNetLanguageAdapter(BaseLanguageAdapter):
    """
    Language adapter for .NET Core / ASP.NET Core enterprise applications.
    Parses .csproj / .fsproj package references, segregates dev/test dependencies,
    synthesizes production-hardened multi-stage .NET Dockerfiles with unprivileged non-root user (UID 10001),
    and discovers ASP.NET Core health probes (/health, /healthz).
    """

    DEV_TEST_PACKAGES: Set[str] = {
        "xunit",
        "nunit",
        "moq",
        "fluentassertions",
        "microsoft.net.test.sdk",
        "xunit.runner.visualstudio",
        "nunit3testadapter",
        "nunit.analyzers",
        "coverlet.collector",
        "coverlet.msbuild",
        "mstest.testadapter",
        "mstest.testframework",
        "specflow",
        "specflow.xunit",
        "specflow.nunit",
        "benchmarkdotnet",
        "shouldly",
        "autofixture"
    }

    DEV_TEST_PATTERNS: List[str] = [
        r"^xunit(\..+)?$",
        r"^nunit(\..+)?$",
        r"^moq(\..+)?$",
        r"^fluentassertions(\..+)?$",
        r"^microsoft\.net\.test\.sdk$",
        r"^coverlet\..+$",
        r"^mstest\..+$",
        r"^specflow(\..+)?$",
        r"^benchmarkdotnet(\..+)?$"
    ]

    PACKAGE_SIZE_ESTIMATES = {
        "microsoft.net.test.sdk": 32.0,
        "xunit": 16.5,
        "xunit.runner.visualstudio": 12.0,
        "nunit": 14.0,
        "nunit3testadapter": 10.5,
        "moq": 8.5,
        "fluentassertions": 10.0,
        "coverlet.collector": 6.5,
        "coverlet.msbuild": 5.5,
        "benchmarkdotnet": 22.0
    }

    @property
    def name(self) -> str:
        return "dotnet"

    @property
    def display_name(self) -> str:
        return ".NET Core / ASP.NET Core"

    def detect(self, root_dir: str) -> bool:
        """Detects .csproj, .fsproj, .sln, or Program.cs in repository."""
        root = os.path.abspath(root_dir)
        if not os.path.isdir(root):
            return False

        # Check top-level files
        try:
            top_files = os.listdir(root)
            for f in top_files:
                if f.endswith((".csproj", ".fsproj", ".sln")) or f == "Program.cs":
                    return True
        except OSError:
            return False

        # Scan subdirectories skipping build/system artifacts
        ignored_dirs = {".git", ".rover-slim", "bin", "obj", "node_modules", ".vs", ".idea"}
        for r, dirs, files in os.walk(root, followlinks=False):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ignored_dirs]
            for f in files:
                if f.endswith((".csproj", ".fsproj", ".sln")) or f == "Program.cs":
                    return True

        return False

    def segregate_dependencies(
        self,
        root_dir: str,
        always_prod: Optional[List[str]] = None,
        always_dev: Optional[List[str]] = None
    ) -> Tuple[List[DotNetPackageEntry], List[DotNetPackageEntry], List[PrunedPackage]]:
        """Parses <PackageReference> in .csproj to segregate production vs dev/test packages."""
        root = os.path.abspath(root_dir)
        always_prod_set = set(p.strip().lower() for p in (always_prod or []))
        always_dev_set = set(d.strip().lower() for d in (always_dev or []))

        prod_dependencies: List[DotNetPackageEntry] = []
        dev_dependencies: List[DotNetPackageEntry] = []
        pruned_packages: List[PrunedPackage] = []
        seen_packages: Set[str] = set()

        # Find all project files
        project_files: List[str] = []
        ignored_dirs = {".git", ".rover-slim", "bin", "obj", "node_modules"}
        for r, dirs, files in os.walk(root, followlinks=False):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ignored_dirs]
            for f in files:
                if f.endswith((".csproj", ".fsproj")):
                    project_files.append(os.path.join(r, f))

        if not project_files:
            # Fallback default ASP.NET Core stack
            default_prod = DotNetPackageEntry("Microsoft.AspNetCore.App", "8.0.0")
            default_dev = DotNetPackageEntry("Microsoft.NET.Test.Sdk", "17.8.0")
            prod_dependencies.append(default_prod)
            dev_dependencies.append(default_dev)
            pruned_packages.append(PrunedPackage(
                package="Microsoft.NET.Test.Sdk",
                action="EXCLUDED",
                reason="Default .NET test SDK pruned from production runtime.",
                estimated_size_mb=32.0
            ))
            return prod_dependencies, dev_dependencies, pruned_packages

        for proj in project_files:
            try:
                tree = ET.parse(proj)
                xml_root = tree.getroot()
                for elem in xml_root.iter():
                    tag_name = elem.tag.split("}")[-1]
                    if tag_name == "PackageReference":
                        pkg_name = elem.attrib.get("Include") or elem.attrib.get("Update")
                        if not pkg_name:
                            continue

                        pkg_name_clean = pkg_name.strip()
                        pkg_key = pkg_name_clean.lower()
                        if pkg_key in seen_packages:
                            continue
                        seen_packages.add(pkg_key)

                        version = elem.attrib.get("Version", "").strip()
                        if not version:
                            for child in elem:
                                if child.tag.split("}")[-1] == "Version" and child.text:
                                    version = child.text.strip()
                                    break
                        if not version:
                            version = "latest"

                        raw_xml = f'<PackageReference Include="{pkg_name_clean}" Version="{version}" />'
                        entry = DotNetPackageEntry(name=pkg_name_clean, version=version, raw_line=raw_xml)

                        # Determine if test/dev package
                        if pkg_key in always_prod_set:
                            is_test = False
                        elif pkg_key in always_dev_set:
                            is_test = True
                        else:
                            is_test = (
                                pkg_key in self.DEV_TEST_PACKAGES
                                or any(re.search(pat, pkg_key) for pat in self.DEV_TEST_PATTERNS)
                            )

                        if is_test:
                            dev_dependencies.append(entry)
                            est_size = self.PACKAGE_SIZE_ESTIMATES.get(pkg_key, 15.0)
                            pruned_packages.append(PrunedPackage(
                                package=pkg_name_clean,
                                action="EXCLUDED",
                                reason=f".NET test/development dependency ({pkg_name_clean}) pruned from production runtime.",
                                estimated_size_mb=est_size
                            ))
                        else:
                            prod_dependencies.append(entry)
            except Exception:
                continue

        return prod_dependencies, dev_dependencies, pruned_packages

    def synthesize_dockerfile(
        self,
        config: RoverSlimConfig,
        root_dir: str,
        existing_dockerfile_path: Optional[str] = None
    ) -> str:
        """Synthesizes a minimal multi-stage .NET 8/9 Dockerfile with UID 10001 non-root user."""
        root = os.path.abspath(root_dir)

        # Detect target framework (.NET 8 vs .NET 9)
        dotnet_ver = "8.0"
        project_name = config.project_name if config.project_name and config.project_name not in ("default-project", "rover-slim-project") else "App"

        # Search for .csproj to detect framework & assembly name
        for r, dirs, files in os.walk(root, followlinks=False):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["bin", "obj", ".git", ".rover-slim"]]
            for f in files:
                if f.endswith((".csproj", ".fsproj")):
                    proj_stem = f.rsplit(".", 1)[0]
                    if proj_stem and project_name == "App":
                        project_name = proj_stem
                    proj_path = os.path.join(r, f)
                    try:
                        with open(proj_path, "r", encoding="utf-8", errors="ignore") as fh:
                            content = fh.read()
                            if "net9.0" in content:
                                dotnet_ver = "9.0"
                            elif "net8.0" in content:
                                dotnet_ver = "8.0"
                    except Exception:
                        pass
                    break

        sdk_image = f"mcr.microsoft.com/dotnet/sdk:{dotnet_ver}"
        if config.build and config.build.target_base_image and ("dotnet" in config.build.target_base_image or "aspnet" in config.build.target_base_image):
            runtime_image = config.build.target_base_image
        else:
            runtime_image = f"mcr.microsoft.com/dotnet/aspnet:{dotnet_ver}-alpine"

        # Discover probe endpoint for healthcheck
        probes = self.discover_health_probes(root)
        health_path = probes[0].path if probes else "/health"
        port = probes[0].port if probes else 8080

        dll_name = f"{project_name}.dll"

        # Determine existing solution/project files to emit valid Dockerfile COPY instructions
        copy_directives = []
        try:
            entries = os.listdir(root)
            if any(f.endswith(".sln") for f in entries):
                copy_directives.append("COPY *.sln ./")
            if any(f.endswith(".csproj") for f in entries):
                copy_directives.append("COPY *.csproj ./")
            elif any(f.endswith(".fsproj") for f in entries):
                copy_directives.append("COPY *.fsproj ./")
        except Exception:
            pass

        if not copy_directives:
            copy_directives.append("COPY *.csproj ./")

        copy_proj_step = "\n".join(copy_directives)

        return f"""# Generated by Rover-Slim Polyglot Synthesizer for .NET Core
# Stage 1: Build & Publish
FROM {sdk_image} AS build
WORKDIR /source

# Copy project definitions and restore NuGet packages (layer caching optimization)
{copy_proj_step}
RUN dotnet restore --verbosity minimal

# Copy remaining source code and publish release binaries
COPY . .
RUN dotnet publish -c Release -o /app/publish --no-restore

# Stage 2: Minimal Production Runtime
FROM {runtime_image} AS runtime
WORKDIR /app

# Harden container with unprivileged non-root user (UID 10001)
RUN addgroup -g 10001 -S appgroup && adduser -u 10001 -S appuser -G appgroup

# Copy published artifacts from build stage
COPY --from=build /app/publish ./

USER 10001:10001
EXPOSE {port}
ENV ASPNETCORE_URLS=http://+:{port} \\
    DOTNET_EnableDiagnostics=0

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \\
  CMD wget -qO- http://localhost:{port}{health_path} || exit 1

ENTRYPOINT ["dotnet", "{dll_name}"]
"""

    def discover_health_probes(self, root_dir: str) -> List[ProbeConfig]:
        """Auto-discovers ASP.NET Core health endpoints (/health, /healthz) and ports."""
        root = os.path.abspath(root_dir)
        detected_paths: Set[str] = set()
        detected_port = 8080

        health_regex = re.compile(
            r"""(?:MapHealthChecks|MapGet|HttpGet|Route)\s*\(\s*["']([^"']*(?:health|healthz)[^"']*)["']""",
            re.IGNORECASE
        )

        ignored_dirs = {".git", ".rover-slim", "bin", "obj", "node_modules"}
        for r, dirs, files in os.walk(root, followlinks=False):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ignored_dirs]
            for f in files:
                full_path = os.path.join(r, f)
                # Check C# files for endpoint definitions
                if f.endswith(".cs"):
                    try:
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as cs_file:
                            code = cs_file.read()
                            for match in health_regex.finditer(code):
                                path_found = match.group(1).strip()
                                if not path_found.startswith("/"):
                                    path_found = "/" + path_found
                                detected_paths.add(path_found)

                            if "/healthz" in code:
                                detected_paths.add("/healthz")
                            elif "/health" in code:
                                detected_paths.add("/health")
                    except Exception:
                        pass

                # Check configuration files for port
                if f in ("appsettings.json", "launchSettings.json"):
                    try:
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as json_file:
                            content = json_file.read()
                            port_match = re.search(r"""(?:applicationUrl|ASPNETCORE_HTTP_PORTS|urls).*?(\d{4,5})""", content)
                            if port_match:
                                detected_port = int(port_match.group(1))
                    except Exception:
                        pass

        if not detected_paths:
            detected_paths.add("/health")

        probes: List[ProbeConfig] = []
        for path in sorted(detected_paths):
            probes.append(
                ProbeConfig(
                    name=f"ASP.NET Core Health Probe ({path})",
                    type="http",
                    path=path,
                    port=detected_port,
                    expected_status=200,
                    timeout_seconds=5
                )
            )

        return probes
