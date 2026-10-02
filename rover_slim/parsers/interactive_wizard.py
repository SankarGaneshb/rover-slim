import os
import yaml
from typing import List, Dict, Tuple, Optional
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rover_slim.parsers.req_parser import RequirementEntry
from rover_slim.models import PrunedPackage

class InteractiveWizard:
    """Provides an interactive terminal wizard for reviewing and overriding dependency segregation."""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()

    def review_segregation(
        self,
        prod_entries: List[RequirementEntry],
        dev_entries: List[RequirementEntry],
        pruned_packages: List[PrunedPackage]
    ) -> Tuple[List[RequirementEntry], List[RequirementEntry], List[PrunedPackage]]:
        self.console.print("\n[bold cyan]🔍 Rover-Slim Interactive Dependency Review[/bold cyan]")
        
        table = Table(title="Proposed Dependency Classification", header_style="bold magenta")
        table.add_column("Package", style="bold white")
        table.add_column("Proposed Target", style="yellow")
        table.add_column("Reasoning", style="dim")

        for p in prod_entries:
            table.add_row(p.raw_line, "[green]Production[/green]", "Imported in production code")
        for d in dev_entries:
            table.add_row(d.raw_line, "[yellow]Development/Test[/yellow]", "Unreferenced / Dev tool")

        self.console.print(table)

        reclassified_prod = list(prod_entries)
        reclassified_dev = list(dev_entries)
        reclassified_pruned = list(pruned_packages)

        prompt_msg = "\nWould you like to move any Development package back to Production? (Enter package names comma-separated, or 'none')"
        ans = Prompt.ask(prompt_msg, default="none")

        if ans.lower() != "none" and ans.strip():
            pkgs_to_move = [p.strip().lower() for p in ans.split(",") if p.strip()]
            for p_name in pkgs_to_move:
                entry = next((e for e in reclassified_dev if e.normalized_name == p_name or e.name.lower() == p_name), None)
                if entry:
                    reclassified_dev.remove(entry)
                    reclassified_prod.append(entry)
                    reclassified_pruned = [p for p in reclassified_pruned if p.package != entry.raw_line]
                    self.console.print(f"  [green]✔ Moved '{entry.name}' to Production[/green]")

        return reclassified_prod, reclassified_dev, reclassified_pruned
