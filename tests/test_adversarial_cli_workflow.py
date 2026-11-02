"""
Empirical Adversarial Test Suite for CLI Decouple Command and Container Governance Policy Gate.
Executed by Challenger 1 (CLI & Workflow Challenger).
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
import pytest
import yaml
from typer.testing import CliRunner

from rover_slim.cli import app

runner = CliRunner()


# ==============================================================================
# 1. PARAMETER BOUNDARY & CLI ADVERSARIAL STRESS-TESTS (CliRunner & Subprocess)
# ==============================================================================

def test_decouple_missing_all_arguments():
    """Verify missing required asset_path, --mount, and --ref exits with error (non-zero)."""
    result = runner.invoke(app, ["decouple"])
    assert result.exit_code != 0
    # Typer/Click reports Missing argument / Missing option
    assert "Missing" in result.output or "Usage:" in result.output


def test_decouple_missing_mount_option(tmp_path):
    """Verify missing --mount option exits with code != 0."""
    asset = tmp_path / "assets"
    asset.mkdir()
    result = runner.invoke(app, [
        "decouple",
        str(asset),
        "--ref", "registry.enterprise.local/assets/frontend:v1.0.0"
    ])
    assert result.exit_code != 0
    assert "Missing option" in result.output or "--mount" in result.output


def test_decouple_missing_ref_option(tmp_path):
    """Verify missing --ref option exits with code != 0."""
    asset = tmp_path / "assets"
    asset.mkdir()
    result = runner.invoke(app, [
        "decouple",
        str(asset),
        "--mount", "/app/static"
    ])
    assert result.exit_code != 0
    assert "Missing option" in result.output or "--ref" in result.output


@pytest.mark.parametrize("invalid_mount", [
    "app/static",
    "./app/static",
    "../static",
    "relative/path",
    "static",
])
def test_decouple_invalid_mount_path_relative(tmp_path, invalid_mount):
    """Verify relative mount paths are strictly rejected with exit code 1."""
    asset = tmp_path / "dist"
    asset.mkdir()
    result = runner.invoke(app, [
        "decouple",
        str(asset),
        "--mount", invalid_mount,
        "--ref", "registry.enterprise.local/assets/bundle:v1.0"
    ])
    assert result.exit_code == 1
    assert "Decoupling failed:" in result.output
    normalized_output = " ".join(result.output.split())
    assert "must be an absolute Unix path" in normalized_output
    assert "starting with '/'" in normalized_output


def test_decouple_empty_mount_path(tmp_path):
    """Verify empty string mount path is rejected."""
    asset = tmp_path / "dist"
    asset.mkdir()
    result = runner.invoke(app, [
        "decouple",
        str(asset),
        "--mount", "",
        "--ref", "registry.enterprise.local/assets/bundle:v1.0"
    ])
    assert result.exit_code == 1
    assert "Decoupling failed:" in result.output


def test_decouple_non_existent_asset_path(tmp_path):
    """Verify decoupling a non-existent asset path succeeds gracefully with 0.0 MB size estimate."""
    non_existent = tmp_path / "does_not_exist_static"
    result = runner.invoke(app, [
        "decouple",
        str(non_existent),
        "--mount", "/app/static",
        "--ref", "registry.enterprise.local/assets/app:v1"
    ])
    assert result.exit_code == 0
    assert "Cloud-Native Decoupling Synthesis Complete" in result.output
    assert "Estimated Savings: 0.0 MB" in result.output


def test_decouple_valid_file_asset(tmp_path):
    """Verify decoupling a single heavy static file calculates correct size and outputs bundle."""
    file_path = tmp_path / "large_model.bin"
    # Write 2 MB dummy data
    file_path.write_bytes(b"0" * (2 * 1024 * 1024))

    result = runner.invoke(app, [
        "decouple",
        str(file_path),
        "--mount", "/app/models/large_model.bin",
        "--ref", "registry.enterprise.local/models/bert:v1"
    ])
    assert result.exit_code == 0
    assert "Cloud-Native Decoupling Synthesis Complete" in result.output
    assert "Estimated Savings: 2.0 MB" in result.output
    assert "init-fetch-" in result.output


def test_decouple_valid_directory_asset(tmp_path):
    """Verify decoupling a nested directory calculates aggregate size and outputs bundle."""
    dist_dir = tmp_path / "frontend_dist"
    dist_dir.mkdir()
    (dist_dir / "index.html").write_bytes(b"A" * (512 * 1024))  # 0.5 MB
    sub = dist_dir / "assets"
    sub.mkdir()
    (sub / "bundle.js").write_bytes(b"B" * (1024 * 1024))  # 1.0 MB

    result = runner.invoke(app, [
        "decouple",
        str(dist_dir),
        "--mount", "/app/public",
        "--ref", "registry.enterprise.local/frontend/assets:2026.1"
    ])
    assert result.exit_code == 0
    assert "Cloud-Native Decoupling Synthesis Complete" in result.output
    # Total ~1.5 MB
    assert "Estimated Savings: 1.5 MB" in result.output


def test_decouple_custom_name_and_workload_and_container(tmp_path):
    """Verify custom --name, --workload-type Pod, and --target-container."""
    asset_dir = tmp_path / "static_assets"
    asset_dir.mkdir()
    (asset_dir / "style.css").write_text("body { margin: 0; }", encoding="utf-8")

    result = runner.invoke(app, [
        "decouple",
        str(asset_dir),
        "--mount", "/var/www/html",
        "--ref", "registry.enterprise.local/web/css:v2",
        "--name", "enterprise-theme",
        "--workload-type", "Pod",
        "--target-container", "nginx-ingress"
    ])
    assert result.exit_code == 0
    assert "init-fetch-enterprise-theme" in result.output
    assert "enterprise-theme-volume" in result.output
    assert "nginx-ingress" in result.output
    assert "kind: Pod" in result.output


def test_decouple_sanitization_of_complex_asset_path(tmp_path):
    """Verify automatic asset name sanitization when name is omitted and path has punctuation."""
    weird_dir = tmp_path / ".-_frontend--assets.v2_.-"
    weird_dir.mkdir()
    (weird_dir / "main.js").write_text("console.log('test')", encoding="utf-8")

    result = runner.invoke(app, [
        "decouple",
        str(weird_dir),
        "--mount", "/app/dist",
        "--ref", "registry.enterprise.local/assets:v1"
    ])
    assert result.exit_code == 0
    assert "Cloud-Native Decoupling Synthesis Complete" in result.output


def test_decouple_adversarial_invalid_name(tmp_path):
    """Verify that an invalid asset name (e.g., spaces or illegal characters) fails gracefully with exit code 1."""
    asset_dir = tmp_path / "assets"
    asset_dir.mkdir()

    result = runner.invoke(app, [
        "decouple",
        str(asset_dir),
        "--mount", "/app/static",
        "--ref", "registry.enterprise.local/assets:v1",
        "--name", "invalid name with spaces!"
    ])
    assert result.exit_code == 1
    assert "Decoupling failed:" in result.output


def test_decouple_adversarial_invalid_workload_type(tmp_path):
    """Verify that an unsupported workload type fails gracefully with exit code 1."""
    asset_dir = tmp_path / "assets"
    asset_dir.mkdir()

    result = runner.invoke(app, [
        "decouple",
        str(asset_dir),
        "--mount", "/app/static",
        "--ref", "registry.enterprise.local/assets:v1",
        "--workload-type", "InvalidWorkloadType"
    ])
    assert result.exit_code == 1
    assert "Decoupling failed:" in result.output
    assert "Unsupported workload type" in result.output


def test_decouple_adversarial_invalid_ref(tmp_path):
    """Verify that an invalid OCI reference fails gracefully with exit code 1."""
    asset_dir = tmp_path / "assets"
    asset_dir.mkdir()

    result = runner.invoke(app, [
        "decouple",
        str(asset_dir),
        "--mount", "/app/static",
        "--ref", "invalid reference with spaces $$$"
    ])
    assert result.exit_code == 1
    assert "Decoupling failed:" in result.output


# ==============================================================================
# 2. OUTPUT FILE GENERATION & SYNTAX VALIDATION
# ==============================================================================

def test_decouple_file_generation_all_four_files_syntax(tmp_path):
    """
    Verify --output creates the directory and writes all 4 files with valid YAML and sh syntax:
    1. init-container-deployment-patch.yaml (Valid Kubernetes Deployment YAML)
    2. init-container-pod-patch.yaml (Valid Kubernetes Pod YAML)
    3. oras-push.sh (Valid POSIX sh script with shebang)
    4. oras-pull.sh (Valid POSIX sh script with shebang)
    """
    asset_dir = tmp_path / "web_dist"
    asset_dir.mkdir()
    (asset_dir / "app.min.js").write_bytes(b"X" * 1024)

    out_dir = tmp_path / "manifests_output" / "nested"

    result = runner.invoke(app, [
        "decouple",
        str(asset_dir),
        "--mount", "/app/dist",
        "--ref", "registry.enterprise.local/frontend/bundle:v1.2.3",
        "--name", "frontend-bundle",
        "--target-container", "web-gateway",
        "--plain-http",
        "--insecure",
        "--output", str(out_dir)
    ])
    assert result.exit_code == 0
    assert "Cloud-Native Decoupling manifests synthesized successfully" in result.output

    dep_patch_file = out_dir / "init-container-deployment-patch.yaml"
    pod_patch_file = out_dir / "init-container-pod-patch.yaml"
    push_sh_file = out_dir / "oras-push.sh"
    pull_sh_file = out_dir / "oras-pull.sh"

    assert dep_patch_file.is_file(), "init-container-deployment-patch.yaml was not created"
    assert pod_patch_file.is_file(), "init-container-pod-patch.yaml was not created"
    assert push_sh_file.is_file(), "oras-push.sh was not created"
    assert pull_sh_file.is_file(), "oras-pull.sh was not created"

    # 1. Parse and validate Deployment Patch YAML
    dep_content = dep_patch_file.read_text(encoding="utf-8")
    dep_yaml = yaml.safe_load(dep_content)
    assert dep_yaml["apiVersion"] == "apps/v1"
    assert dep_yaml["kind"] == "Deployment"
    spec = dep_yaml["spec"]["template"]["spec"]
    # Check volume
    assert any(v["name"] == "frontend-bundle-volume" and "emptyDir" in v for v in spec["volumes"])
    # Check init container
    init_c = spec["initContainers"][0]
    assert init_c["name"] == "init-fetch-frontend-bundle"
    assert init_c["image"] == "ghcr.io/oras-project/oras:v1.2.2"
    assert any(vm["name"] == "frontend-bundle-volume" for vm in init_c["volumeMounts"])
    # Check target container volume mount
    target_c = [c for c in spec["containers"] if c["name"] == "web-gateway"][0]
    assert any(vm["name"] == "frontend-bundle-volume" and vm["mountPath"] == "/app/dist" for vm in target_c["volumeMounts"])

    # 2. Parse and validate Pod Patch YAML
    pod_content = pod_patch_file.read_text(encoding="utf-8")
    pod_yaml = yaml.safe_load(pod_content)
    assert pod_yaml["apiVersion"] == "v1"
    assert pod_yaml["kind"] == "Pod"
    pod_spec = pod_yaml["spec"]
    assert any(v["name"] == "frontend-bundle-volume" for v in pod_spec["volumes"])
    assert pod_spec["initContainers"][0]["name"] == "init-fetch-frontend-bundle"

    # 3. Validate ORAS Push Shell Script
    push_content = push_sh_file.read_text(encoding="utf-8")
    assert push_content.startswith("#!/bin/sh\nset -e\n")
    assert "oras push --plain-http --insecure registry.enterprise.local/frontend/bundle:v1.2.3" in push_content

    # 4. Validate ORAS Pull Shell Script
    pull_content = pull_sh_file.read_text(encoding="utf-8")
    assert pull_content.startswith("#!/bin/sh\nset -e\n")
    assert "oras pull --plain-http --insecure registry.enterprise.local/frontend/bundle:v1.2.3 -o /app/dist" in pull_content


# ==============================================================================
# 3. DIRECT SUBPROCESS EXECUTION CLI TESTS
# ==============================================================================

def test_decouple_direct_subprocess_execution(tmp_path):
    """Verify decoupling executes cleanly via python -m subprocess with zero crashes."""
    asset_file = tmp_path / "sample.tar.gz"
    asset_file.write_bytes(b"Z" * 1024)

    cmd = [
        sys.executable,
        "-m",
        "rover_slim.cli",
        "decouple",
        str(asset_file),
        "--mount", "/opt/data",
        "--ref", "registry.enterprise.local/data/archive:v1",
        "--name", "archive-data"
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    assert proc.returncode == 0, f"Subprocess failed with stderr: {proc.stderr}"
    assert "Cloud-Native Decoupling Synthesis Complete" in proc.stdout
    assert "init-fetch-archive-data" in proc.stdout
    assert "Traceback" not in proc.stderr
    assert "Traceback" not in proc.stdout


def test_decouple_direct_subprocess_missing_args():
    """Verify subprocess exits with non-zero code on missing arguments without Python traceback."""
    cmd = [
        sys.executable,
        "-m",
        "rover_slim.cli",
        "decouple"
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    assert proc.returncode != 0
    # No unhandled traceback
    assert "Traceback (most recent call last)" not in proc.stderr


# ==============================================================================
# 4. CONTAINER GOVERNANCE POLICY GATE EMBEDDED SCRIPT STRESS-TESTS
# ==============================================================================

GOVERNANCE_SCRIPT = """
import json
import sys

