"""
Empirical Boundary and Stress-Testing Harness for Rover Slim Enhancements.
Challenger 2 - Adversarial Verification Suite.
"""

import os
import re
import tempfile
import pytest
import yaml
from rover_slim.languages.dotnet_adapter import DotNetLanguageAdapter, DotNetPackageEntry
from rover_slim.languages.registry import LanguageRegistry
from rover_slim.models import RoverSlimConfig, PrunedPackage
from rover_slim.synthesizers.decoupling import (
    DecouplingSynthesizer,
    AssetSpec,
    InitContainerConfig,
    OrasConfig,
    DecouplingReport
)


# =========================================================================
# SUITE 1: .NET LANGUAGE ADAPTER BOUNDARY & STRESS TESTS
# =========================================================================

def test_dotnet_case_insensitive_package_matching_extensive():
    """Verify adversarial casing combinations are pruned accurately."""
    adapter = DotNetLanguageAdapter()
    
    csproj_content = """<Project Sdk="Microsoft.NET.Sdk">
  <ItemGroup>
    <PackageReference Include="xUnit" Version="2.6.2" />
    <PackageReference Include="XUNIT.RUNNER.VISUALSTUDIO" Version="2.5.4" />
    <PackageReference Include="MoQ" Version="4.20.70" />
    <PackageReference Include="FluentAssertions" Version="6.12.0" />
    <PackageReference Include="NUnit" Version="4.0.1" />
    <PackageReference Include="NUNIT3TESTADAPTER" Version="4.5.0" />
    <PackageReference Include="Microsoft.Net.Test.Sdk" Version="17.8.0" />
    <PackageReference Include="Coverlet.Collector" Version="6.0.0" />
    <PackageReference Include="Coverlet.MSBuild" Version="6.0.0" />
    <PackageReference Include="BenchmarkDotNet" Version="0.13.12" />
    <PackageReference Include="SpecFlow.xUnit" Version="3.9.74" />
    <PackageReference Include="Shouldly" Version="4.2.1" />
    <PackageReference Include="AutoFixture" Version="4.18.1" />
    <PackageReference Include="Microsoft.EntityFrameworkCore" Version="8.0.0" />
    <PackageReference Include="Serilog.AspNetCore" Version="8.0.0" />
  </ItemGroup>
</Project>"""

    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "MixedCaseService.csproj"), "w", encoding="utf-8") as f:
            f.write(csproj_content)

        prod, dev, pruned = adapter.segregate_dependencies(tmpdir)
        prod_names = [p.name for p in prod]
        dev_names = [d.name.lower() for d in dev]
        pruned_dict = {p.package.lower(): p for p in pruned}

        # Verify legitimate prod packages
        assert "Microsoft.EntityFrameworkCore" in prod_names
        assert "Serilog.AspNetCore" in prod_names
        assert len(prod) == 2

        # Verify all 13 test/dev packages were segregated regardless of casing
        expected_dev = [
            "xunit", "xunit.runner.visualstudio", "moq", "fluentassertions",
            "nunit", "nunit3testadapter", "microsoft.net.test.sdk",
            "coverlet.collector", "coverlet.msbuild", "benchmarkdotnet",
            "specflow.xunit", "shouldly", "autofixture"
        ]
        for pkg in expected_dev:
            assert pkg in dev_names, f"Package {pkg} was not found in dev dependencies"
            assert pkg in pruned_dict, f"Package {pkg} was not found in pruned packages"
            entry = pruned_dict[pkg]
            assert entry.action == "EXCLUDED"
            assert entry.estimated_size_mb > 0
            assert "pruned" in entry.reason.lower()


def test_dotnet_case_insensitive_overrides():
    """Verify always_prod and always_dev overrides handle mixed and inverted casing."""
    adapter = DotNetLanguageAdapter()
    csproj = """<Project Sdk="Microsoft.NET.Sdk">
  <ItemGroup>
    <PackageReference Include="xunit" Version="2.6.2" />
    <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />
  </ItemGroup>
</Project>"""

    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "Override.csproj"), "w", encoding="utf-8") as f:
            f.write(csproj)

        # Force XUNIT into prod, force NEWTONSOFT.JSON into dev
        prod, dev, pruned = adapter.segregate_dependencies(
            tmpdir,
            always_prod=["XUNIT"],
            always_dev=["nEwToNsOfT.jSoN"]
        )
        prod_names = [p.name.lower() for p in prod]
        dev_names = [d.name.lower() for d in dev]

        assert "xunit" in prod_names
        assert "newtonsoft.json" in dev_names


