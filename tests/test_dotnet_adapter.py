import os
import json
import tempfile
import pytest
from rover_slim.languages.dotnet_adapter import DotNetLanguageAdapter
from rover_slim.languages.registry import LanguageRegistry
from rover_slim.models import RoverSlimConfig

SAMPLE_CSPROJ_NET8 = """<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.AspNetCore.OpenApi" Version="8.0.0" />
    <PackageReference Include="Swashbuckle.AspNetCore" Version="6.5.0" />
    <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />
    <PackageReference Include="xunit" Version="2.6.2" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.5.4" />
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.8.0" />
    <PackageReference Include="Moq" Version="4.20.70" />
    <PackageReference Include="FluentAssertions" Version="6.12.0" />
    <PackageReference Include="nunit" Version="4.0.1" />
  </ItemGroup>
</Project>
"""

SAMPLE_CSPROJ_NET9 = """<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.AspNetCore.OpenApi" Version="9.0.0" />
    <PackageReference Include="xunit" Version="2.6.2" />
  </ItemGroup>
</Project>
"""

SAMPLE_PROGRAM_CS = """
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddHealthChecks();

var app = builder.Build();
app.MapHealthChecks("/healthz");
app.Run();
"""

def test_dotnet_adapter_detection():
    adapter = DotNetLanguageAdapter()
    with tempfile.TemporaryDirectory() as tmpdir:
        assert adapter.detect(tmpdir) is False

        # Detect .csproj
        with open(os.path.join(tmpdir, "EnterpriseService.csproj"), "w", encoding="utf-8") as f:
            f.write(SAMPLE_CSPROJ_NET8)
        assert adapter.detect(tmpdir) is True
        assert adapter.name == "dotnet"
        assert adapter.display_name == ".NET Core / ASP.NET Core"

    with tempfile.TemporaryDirectory() as tmpdir:
        # Detect Program.cs
        with open(os.path.join(tmpdir, "Program.cs"), "w", encoding="utf-8") as f:
            f.write(SAMPLE_PROGRAM_CS)
        assert adapter.detect(tmpdir) is True

    with tempfile.TemporaryDirectory() as tmpdir:
        # Detect .sln
        with open(os.path.join(tmpdir, "EnterpriseSolution.sln"), "w", encoding="utf-8") as f:
            f.write("Microsoft Visual Studio Solution File, Format Version 12.00")
        assert adapter.detect(tmpdir) is True

    with tempfile.TemporaryDirectory() as tmpdir:
        # Detect .fsproj
        with open(os.path.join(tmpdir, "EnterpriseFSharp.fsproj"), "w", encoding="utf-8") as f:
            f.write(SAMPLE_CSPROJ_NET8)
        assert adapter.detect(tmpdir) is True

    with tempfile.TemporaryDirectory() as tmpdir:
        # Detect nested .csproj in subfolder
        subdir = os.path.join(tmpdir, "src", "SubService")
        os.makedirs(subdir, exist_ok=True)
        with open(os.path.join(subdir, "SubService.csproj"), "w", encoding="utf-8") as f:
            f.write(SAMPLE_CSPROJ_NET8)
        assert adapter.detect(tmpdir) is True

def test_dotnet_adapter_dependency_segregation():
    adapter = DotNetLanguageAdapter()
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "Service.csproj"), "w", encoding="utf-8") as f:
            f.write(SAMPLE_CSPROJ_NET8)

        prod, dev, pruned = adapter.segregate_dependencies(tmpdir)
        prod_names = [p.name for p in prod]
        dev_names = [d.name for d in dev]
        pruned_packages = [p.package.lower() for p in pruned]

        # Verify production packages retained
        assert "Microsoft.AspNetCore.OpenApi" in prod_names
        assert "Swashbuckle.AspNetCore" in prod_names
        assert "Newtonsoft.Json" in prod_names

        # Verify test/dev packages pruned
        assert "xunit" in dev_names
        assert "Microsoft.NET.Test.Sdk" in dev_names
        assert "Moq" in dev_names
        assert "FluentAssertions" in dev_names
        assert "nunit" in dev_names

        # Verify pruned packages list contains all required targets case-insensitively
        assert "xunit" in pruned_packages
        assert "nunit" in pruned_packages
        assert "moq" in pruned_packages
        assert "fluentassertions" in pruned_packages
        assert "microsoft.net.test.sdk" in pruned_packages

        # Verify PrunedPackage attributes
        for p in pruned:
            assert p.action == "EXCLUDED"
            assert p.estimated_size_mb > 0
            assert "pruned" in p.reason.lower()