REPORT_PATH = sys.argv[1] if len(sys.argv) > 1 else ".rover-slim/report.json"
MAX_IMAGE_SIZE_MB = 350.0
MAX_WASTED_PERCENT = 10.0

print("=" * 70)
print("[POLICY GATE] ENTERPRISE CONTAINER GOVERNANCE EVALUATION")
print("=" * 70)

try:
    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        report = json.load(f)
except Exception as exc:
    print(f"[FATAL] Could not read governance report from {REPORT_PATH}: {exc}")
    sys.exit(1)

optimized = report.get("optimized", {})
wasted_pct = float(optimized.get("wasted_percent", 0.0))
size_mb = float(optimized.get("uncompressed_size_mb", 0.0))
cve_summary = optimized.get("cve_summary", {})
critical_cves = int(cve_summary.get("CRITICAL", 0))
high_cves = int(cve_summary.get("HIGH", 0))
goa_status = report.get("goa_verification", {}).get("overall_status", "UNKNOWN")
overall_status = report.get("status", "UNKNOWN")

print(f"  * Overall Status        : {overall_status}")
print(f"  * GoA Sentinel Status   : {goa_status}")
print(f"  * Final Image Size      : {size_mb:.2f} MB (Policy Threshold: <= {MAX_IMAGE_SIZE_MB} MB)")
print(f"  * Layer Waste Ratio     : {wasted_pct:.2f}% (Policy Threshold: <= {MAX_WASTED_PERCENT}%)")
print(f"  * Critical CVEs         : {critical_cves} (Policy Threshold: == 0)")
print(f"  * High CVEs             : {high_cves} (Policy Threshold: == 0)")
print("=" * 70)