def test_dotnet_project_xml_with_namespaces():
    """Verify parsing works on traditional MSBuild XML with xmlns attributes."""
    adapter = DotNetLanguageAdapter()
    namespaced_csproj = """<?xml version="1.0" encoding="utf-8"?>
<Project ToolsVersion="15.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <ItemGroup>
    <PackageReference Include="Microsoft.AspNetCore.OpenApi">
      <Version>8.0.0</Version>
    </PackageReference>
    <PackageReference Include="Moq">
      <Version>4.20.70</Version>
    </PackageReference>
  </ItemGroup>
</Project>"""

    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "Legacy.csproj"), "w", encoding="utf-8") as f:
            f.write(namespaced_csproj)

        prod, dev, pruned = adapter.segregate_dependencies(tmpdir)
        assert any(p.name == "Microsoft.AspNetCore.OpenApi" for p in prod)
        assert any(d.name == "Moq" for d in dev)
        # Check child Version tag was extracted
        assert prod[0].version == "8.0.0"
        assert dev[0].version == "4.20.70"


def test_dotnet_central_package_management_cpm():
    """Verify Central Package Management (CPM) without inline Version attributes."""
    adapter = DotNetLanguageAdapter()
    cpm_csproj = """<Project Sdk="Microsoft.NET.Sdk.Web">
  <ItemGroup>
    <PackageReference Include="Dapper" />
    <PackageReference Update="Npgsql" Version="8.0.2" />
    <PackageReference Include="xunit" />
  </ItemGroup>
</Project>"""

    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "CpmApp.csproj"), "w", encoding="utf-8") as f:
            f.write(cpm_csproj)

        prod, dev, pruned = adapter.segregate_dependencies(tmpdir)
        prod_dict = {p.name: p.version for p in prod}
        dev_dict = {d.name: d.version for d in dev}

        assert "Dapper" in prod_dict
        assert prod_dict["Dapper"] == "latest"  # Fallback for CPM without version
        assert "Npgsql" in prod_dict
        assert prod_dict["Npgsql"] == "8.0.2"   # Handled via Update attribute
        assert "xunit" in dev_dict
        assert dev_dict["xunit"] == "latest"


def test_dotnet_malformed_and_empty_project_files():
    """Verify corrupt XML or 0-byte project files do not crash the parser."""
    adapter = DotNetLanguageAdapter()
    with tempfile.TemporaryDirectory() as tmpdir:
        # Zero-byte csproj
        open(os.path.join(tmpdir, "Empty.csproj"), "w").close()
        # Corrupt XML
        with open(os.path.join(tmpdir, "Corrupt.csproj"), "w", encoding="utf-8") as f:
            f.write("<Project><UnclosedTag>")

        # Valid csproj alongside corrupt ones
        with open(os.path.join(tmpdir, "Valid.csproj"), "w", encoding="utf-8") as f:
            f.write("""<Project Sdk="Microsoft.NET.Sdk">
  <ItemGroup>
    <PackageReference Include="Microsoft.Extensions.Logging" Version="8.0.0" />
    <PackageReference Include="xunit" Version="2.6.2" />
  </ItemGroup>
</Project>""")

        prod, dev, pruned = adapter.segregate_dependencies(tmpdir)
        assert any(p.name == "Microsoft.Extensions.Logging" for p in prod)
        assert any(d.name == "xunit" for d in dev)


def test_dotnet_pure_program_cs_fallback():
    """Verify fallback behavior when only Program.cs is present without any project files."""
    adapter = DotNetLanguageAdapter()
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "Program.cs"), "w", encoding="utf-8") as f:
            f.write('var app = WebApplication.Create(); app.MapGet("/", () => "OK"); app.Run();')

        assert adapter.detect(tmpdir) is True
        prod, dev, pruned = adapter.segregate_dependencies(tmpdir)
        assert len(prod) == 1
        assert prod[0].name == "Microsoft.AspNetCore.App"
        assert len(dev) == 1
        assert dev[0].name == "Microsoft.NET.Test.Sdk"
        assert len(pruned) == 1
        assert pruned[0].action == "EXCLUDED"


