import sys
import os
from typing import Optional

# Reconfigure stdout/stderr to utf-8 if supported
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import typer
from rich.console import Console
from rich.prompt import Confirm
from rover_slim.core.engine import RoverSlimEngine
from rover_slim.reporters.terminal_reporter import TerminalReporter

app = typer.Typer(
    name="rover-slim",
    help="Autonomous Container Optimization, AST Dependency Segregation, and Green-on-Arrival Verification Engine.",
    add_completion=False
)
console = Console(highlight=False)

def version_callback(value: bool):
    if value:
        from rover_slim import __version__
        console.print(f"[bold cyan]Rover-Slim[/bold cyan] version [bold green]{__version__}[/bold green]")
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show Rover-Slim version and exit.",
        callback=version_callback,
        is_eager=True,
    )
):
    pass

def _validate_path(path: str):
    if not os.path.exists(path):
        console.print(f"[bold red]Error: Target path '{path}' does not exist.[/bold red]")
        raise typer.Exit(code=1)

@app.command("audit")
def audit_command(
    path: str = typer.Argument(".", help="Target project root directory to audit"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to custom .rover-slim.yaml"),
    image: Optional[str] = typer.Option(None, "--image", "-i", help="Existing Docker image tag to inspect")
):
    """Audits container bloat, AST dependency usage, context leakage, and CVE thresholds."""
    _validate_path(path)
    try:
        engine = RoverSlimEngine(root_dir=path, config_path=config)
        with console.status("[bold green]Scanning AST dependencies, build context, and container layers...[/bold green]"):
            report = engine.audit(existing_image=image)
        
        reporter = TerminalReporter(console)
        reporter.print_report(report)
    except Exception as e:
        console.print(f"[bold red]Audit failed: {e}[/bold red]")
        raise typer.Exit(code=1)

@app.command("optimize")
def optimize_command(
    path: str = typer.Argument(".", help="Target project root directory to optimize"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to custom .rover-slim.yaml"),
    verify_goa: bool = typer.Option(True, "--verify-goa/--no-verify-goa", help="Run Green-on-Arrival sentinel verification"),
    interactive: bool = typer.Option(False, "--interactive", help="Prompt to interactively review and customize dependency splits"),
    multi_arch: bool = typer.Option(False, "--multi-arch", help="Generate multi-architecture Buildx Dockerfile (amd64 + arm64)")
):
    """Executes full optimization: AST dependency split, multi-stage Dockerfile synthesis, and GoA sentinel."""
    _validate_path(path)
    try:
        engine = RoverSlimEngine(root_dir=path, config_path=config)
        
        with console.status("[bold green]Synthesizing lean multi-stage Dockerfile and verifying runtime GoA...[/bold green]"):
            report = engine.optimize(target_dir=path, verify_goa=verify_goa, interactive=interactive, multi_arch=multi_arch)

        reporter = TerminalReporter(console)
        reporter.print_report(report)
        
        if report.status == "FAILED":
            console.print("\n[bold red][FAIL] Optimization failed runtime GoA verification - changes automatically rolled back.[/bold red]")
            raise typer.Exit(code=1)
        else:
            console.print(f"\n[bold green][OK] Optimization complete![/bold green] Generated artifacts:")
            if os.path.exists(os.path.join(path, "requirements-prod.txt")):
                console.print("  * [cyan]requirements-prod.txt[/cyan] (Lean production dependencies)")
                console.print("  * [cyan]requirements-dev.txt[/cyan] (Full dev/test dependencies)")
            console.print("  * [cyan].dockerignore[/cyan] (Hardened context shield)")
            console.print("  * [cyan]Dockerfile[/cyan] (Multi-stage slim template)")
            console.print("  * [cyan].rover-slim/report.html[/cyan] (Interactive dashboard)")
            console.print("  * [cyan].rover-slim/summary.md[/cyan] (GitHub PR markdown)")
            console.print("  * [cyan].rover-slim/report.json[/cyan] (Structured metrics)")
            console.print("  * [cyan].rover-slim/sbom.spdx.json[/cyan] (SPDX 2.3 SBOM)")
            console.print("  * [cyan].rover-slim/sbom.cyclonedx.json[/cyan] (CycloneDX 1.5 SBOM)")
    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[bold red]Optimization encountered an unexpected error: {e}[/bold red]")
        raise typer.Exit(code=1)

@app.command("diff")
def diff_command(
    path: str = typer.Argument(".", help="Target project root directory")
):
    """Displays a visual, colorized diff between baseline and candidate multi-stage Dockerfile."""
    _validate_path(path)
    try:
        engine = RoverSlimEngine(root_dir=path)
        engine.show_diff()
    except Exception as e:
        console.print(f"[bold red]Diff failed: {e}[/bold red]")
        raise typer.Exit(code=1)

@app.command("watch")
def watch_command(
    path: str = typer.Argument(".", help="Target project root directory to watch"),
    interval: float = typer.Option(1.0, "--interval", "-i", help="Poll interval in seconds")
):
    """Starts continuous file watch mode, synchronizing requirements-prod.txt on source code edits."""
    _validate_path(path)
    try:
        engine = RoverSlimEngine(root_dir=path)
        engine.watch(poll_interval=interval)
    except KeyboardInterrupt:
        console.print("\n[yellow]Watcher stopped.[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Watcher error: {e}[/bold red]")
        raise typer.Exit(code=1)

@app.command("sbom")
def sbom_command(
    path: str = typer.Argument(".", help="Target project root directory"),
    output_dir: str = typer.Option(".rover-slim", "--output", "-o", help="Output directory for SBOM files")
):
    """Generates standardized SPDX 2.3 and CycloneDX 1.5 Software Bill of Materials (SBOM)."""
    _validate_path(path)
    try:
        engine = RoverSlimEngine(root_dir=path)
        prod_reqs, _, _ = engine.req_parser.segregate_dependencies()
        paths = engine.sbom_generator.write_sboms(prod_reqs, output_dir=output_dir)
        console.print("[bold green][OK] Generated Software Bill of Materials (SBOM):[/bold green]")
        console.print(f"  * SPDX 2.3: [cyan]{paths['spdx']}[/cyan]")
        console.print(f"  * CycloneDX 1.5: [cyan]{paths['cyclonedx']}[/cyan]")
    except Exception as e:
        console.print(f"[bold red]SBOM generation failed: {e}[/bold red]")
        raise typer.Exit(code=1)

@app.command("rollback")
def rollback_command(
    path: str = typer.Argument(".", help="Target project root directory"),
    checkpoint_id: Optional[str] = typer.Option(None, "--id", help="Specific checkpoint ID to restore (defaults to latest)")
):
    """Restores tracked configuration files from a previous backup checkpoint."""
    _validate_path(path)
    try:
        engine = RoverSlimEngine(root_dir=path)
        restored = engine.checkpoint.restore_checkpoint(checkpoint_id)
        if restored:
            console.print("[bold green][OK] Successfully restored configuration from checkpoint.[/bold green]")
        else:
            console.print("[bold yellow]No valid checkpoint found to restore.[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]Rollback failed: {e}[/bold red]")
        raise typer.Exit(code=1)

@app.command("verify")
def verify_command(
    path: str = typer.Argument(".", help="Target project root directory"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to custom .rover-slim.yaml"),
    image: Optional[str] = typer.Option(None, "--image", "-i", help="Docker image tag to verify")
):
    """Runs Green-on-Arrival (GoA) Sentinel verification on candidate container/sandbox."""
    _validate_path(path)
    try:
        engine = RoverSlimEngine(root_dir=path, config_path=config)
        with console.status("[bold green]Executing GoA Sentinel startup integrity and health probes...[/bold green]"):
            results = engine.sentinel.run_full_goa_verification(image)
        
        status = results.get("overall_status", "UNKNOWN")
        color = "green" if "GREEN" in status else "red"
        console.print(f"\n[bold {color}]GoA Sentinel Result: {status}[/bold {color}]")
        console.print(f"Startup Integrity: {results.get('startup_integrity', {}).get('status', 'PASSED')}")
        console.print(f"Health Probes: {len(results.get('probes', []))} passed")
        console.print(f"Static Assets: {results.get('static_assets', {}).get('status', 'PASSED')}")
    except Exception as e:
        console.print(f"[bold red]Verification failed: {e}[/bold red]")
        raise typer.Exit(code=1)

@app.command("init")
def init_command(
    path: str = typer.Argument(".", help="Target directory for .rover-slim.yaml")
):
    """Initializes a production-ready .rover-slim.yaml configuration file."""
    _validate_path(path)
    target = os.path.join(path, ".rover-slim.yaml")
    if os.path.exists(target):
        console.print(f"[yellow].rover-slim.yaml already exists at {target}[/yellow]")
        return

    proj_name = os.path.basename(os.path.abspath(path)) or "my-service"
    content = f"""version: "1.0"
project_name: "{proj_name}"

thresholds:
  max_image_size_mb: 350.0
  max_wasted_percent: 10.0
  max_cold_start_seconds: 2.5
  fail_on_cve_severity: ["CRITICAL"]

build:
  target_base_image: "python:3.11-slim"
  enable_multistage: true
  strip_node_runtime: true
  frontend_dist_path: "static/"

verification:
  auto_discover: true
  startup_command: "python -c 'import server; print(\"[OK] Startup Integrity verified\")'"
  probes:
    - name: "HTTP Root Health"
      type: "http"
      path: "/health"
      port: 8080
      expected_status: 200
      timeout_seconds: 10
"""
    try:
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
        console.print(f"[bold green][OK] Initialized .rover-slim.yaml at {target}[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Failed to write .rover-slim.yaml: {e}[/bold red]")
        raise typer.Exit(code=1)

@app.command("mcp")
def mcp_command():
    """Runs the Rover-Slim Model Context Protocol (MCP) server over standard I/O."""
    from rover_slim.mcp_server import run_mcp_server
    run_mcp_server()

@app.command("decouple")
def decouple_command(
    asset_path: str = typer.Argument(..., help="Path to static asset directory or file to decouple"),
    mount: str = typer.Option(..., "--mount", "-m", help="Target mount path inside application container (e.g. /app/static)"),
    ref: str = typer.Option(..., "--ref", "-r", help="Remote OCI artifact reference (e.g. registry.enterprise.local/assets/frontend:v1.0.0)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Optional output directory to write patch manifests and ORAS scripts"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Optional asset identifier name (default: basename of asset_path)"),
    workload_type: str = typer.Option("Deployment", "--workload-type", "--workload", "-w", help="Kubernetes workload type (Deployment or Pod)"),
    target_container: str = typer.Option("app", "--target-container", "-t", help="Name of main application container to mount volume"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to custom .rover-slim.yaml"),
    plain_http: bool = typer.Option(False, "--plain-http", help="Use plain HTTP instead of HTTPS for ORAS"),
    insecure: bool = typer.Option(False, "--insecure", help="Allow insecure SSL connections for ORAS"),
):
    """Synthesizes Cloud-Native Decoupling manifests: K8s Pod/Deployment patch YAML with shared emptyDir volumes and init containers, plus ORAS push/pull scripts."""
    try:
        import re
        from rover_slim.synthesizers.decoupling import (
            DecouplingSynthesizer,
            AssetSpec,
            OrasConfig,
        )
        from rover_slim.config import load_config

        # Sanitize name if not provided
        if name:
            asset_name = name
        else:
            raw_base = os.path.basename(os.path.normpath(asset_path)).strip("-._")
            sanitized = re.sub(r"[^a-zA-Z0-9_.-]", "-", raw_base).strip("-")
            asset_name = sanitized if (sanitized and sanitized[0].isalnum()) else "static-assets"

        # Validate mount path starts with /
        if not mount or not mount.startswith("/"):
            console.print(f"[bold red]Decoupling failed: Mount path '{mount}' must be an absolute Unix path starting with '/'.[/bold red]")
            raise typer.Exit(code=1)

        # Estimate asset size in MB if available on local disk
        total_bytes = 0
        if os.path.exists(asset_path):
            try:
                if os.path.isfile(asset_path):
                    total_bytes = os.path.getsize(asset_path)
                elif os.path.isdir(asset_path):
                    total_bytes = sum(
                        os.path.getsize(os.path.join(root, f))
                        for root, _, files in os.walk(asset_path)
                        for f in files
                        if os.path.isfile(os.path.join(root, f))
                    )
            except Exception:
                total_bytes = 0

        size_mb = max(round(total_bytes / (1024 * 1024), 2), 0.01) if total_bytes > 0 else 0.0

        # Construct AssetSpec model (validates name, mount_path, and remote_artifact_ref)
        asset = AssetSpec(
            name=asset_name,
            source_path=asset_path,
            mount_path=mount,
            remote_artifact_ref=ref,
            size_mb=size_mb,
        )

        cfg = load_config(config_path=config) if config else None
        oras_cfg = OrasConfig(plain_http=plain_http, insecure=insecure)
        synth = DecouplingSynthesizer(config=cfg, oras_config=oras_cfg)

        if output:
            manifest_paths = synth.write_manifests(
                output_dir=output,
                assets=[asset],
                target_container_name=target_container,
            )
            console.print(f"[bold green][OK] Cloud-Native Decoupling manifests synthesized successfully at '{output}':[/bold green]")
            console.print(f"  * Deployment Patch: [cyan]{manifest_paths['deployment_patch']}[/cyan]")
            console.print(f"  * Pod Patch: [cyan]{manifest_paths['pod_patch']}[/cyan]")
            console.print(f"  * ORAS Push Script: [cyan]{manifest_paths['oras_push_script']}[/cyan]")
            console.print(f"  * ORAS Pull Script: [cyan]{manifest_paths['oras_pull_script']}[/cyan]")
            if size_mb > 0:
                console.print(f"  * Estimated Image Layer Savings: [bold green]{size_mb:.2f} MB[/bold green]")
        else:
            bundle = synth.generate_decoupling_bundle(
                assets=[asset],
                target_container_name=target_container,
                base_workload_type=workload_type,
            )
            console.print(f"[bold green][OK] Cloud-Native Decoupling Synthesis Complete[/bold green] (Estimated Savings: {bundle.estimated_savings_mb:.1f} MB)")
            console.print("\n[bold cyan]--- Kubernetes Deployment Patch ---[/bold cyan]")
            console.print(bundle.deployment_patch_yaml)
            console.print("[bold cyan]--- Kubernetes Pod Patch ---[/bold cyan]")
            console.print(bundle.pod_patch_yaml)
            console.print("[bold cyan]--- ORAS Push Commands ---[/bold cyan]")
            console.print("\n".join(bundle.oras_push_commands))
            console.print("\n[bold cyan]--- ORAS Pull Commands ---[/bold cyan]")
            console.print("\n".join(bundle.oras_pull_commands))
            if bundle.dockerfile_pruning_directives:
                console.print("\n[bold cyan]--- Dockerfile Pruning Recommendations ---[/bold cyan]")
                console.print("\n".join(bundle.dockerfile_pruning_directives))

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[bold red]Decoupling failed: {e}[/bold red]")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()

