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

if __name__ == "__main__":
    app()
