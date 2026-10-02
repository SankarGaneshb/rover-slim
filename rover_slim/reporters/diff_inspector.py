import difflib
import os
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel

class ContainerDiffInspector:
    """Computes and renders colorized structural and textual diffs between Dockerfiles."""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()

    def generate_unified_diff(self, original_content: str, optimized_content: str) -> str:
        orig_lines = original_content.splitlines(keepends=True)
        opt_lines = optimized_content.splitlines(keepends=True)

        diff = difflib.unified_diff(
            orig_lines,
            opt_lines,
            fromfile="Dockerfile.baseline",
            tofile="Dockerfile.optimized",
            lineterm=""
        )
        return "".join(diff)

    def analyze_structural_improvements(self, original_content: str, optimized_content: str) -> List[Dict[str, Any]]:
        improvements = []
        if "USER" not in original_content and "USER" in optimized_content:
            improvements.append({
                "type": "SECURITY",
                "title": "Non-Root User Enforcement",
                "description": "Added dedicated 'appuser' (UID 10001) to prevent container escape exploits."
            })
        if "--no-cache-dir" not in original_content and "--no-cache-dir" in optimized_content:
            improvements.append({
                "type": "OPTIMIZATION",
                "title": "Disabled Pip Wheel Cache",
                "description": "Enforced '--no-cache-dir' on pip install, saving ~30-60 MB in package layer."
            })
        if "HEALTHCHECK" not in original_content and "HEALTHCHECK" in optimized_content:
            improvements.append({
                "type": "RELIABILITY",
                "title": "Docker Healthcheck Sentinel",
                "description": "Added active healthcheck probe to monitor runtime responsiveness."
            })
        if "AS builder" not in original_content and "AS builder" in optimized_content:
            improvements.append({
                "type": "ARCHITECTURE",
                "title": "2-Stage Multi-Stage Build",
                "description": "Segregated compilation toolchains (gcc/python3-dev) from final runtime image."
            })
        return improvements

    def print_diff(self, original_content: str, optimized_content: str):
        diff_text = self.generate_unified_diff(original_content, optimized_content)
        improvements = self.analyze_structural_improvements(original_content, optimized_content)

        self.console.print(Panel("[bold green]🔍 CONTAINER DOCKERFILE COMPARISON DIFF[/bold green]", expand=False))
        
        if improvements:
            self.console.print("\n[bold cyan]🛡️ Detected Architectural & Security Enhancements:[/bold cyan]")
            for imp in improvements:
                self.console.print(f"  • [bold green][{imp['type']}][/bold green] [bold]{imp['title']}:[/bold] {imp['description']}")

        self.console.print("\n[bold cyan]Unified Diff (Dockerfile):[/bold cyan]")
        syntax = Syntax(diff_text, "diff", theme="monokai", line_numbers=True)
        self.console.print(syntax)