def test_dotnet_framework_version_detection():
    """Verify target framework detection across .NET 8, .NET 9, and fallback defaults."""
    adapter = DotNetLanguageAdapter()

    # Case 1: .NET 9.0
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "Net9App.csproj"), "w", encoding="utf-8") as f:
            f.write("<Project><PropertyGroup><TargetFramework>net9.0</TargetFramework></PropertyGroup></Project>")
        df = adapter.synthesize_dockerfile(RoverSlimConfig(), tmpdir)
        assert "mcr.microsoft.com/dotnet/sdk:9.0" in df
        assert "mcr.microsoft.com/dotnet/aspnet:9.0-alpine" in df
        assert 'ENTRYPOINT ["dotnet", "Net9App.dll"]' in df

    # Case 2: .NET 8.0
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "Net8App.csproj"), "w", encoding="utf-8") as f:
            f.write("<Project><PropertyGroup><TargetFramework>net8.0</TargetFramework></PropertyGroup></Project>")
        df = adapter.synthesize_dockerfile(RoverSlimConfig(), tmpdir)
        assert "mcr.microsoft.com/dotnet/sdk:8.0" in df
        assert "mcr.microsoft.com/dotnet/aspnet:8.0-alpine" in df
        assert 'ENTRYPOINT ["dotnet", "Net8App.dll"]' in df

    # Case 3: Missing TargetFramework -> Default to 8.0
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "DefaultApp.csproj"), "w", encoding="utf-8") as f:
            f.write("<Project><PropertyGroup><Nullable>enable</Nullable></PropertyGroup></Project>")
        df = adapter.synthesize_dockerfile(RoverSlimConfig(), tmpdir)
        assert "mcr.microsoft.com/dotnet/sdk:8.0" in df
        assert "mcr.microsoft.com/dotnet/aspnet:8.0-alpine" in df


def test_dotnet_health_probe_discovery_edge_cases():
    """Verify discovery across minimal APIs, controller attributes, and launchSettings."""
    adapter = DotNetLanguageAdapter()

    # Case 1: Controller HttpGet and Route attributes
    controller_code = """
namespace MyApi.Controllers {
    [ApiController]
    [Route("api/[controller]")]
    public class DiagnosticsController : ControllerBase {
        [HttpGet("/health")]
        public IActionResult GetHealth() => Ok("Healthy");

        [Route("/healthz")]
        public IActionResult GetLiveness() => Ok("Live");
    }
}
"""
    launch_settings = {
        "profiles": {
            "http": {
                "applicationUrl": "http://localhost:5288"
            }
        }
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, "DiagnosticsController.cs"), "w", encoding="utf-8") as f:
            f.write(controller_code)
        os.makedirs(os.path.join(tmpdir, "Properties"), exist_ok=True)
        with open(os.path.join(tmpdir, "Properties", "launchSettings.json"), "w", encoding="utf-8") as f:
            import json
            json.dump(launch_settings, f)

        probes = adapter.discover_health_probes(tmpdir)
        paths = [p.path for p in probes]
        assert "/health" in paths
        assert "/healthz" in paths
        assert all(p.port == 5288 for p in probes)


# =========================================================================
# SUITE 2: CLOUD-NATIVE DECOUPLING SYNTHESIZER BOUNDARY & STRESS TESTS
# =========================================================================

def test_decoupling_volume_deduplication_stress():
    """Verify that multiple assets sharing a volume_name result in exactly 1 volume in spec."""
    synth = DecouplingSynthesizer()
    
    # 4 distinct assets referencing the same volume
    assets = [
        AssetSpec(
            name=f"asset-chunk-{i}",
            source_path=f"dist/chunk-{i}",
            mount_path=f"/app/static/chunk-{i}",
            remote_artifact_ref=f"registry.enterprise.local/chunks/chunk-{i}:v1",
            volume_name="shared-bundle-volume"
        )
        for i in range(1, 5)
    ]

    patch = synth.generate_init_container_patch(assets, single_init_container=True)
    spec = patch["spec"]["template"]["spec"]

    # Exactly 1 volume
    assert len(spec["volumes"]) == 1
    assert spec["volumes"][0]["name"] == "shared-bundle-volume"

    # Single init container mounts all 4 mountPaths cleanly
    assert len(spec["initContainers"]) == 1
    init_mounts = spec["initContainers"][0]["volumeMounts"]
    assert len(init_mounts) == 4
    for m in init_mounts:
        assert m["name"] == "shared-bundle-volume"

    # App container mounts all 4 mountPaths with readOnly: True
    app_mounts = spec["containers"][0]["volumeMounts"]
    assert len(app_mounts) == 4
    for m in app_mounts:
        assert m["name"] == "shared-bundle-volume"
        assert m["readOnly"] is True


