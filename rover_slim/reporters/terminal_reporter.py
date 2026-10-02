import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rover_slim.models import OptimizationReport

class TerminalReporter:
    """Renders formatted, colorized CLI reports to standard terminal output."""

    def __init__(self, console: Console = None):
        if console:
            self.console = console
        else:
            if hasattr(sys.stdout, "reconfigure"):
                try:
                    sys.stdout.reconfigure(encoding="utf-8")
                except Exception:
                    pass
            self.console = Console(highlight=False)

    def print_report(self, report: OptimizationReport):
        # Header banner
        reduction_mb = report.baseline.uncompressed_size_mb - report.optimized.uncompressed_size_mb
        reduction_pct = (
            (reduction_mb / report.baseline.uncompressed_size_mb * 100)
            if report.baseline.uncompressed_size_mb > 0
            else 0.0
        )

        title = f"[bold green]ROVER-SLIM OPTIMIZATION REPORT: {report.project.upper()}[/bold green]"
        status_color = "green" if report.status == "PASSED" else "red"
        
        banner_content = (
            f"[bold]Status:[/bold] [{status_color}]{report.status}[/{status_color}] | "
            f"[bold]Timestamp:[/bold] {report.timestamp}\n"
            f"[bold cyan]Total Size Reduction:[/bold cyan] [bold green]-{reduction_mb:.1f} MB (-{reduction_pct:.1f}%)[/bold green]"
        )
        self.console.print(Panel(banner_content, title=title, expand=False))

        # Metrics comparison table
        table = Table(title="Container Metrics Comparison", header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Baseline (Fat/Single-Stage)", justify="right", style="yellow")
        table.add_column("Optimized (Slim Multi-Stage)", justify="right", style="bold green")
        table.add_column("Delta / Savings", justify="right", style="bold cyan")

        table.add_row(
            "Uncompressed Image Size",
            f"{report.baseline.uncompressed_size_mb:.1f} MB",
            f"{report.optimized.uncompressed_size_mb:.1f} MB",
            f"-{reduction_mb:.1f} MB (-{reduction_pct:.1f}%)"
        )
        comp_reduction = report.baseline.compressed_size_mb - report.optimized.compressed_size_mb
        table.add_row(
            "Estimated Registry Transfer Size",
            f"{report.baseline.compressed_size_mb:.1f} MB",
            f"{report.optimized.compressed_size_mb:.1f} MB",
            f"-{comp_reduction:.1f} MB"
        )
        table.add_row(
            "Build Context Size",
            f"{report.baseline.build_context_mb:.1f} MB",
            f"{report.optimized.build_context_mb:.1f} MB",
            f"-{(report.baseline.build_context_mb - report.optimized.build_context_mb):.1f} MB"
        )
        table.add_row(
            "Image Layers",
            str(report.baseline.layer_count),
            str(report.optimized.layer_count),
            f"-{report.baseline.layer_count - report.optimized.layer_count} layers"
        )
        table.add_row(
            "Wasted Space (% of layers)",
            f"{report.baseline.wasted_percent:.1f}% ({report.baseline.wasted_space_mb:.1f} MB)",
            f"{report.optimized.wasted_percent:.1f}% ({report.optimized.wasted_space_mb:.1f} MB)",
            f"-{(report.baseline.wasted_space_mb - report.optimized.wasted_space_mb):.1f} MB"
        )
        table.add_row(
            "Total Installed Packages",
            str(report.baseline.total_packages),
            str(report.optimized.total_packages),
            f"-{report.baseline.total_packages - report.optimized.total_packages} pkgs"
        )
        self.console.print(table)

        # Pruned dependencies breakdown
        if report.pruned_dependencies:
            pruned_table = Table(title="Pruned Dependencies (Moved to Dev/Test)", header_style="bold blue")
            pruned_table.add_column("Package", style="bold white")
            pruned_table.add_column("Action", style="yellow")
            pruned_table.add_column("Reason", style="cyan")
            pruned_table.add_column("Est. Space Saved", justify="right", style="green")

            for p in report.pruned_dependencies:
                pruned_table.add_row(
                    p.package,
                    p.action,
                    p.reason,
                    f"~{p.estimated_size_mb:.1f} MB"
                )
            self.console.print(pruned_table)

        # GoA Sentinel status
        goa_status = report.goa_verification.get("overall_status", "UNKNOWN")
        goa_panel = Panel(
            f"[bold]GoA Sentinel Verification:[/bold] [green]{goa_status}[/green]\n"
            f"[dim]* Startup Integrity: {report.goa_verification.get('startup_integrity', {}).get('status', 'PASSED')}\n"
            f"* Health Probes: {len(report.goa_verification.get('probes', []))} verified\n"
            f"* Static Assets: {report.goa_verification.get('static_assets', {}).get('status', 'PASSED')}[/dim]",
            title="Green-on-Arrival (GoA) Sentinel",
            border_style="green" if "GREEN" in goa_status else "red"
        )
        self.console.print(goa_panel)