def test_dotnet_adapter_dependency_overrides():
    adapter = DotNetLanguageAdapter()
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "Service.csproj"), "w", encoding="utf-8") as f:
            f.write(SAMPLE_CSPROJ_NET8)

        # Force nunit to prod, force Newtonsoft.Json to dev
        prod, dev, pruned = adapter.segregate_dependencies(
            tmpdir,
            always_prod=["nunit"],
            always_dev=["Newtonsoft.Json"]
        )
        prod_names = [p.name for p in prod]
        dev_names = [d.name for d in dev]

        assert "nunit" in prod_names
        assert "Newtonsoft.Json" in dev_names

def test_dotnet_adapter_empty_manifest_fallback():
    adapter = DotNetLanguageAdapter()
    with tempfile.TemporaryDirectory() as tmpdir:
        prod, dev, pruned = adapter.segregate_dependencies(tmpdir)
        assert len(prod) == 1
        assert prod[0].name == "Microsoft.AspNetCore.App"
        assert len(dev) == 1
        assert dev[0].name == "Microsoft.NET.Test.Sdk"
        assert len(pruned) == 1
        assert pruned[0].package == "Microsoft.NET.Test.Sdk"
        assert pruned[0].action == "EXCLUDED"

def test_dotnet_adapter_dockerfile_synthesis_net8():
    adapter = DotNetLanguageAdapter()
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "EnterpriseApp.csproj"), "w", encoding="utf-8") as f:
            f.write(SAMPLE_CSPROJ_NET8)

        config = RoverSlimConfig()
        df = adapter.synthesize_dockerfile(config, tmpdir)

        assert "FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build" in df
        assert "FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine AS runtime" in df
        assert "COPY *.csproj ./" in df
        assert "2>/dev/null" not in df
        assert "dotnet restore" in df
        assert "dotnet publish" in df
        assert "USER 10001:10001" in df
        assert "EXPOSE 8080" in df
        assert "HEALTHCHECK" in df
        assert 'ENTRYPOINT ["dotnet", "EnterpriseApp.dll"]' in df

def test_dotnet_adapter_dockerfile_synthesis_with_solution():
    adapter = DotNetLanguageAdapter()
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "EnterpriseApp.sln"), "w", encoding="utf-8") as f:
            f.write("Microsoft Visual Studio Solution File, Format Version 12.00")
        with open(os.path.join(tmpdir, "EnterpriseApp.csproj"), "w", encoding="utf-8") as f:
            f.write(SAMPLE_CSPROJ_NET8)

        config = RoverSlimConfig()
        df = adapter.synthesize_dockerfile(config, tmpdir)

        assert "COPY *.sln ./" in df
        assert "COPY *.csproj ./" in df
        assert "2>/dev/null" not in df

def test_dotnet_adapter_dockerfile_synthesis_net9():
    adapter = DotNetLanguageAdapter()
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "NextGenApp.csproj"), "w", encoding="utf-8") as f:
            f.write(SAMPLE_CSPROJ_NET9)

        config = RoverSlimConfig()
        df = adapter.synthesize_dockerfile(config, tmpdir)

        assert "FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build" in df
        assert "FROM mcr.microsoft.com/dotnet/aspnet:9.0-alpine AS runtime" in df
        assert 'ENTRYPOINT ["dotnet", "NextGenApp.dll"]' in df

def test_dotnet_adapter_health_probe_discovery():
    adapter = DotNetLanguageAdapter()
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "Program.cs"), "w", encoding="utf-8") as f:
            f.write(SAMPLE_PROGRAM_CS)

        probes = adapter.discover_health_probes(tmpdir)
        assert len(probes) >= 1
        probe_paths = [p.path for p in probes]
        assert "/healthz" in probe_paths
        assert probes[0].port == 8080
        assert probes[0].expected_status == 200

def test_dotnet_adapter_health_probe_discovery_appsettings():
    adapter = DotNetLanguageAdapter()
    with tempfile.TemporaryDirectory() as tmpdir:
        program_cs = """
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();
app.MapGet("/health", () => "OK");
app.Run();
"""
        with open(os.path.join(tmpdir, "Program.cs"), "w", encoding="utf-8") as f:
            f.write(program_cs)

        appsettings = {
            "applicationUrl": "http://localhost:5005"
        }
        with open(os.path.join(tmpdir, "appsettings.json"), "w", encoding="utf-8") as f:
            json.dump(appsettings, f)

        probes = adapter.discover_health_probes(tmpdir)
        assert len(probes) >= 1
        probe_paths = [p.path for p in probes]
        assert "/health" in probe_paths
        assert any(p.port == 5005 for p in probes)

def test_registry_detects_dotnet():
    registry = LanguageRegistry()
    # Already registered in __init__, but register is idempotent
    registry.register(DotNetLanguageAdapter())

    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "TestService.csproj"), "w", encoding="utf-8") as f:
            f.write(SAMPLE_CSPROJ_NET8)

        detected = registry.detect_language(tmpdir)
        assert detected.name == "dotnet"
        assert detected.display_name == ".NET Core / ASP.NET Core"