def test_decoupling_duplicate_mount_path_deduplication():
    """Verify that assets sharing the exact same mount_path do not duplicate container volumeMounts."""
    synth = DecouplingSynthesizer()
    assets = [
        AssetSpec(
            name="base-static",
            source_path="dist/base",
            mount_path="/app/static",
            remote_artifact_ref="registry.enterprise.local/static:1.0",
            volume_name="static-vol"
        ),
        AssetSpec(
            name="patch-static",
            source_path="dist/patch",
            mount_path="/app/static",
            remote_artifact_ref="registry.enterprise.local/static-patch:1.0",
            volume_name="static-vol"
        )
    ]

    patch = synth.generate_init_container_patch(assets, single_init_container=True)
    spec = patch["spec"]["template"]["spec"]

    # init container should mount /app/static only once
    assert len(spec["initContainers"][0]["volumeMounts"]) == 1
    # app container should mount /app/static only once
    assert len(spec["containers"][0]["volumeMounts"]) == 1


def test_decoupling_asset_validation_boundary():
    """Verify strict validation on names and paths."""
    # Valid characters
    valid_asset = AssetSpec(
        name="my-asset.part_1",
        source_path="data/",
        mount_path="/var/data",
        remote_artifact_ref="reg.local/data:1"
    )
    assert valid_asset.name == "my-asset.part_1"
    # DNS-1123 sanitized effective volume name
    assert valid_asset.effective_volume_name == "my-asset-part-1-volume"

    # Invalid names
    for bad_name in ["", " space-start", "bad$char", "-hyphen-start", "slash/name"]:
        with pytest.raises(ValueError):
            AssetSpec(
                name=bad_name,
                source_path="data/",
                mount_path="/valid",
                remote_artifact_ref="reg.local/data:1"
            )

    # Invalid mount paths (must be absolute Unix path starting with /)
    for bad_path in ["", "relative/path", "C:\\Windows\\Path", "app/static"]:
        with pytest.raises(ValueError, match="must be an absolute Unix path"):
            AssetSpec(
                name="valid-name",
                source_path="data/",
                mount_path=bad_path,
                remote_artifact_ref="reg.local/data:1"
            )


def test_decoupling_protocol_flags_and_media_types():
    """Verify --plain-http, --insecure flags and custom media types."""
    oras_cfg = OrasConfig(plain_http=True, insecure=True)
    synth = DecouplingSynthesizer(oras_config=oras_cfg)

    asset = AssetSpec(
        name="custom-layer-asset",
        source_path="assets/dataset.parquet",
        mount_path="/app/datasets",
        remote_artifact_ref="registry.enterprise.local/data/dataset:v1.0",
        media_type="application/vnd.apache.parquet"
    )

    # Push commands
    push_cmds = synth.generate_oras_push_commands([asset])
    assert len(push_cmds) == 1
    assert "--plain-http" in push_cmds[0]
    assert "--insecure" in push_cmds[0]
    assert "assets/dataset.parquet:application/vnd.apache.parquet" in push_cmds[0]

    # Pull commands
    pull_cmds = synth.generate_oras_pull_commands([asset])
    assert len(pull_cmds) == 1
    assert "--plain-http" in pull_cmds[0]
    assert "--insecure" in pull_cmds[0]
    assert "-o /app/datasets" in pull_cmds[0]

    # Init container args in patch
    patch = synth.generate_init_container_patch([asset])
    init_cmd = patch["spec"]["template"]["spec"]["initContainers"][0]["args"][0]
    assert "--plain-http" in init_cmd
    assert "--insecure" in init_cmd


def test_decoupling_custom_init_container_security():
    """Verify security context customization and default non-root values."""
    custom_init_cfg = InitContainerConfig(
        image="ghcr.io/oras-project/oras:v1.2.3",
        run_as_user=20002,
        read_only_root_filesystem=True,
        cpu_limit="500m",
        memory_limit="512Mi"
    )
    synth = DecouplingSynthesizer(init_container_config=custom_init_cfg)

    asset = AssetSpec(
        name="secure-asset",
        source_path="dist/",
        mount_path="/app/secure",
        remote_artifact_ref="registry.enterprise.local/secure:1.0"
    )

    patch = synth.generate_init_container_patch([asset])
    init_c = patch["spec"]["template"]["spec"]["initContainers"][0]

    assert init_c["image"] == "ghcr.io/oras-project/oras:v1.2.3"
    assert init_c["resources"]["limits"]["cpu"] == "500m"
    assert init_c["resources"]["limits"]["memory"] == "512Mi"
    assert init_c["securityContext"]["runAsUser"] == 20002
    assert init_c["securityContext"]["readOnlyRootFilesystem"] is True
    assert init_c["securityContext"]["runAsNonRoot"] is True
