import os
import time
import threading
from typing import Dict, Optional, Callable, Set
from rich.console import Console
from rover_slim.parsers.req_parser import RequirementsParser
from rover_slim.parsers.ast_parser import ASTDependencyParser

class ProjectWatcher:
    """Monitors repository Python and requirements files and dynamically synchronizes dependencies."""

    def __init__(self, root_dir: str = ".", poll_interval: float = 1.0, console: Optional[Console] = None):
        self.root_dir = os.path.abspath(root_dir)
        self.poll_interval = poll_interval
        self.console = console or Console()
        self.req_parser = RequirementsParser(self.root_dir)
        self.ast_parser = ASTDependencyParser(self.root_dir)
        self._is_running = False
        self._file_mtimes: Dict[str, float] = {}

    def _get_tracked_files(self) -> Dict[str, float]:
        """Collects all .py and requirements files with their modification timestamps."""
        tracked = {}
        # Ignored files that should NEVER trigger watcher cycles
        ignored_files = {
            "requirements-prod.txt",
            "requirements-dev.txt",
            "Dockerfile",
            ".dockerignore",
            "metadata.json"
        }
        for root, dirs, files in os.walk(self.root_dir, followlinks=False):
            dirs[:] = [
                d for d in dirs
                if not d.startswith(".") and d not in [
                    "venv", ".venv", "env", ".env", "tests", "test",
                    "node_modules", "build", "dist", "scratch", ".rover-slim", ".pytest_cache"
                ]
            ]
            for f in files:
                if f in ignored_files or f.startswith("."):
                    continue
                if f.endswith(".py") or f in ["requirements.txt", ".rover-slim.yaml"]:
                    full_path = os.path.join(root, f)
                    try:
                        tracked[full_path] = os.path.getmtime(full_path)
                    except OSError:
                        pass
        return tracked

    def sync_once(self) -> bool:
        """Runs a single AST scan and updates requirements-prod.txt if imports changed."""
        try:
            prod_reqs, dev_reqs, pruned = self.req_parser.segregate_dependencies()
            prod_path, dev_path = self.req_parser.write_segregated_files(prod_reqs, dev_reqs)
            return True
        except Exception as e:
            self.console.print(f"[yellow]⚠️ Warning during AST sync: {e}[/yellow]")
            return False

    def start_watch(self, callback: Optional[Callable[[], None]] = None):
        """Starts the blocking file watch loop with error resilience and anti-spin backoff."""
        self._is_running = True
        self._file_mtimes = self._get_tracked_files()
        self.console.print(f"[bold green]👀 Rover-Slim Watcher active on '{self.root_dir}'[/bold green]")
        self.console.print("[dim]Press Ctrl+C to stop watching.[/dim]\n")

        # Initial safe synchronization
        self.sync_once()

        consecutive_errors = 0
        try:
            while self._is_running:
                try:
                    time.sleep(self.poll_interval)
                    current_files = self._get_tracked_files()

                    # Detect modified, added, or deleted files
                    changed = False
                    if set(current_files.keys()) != set(self._file_mtimes.keys()):
                        changed = True
                    else:
                        for path, mtime in current_files.items():
                            if mtime > self._file_mtimes.get(path, 0):
                                changed = True
                                break

                    if changed:
                        self._file_mtimes = current_files
                        t_str = time.strftime("%H:%M:%S")
                        self.console.print(f"[{t_str}] [cyan]Change detected[/cyan] -> Re-evaluating AST dependencies...")
                        success = self.sync_once()
                        if success:
                            self.console.print(f"[{t_str}] [bold green]✔ requirements-prod.txt synchronized[/bold green]")
                            consecutive_errors = 0
                        else:
                            consecutive_errors += 1
                        if callback:
                            try:
                                callback()
                            except Exception:
                                pass
                except Exception as loop_err:
                    consecutive_errors += 1
                    backoff = min(10.0, self.poll_interval * (1.5 ** consecutive_errors))
                    self.console.print(f"[dim yellow]Watcher transient error (backing off {backoff:.1f}s): {loop_err}[/dim yellow]")
                    time.sleep(backoff)
        except KeyboardInterrupt:
            self.stop()
            self.console.print("\n[yellow]Rover-Slim Watcher stopped.[/yellow]")

    def stop(self):
        self._is_running = False
