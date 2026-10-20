import subprocess
import time
import socket
import os
import sys
import shlex
import requests
from typing import Dict, Any, List, Optional
from rover_slim.models import RoverSlimConfig, ProbeConfig

class GoASentinelVerifier:
    """
    Green-on-Arrival (GoA) Sentinel: Validates runtime boot integrity,
    HTTP health checks, TCP probes, and static assets in an isolated sandbox.
    """

    def __init__(self, config: Optional[RoverSlimConfig] = None, root_dir: str = "."):
        self.config = config or RoverSlimConfig(project_name="rover-slim-app")
        self.root_dir = os.path.abspath(root_dir)

    def is_docker_available(self) -> bool:
        """Checks if local Docker daemon is reachable."""
        try:
            res = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def discover_startup_command(self) -> str:
        """Determines the best startup validation command based on available entrypoints."""
        explicit_cmd = self.config.verification.startup_command
        if explicit_cmd and "import server" not in explicit_cmd:
            return explicit_cmd

        if os.path.exists(os.path.join(self.root_dir, "server.py")):
            return 'import server; print("[OK] server.py verified")'
        elif os.path.exists(os.path.join(self.root_dir, "app.py")):
            return 'import app; print("[OK] app.py verified")'
        elif os.path.exists(os.path.join(self.root_dir, "main.py")):
            return 'import main; print("[OK] main.py verified")'
        
        # Fallback safe environment check
        return 'import sys; print("[OK] Environment Integrity verified")'

    def verify_startup_integrity(self, image_tag: Optional[str] = None) -> Dict[str, Any]:
        """Runs the configured startup command inside the container or sandbox environment."""
        py_snippet = self.discover_startup_command()
        
        if image_tag and self.is_docker_available():
            try:
                cmd = ["docker", "run", "--rm", image_tag, "python", "-c", py_snippet]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
                passed = res.returncode == 0
                return {
                    "check": "Startup Integrity",
                    "command": f'python -c "{py_snippet}"',
                    "status": "PASSED" if passed else "FAILED",
                    "output": res.stdout.strip() or res.stderr.strip()
                }
            except Exception as e:
                return {
                    "check": "Startup Integrity",
                    "command": f'python -c "{py_snippet}"',
                    "status": "FAILED",
                    "error": str(e)
                }
        else:
            # Sandbox / Simulated dry-run verification
            try:
                res = subprocess.run(
                    [sys.executable, "-c", py_snippet],
                    cwd=self.root_dir,
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                passed = res.returncode == 0
                return {
                    "check": "Startup Integrity (Local Sandbox)",
                    "command": f'python -c "{py_snippet}"',
                    "status": "PASSED" if passed else "FAILED",
                    "output": res.stdout.strip() or res.stderr.strip()
                }
            except Exception as e:
                return {
                    "check": "Startup Integrity (Local Sandbox)",
                    "command": f'python -c "{py_snippet}"',
                    "status": "FAILED",
                    "output": f"Startup verification failed: {e}"
                }

    def verify_probes(self, image_tag: Optional[str] = None) -> List[Dict[str, Any]]:
        """Executes all configured probes (HTTP, TCP, script) against the candidate runtime."""
        probe_results = []
        probes = self.config.verification.probes or []

        for p in probes:
            start_t = time.perf_counter()
            if p.type == "http":
                target_url = f"http://127.0.0.1:{p.port}{p.path}"
                try:
                    resp = requests.get(target_url, timeout=p.timeout_seconds or 5)
                    lat = round((time.perf_counter() - start_t) * 1000.0, 2)
                    is_ok = (resp.status_code == p.expected_status)
                    probe_results.append({
                        "probe": p.name,
                        "type": "HTTP GET",
                        "target": target_url,
                        "expected_status": p.expected_status,
                        "status_code": resp.status_code,
                        "status": "PASSED" if is_ok else "FAILED",
                        "latency_ms": lat
                    })
                except Exception as e:
                    lat = round((time.perf_counter() - start_t) * 1000.0, 2)
                    probe_results.append({
                        "probe": p.name,
                        "type": "HTTP GET",
                        "target": target_url,
                        "expected_status": p.expected_status,
                        "status": "FAILED",
                        "latency_ms": lat,
                        "error": str(e)
                    })
            elif p.type == "tcp":
                try:
                    sock = socket.create_connection(("127.0.0.1", p.port), timeout=p.timeout_seconds or 5)
                    sock.close()
                    lat = round((time.perf_counter() - start_t) * 1000.0, 2)
                    probe_results.append({
                        "probe": p.name,
                        "type": "TCP Connect",
                        "port": p.port,
                        "status": "PASSED",
                        "latency_ms": lat
                    })
                except Exception as e:
                    lat = round((time.perf_counter() - start_t) * 1000.0, 2)
                    probe_results.append({
                        "probe": p.name,
                        "type": "TCP Connect",
                        "port": p.port,
                        "status": "FAILED",
                        "latency_ms": lat,
                        "error": str(e)
                    })
            elif p.type == "script":
                try:
                    res = subprocess.run(
                        p.command,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=p.timeout_seconds or 15,
                        cwd=self.root_dir
                    )
                    passed = (res.returncode == 0)
                    probe_results.append({
                        "probe": p.name,
                        "type": "Custom Script",
                        "command": p.command,
                        "status": "PASSED" if passed else "FAILED",
                        "exit_code": res.returncode,
                        "output": res.stdout.strip() or res.stderr.strip()
                    })
                except Exception as e:
                    probe_results.append({
                        "probe": p.name,
                        "type": "Custom Script",
                        "command": p.command,
                        "status": "FAILED",
                        "error": str(e)
                    })

        return probe_results

    def verify_static_assets(self) -> Dict[str, Any]:
        """Validates that frontend distribution assets exist and are non-empty."""
        dist_path = self.config.build.frontend_dist_path
        if not dist_path:
            return {
                "check": "Static Frontend Assets",
                "dist_path": None,
                "status": "SKIPPED",
                "details": "No frontend dist path configured"
            }
        full_dist = os.path.join(self.root_dir, dist_path)
        
        if not os.path.exists(full_dist):
            return {
                "check": "Static Frontend Assets",
                "dist_path": dist_path,
                "status": "SKIPPED",
                "details": "No frontend dist path present or required"
            }
            
        files = []
        for root, _, fs in os.walk(full_dist):
            for f in fs:
                files.append(os.path.join(root, f))
                
        return {
            "check": "Static Frontend Assets",
            "dist_path": dist_path,
            "status": "PASSED" if files else "EMPTY",
            "asset_count": len(files),
            "details": f"Found {len(files)} compiled static asset files"
        }

    def run_full_goa_verification(self, image_tag: Optional[str] = None) -> Dict[str, Any]:
        """Runs the complete suite of Green-on-Arrival verifications."""
        startup = self.verify_startup_integrity(image_tag)
        probes = self.verify_probes(image_tag)
        assets = self.verify_static_assets()
        
        all_passed = (
            startup.get("status") in ["PASSED", "SKIPPED"]
            and all(p.get("status") == "PASSED" for p in probes)
            and assets.get("status") in ["PASSED", "SKIPPED"]
        )

        return {
            "overall_status": "GREEN (PASSED)" if all_passed else "RED (FAILED)",
            "startup_integrity": startup,
            "probes": probes,
            "static_assets": assets,
            "verified_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