violations = []

if overall_status != "PASSED":
    violations.append(f"Optimization report status is {overall_status} (must be PASSED)")

if goa_status != "GREEN (PASSED)":
    violations.append(f"Green-on-Arrival Sentinel verification failed with status: {goa_status}")

if size_mb > MAX_IMAGE_SIZE_MB:
    violations.append(f"Image size {size_mb:.2f} MB exceeds policy maximum of {MAX_IMAGE_SIZE_MB} MB")

if wasted_pct > MAX_WASTED_PERCENT:
    violations.append(f"Layer waste {wasted_pct:.2f}% exceeds policy maximum of {MAX_WASTED_PERCENT}%")

if critical_cves > 0:
    violations.append(f"Found {critical_cves} CRITICAL vulnerability/vulnerabilities (zero allowed)")

if high_cves > 0:
    violations.append(f"Found {high_cves} HIGH vulnerability/vulnerabilities (zero allowed)")

if violations:
    print("\\n[POLICY GATE FAILED] PR merge blocked due to governance policy breaches:")
    for v in violations:
        print(f"   [VIOLATION] {v}")
    print("\\nRemediation required: re-run optimization locally or address CVEs before merging.\\n")
    sys.exit(1)

print("\\n[POLICY GATE PASSED] All enterprise security, size, and bloat policies verified.\\n")
"""


def run_policy_gate(report_path: str):
    """Helper to run the embedded governance script against a target report file."""
    proc = subprocess.run(
        [sys.executable, "-c", GOVERNANCE_SCRIPT, report_path],
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    return proc


def make_report(status="PASSED", goa="GREEN (PASSED)", size_mb=250.0, wasted_pct=5.0, crit_cve=0, high_cve=0):
    return {
        "project": "enterprise-test-service",
        "timestamp": "2026-11-02T12:00:00Z",
        "status": status,
        "baseline": {
            "uncompressed_size_mb": 500.0,
            "compressed_size_mb": 180.0,
            "layer_count": 22,
            "wasted_percent": 25.0,
            "build_time_seconds": 15.0,
            "cve_summary": {"CRITICAL": 3, "HIGH": 5}
        },
        "optimized": {
            "uncompressed_size_mb": size_mb,
            "compressed_size_mb": 80.0,
            "layer_count": 7,
            "wasted_percent": wasted_pct,
            "build_time_seconds": 4.2,
            "cve_summary": {"CRITICAL": crit_cve, "HIGH": high_cve}
        },
        "goa_verification": {
            "overall_status": goa
        }
    }


def test_policy_gate_standard_passing(tmp_path):
    """Verify that a compliant report cleanly passes the policy gate with code 0."""
    rep_file = tmp_path / "report.json"
    rep_file.write_text(json.dumps(make_report()), encoding="utf-8")

    proc = run_policy_gate(str(rep_file))
    assert proc.returncode == 0
    assert "[POLICY GATE PASSED]" in proc.stdout
    assert "All enterprise security, size, and bloat policies verified" in proc.stdout


def test_policy_gate_critical_cves_rejection(tmp_path):
    """Verify that Critical CVEs > 0 fails policy gate with code 1."""
    rep_file = tmp_path / "report.json"
    rep_file.write_text(json.dumps(make_report(crit_cve=1)), encoding="utf-8")

    proc = run_policy_gate(str(rep_file))
    assert proc.returncode == 1
    assert "[POLICY GATE FAILED]" in proc.stdout
    assert "CRITICAL vulnerability/vulnerabilities (zero allowed)" in proc.stdout


def test_policy_gate_high_cves_rejection(tmp_path):
    """Verify that High CVEs > 0 fails policy gate with code 1."""
    rep_file = tmp_path / "report.json"
    rep_file.write_text(json.dumps(make_report(high_cve=3)), encoding="utf-8")

    proc = run_policy_gate(str(rep_file))
    assert proc.returncode == 1
    assert "[POLICY GATE FAILED]" in proc.stdout
    assert "HIGH vulnerability/vulnerabilities (zero allowed)" in proc.stdout


def test_policy_gate_excessive_waste_rejection(tmp_path):
    """Verify that wasted_percent > 10.0 fails policy gate with code 1."""
    rep_file = tmp_path / "report.json"
    rep_file.write_text(json.dumps(make_report(wasted_pct=10.1)), encoding="utf-8")

    proc = run_policy_gate(str(rep_file))
    assert proc.returncode == 1
    assert "[POLICY GATE FAILED]" in proc.stdout
    assert "Layer waste 10.10% exceeds policy maximum of 10.0%" in proc.stdout


def test_policy_gate_excessive_size_rejection(tmp_path):
    """Verify that image size > 350.0 MB fails policy gate with code 1."""
    rep_file = tmp_path / "report.json"
    rep_file.write_text(json.dumps(make_report(size_mb=350.5)), encoding="utf-8")

    proc = run_policy_gate(str(rep_file))
    assert proc.returncode == 1
    assert "[POLICY GATE FAILED]" in proc.stdout
    assert "Image size 350.50 MB exceeds policy maximum of 350.0 MB" in proc.stdout


def test_policy_gate_goa_failure_rejection(tmp_path):
    """Verify that GoA status != 'GREEN (PASSED)' fails policy gate with code 1."""
    rep_file = tmp_path / "report.json"
    rep_file.write_text(json.dumps(make_report(goa="RED (FAILED)")), encoding="utf-8")

    proc = run_policy_gate(str(rep_file))
    assert proc.returncode == 1
    assert "[POLICY GATE FAILED]" in proc.stdout
    assert "Green-on-Arrival Sentinel verification failed with status: RED (FAILED)" in proc.stdout


def test_policy_gate_overall_status_failure_rejection(tmp_path):
    """Verify that report overall status != 'PASSED' fails policy gate with code 1."""
    rep_file = tmp_path / "report.json"
    rep_file.write_text(json.dumps(make_report(status="FAILED")), encoding="utf-8")

    proc = run_policy_gate(str(rep_file))
    assert proc.returncode == 1
    assert "[POLICY GATE FAILED]" in proc.stdout
    assert "Optimization report status is FAILED (must be PASSED)" in proc.stdout


def test_policy_gate_boundary_exact_limits(tmp_path):
    """Verify that exact threshold boundaries (350.0 MB, 10.0% waste, 0 CVEs) pass cleanly."""
    rep_file = tmp_path / "report.json"
    rep_file.write_text(json.dumps(make_report(size_mb=350.0, wasted_pct=10.0, crit_cve=0, high_cve=0)), encoding="utf-8")

    proc = run_policy_gate(str(rep_file))
    assert proc.returncode == 0
    assert "[POLICY GATE PASSED]" in proc.stdout


def test_policy_gate_missing_file_fatality(tmp_path):
    """Verify that missing report file exits with code 1 and fatal message."""
    missing = tmp_path / "non_existent_report.json"
    proc = run_policy_gate(str(missing))
    assert proc.returncode == 1
    assert "[FATAL] Could not read governance report" in proc.stdout


def test_policy_gate_corrupted_json_fatality(tmp_path):
    """Verify that malformed JSON in report file exits with code 1 and fatal message."""
    bad_json = tmp_path / "corrupted.json"
    bad_json.write_text("{ this is not valid json :", encoding="utf-8")

    proc = run_policy_gate(str(bad_json))
    assert proc.returncode == 1
    assert "[FATAL] Could not read governance report" in proc.stdout


def test_policy_gate_multiple_violations_reported(tmp_path):
    """Verify that when multiple policies fail, all violations are enumerated."""
    rep_file = tmp_path / "report.json"
    rep_file.write_text(json.dumps(make_report(
        size_mb=400.0,
        wasted_pct=15.0,
        crit_cve=2,
        high_cve=4,
        goa="RED (FAILED)",
        status="FAILED"
    )), encoding="utf-8")

    proc = run_policy_gate(str(rep_file))
    assert proc.returncode == 1
    assert "[POLICY GATE FAILED]" in proc.stdout
    assert "CRITICAL vulnerability" in proc.stdout
    assert "HIGH vulnerability" in proc.stdout
    assert "Image size 400.00 MB exceeds" in proc.stdout
    assert "Layer waste 15.00% exceeds" in proc.stdout
    assert "Green-on-Arrival Sentinel verification failed" in proc.stdout
    assert "Optimization report status is FAILED" in proc.stdout


# ==============================================================================
# 5. ENTERPRISE TERMINOLOGY COMPLIANCE VERIFICATION
# ==============================================================================

def test_enterprise_terminology_compliance():
    """Verify zero prohibited enterprise terms appear in codebase."""
    prohibited_term = "M" + "O" + "S" + "I" + "P"
    targets = [
        Path("rover_slim/cli.py"),
        Path("rover_slim/synthesizers/decoupling.py"),
        Path(".github/workflows/container-governance.yml"),
        Path("tests/test_cli_commands_extended.py"),
    ]
    for target in targets:
        if target.exists():
            content = target.read_text(encoding="utf-8")
            assert prohibited_term.lower() not in content.lower(), f"Prohibited enterprise term found in {target}!"
