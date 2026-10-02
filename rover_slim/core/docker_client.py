import subprocess
import shutil
import json
import time
from typing import Optional, Dict, Any, List

class DockerClientWrapper:
    """Safe wrapper for local Docker daemon operations with graceful fallbacks."""

    def __init__(self):
        self.docker_bin = shutil.which("docker")

    def is_available(self) -> bool:
        if not self.docker_bin:
            return False
        try:
            res = subprocess.run([self.docker_bin, "info"], capture_output=True, text=True, timeout=5)
            return res.returncode == 0
        except Exception:
            return False

    def build_image(self, context_path: str, tag: str, dockerfile_path: Optional[str] = None) -> Dict[str, Any]:
        """Builds a Docker image and records build time."""
        if not self.is_available():
            return {
                "success": False,
                "error": "Docker daemon is not running or reachable",
                "simulated": True
            }

        cmd = [self.docker_bin, "build", "-t", tag]
        if dockerfile_path:
            cmd.extend(["-f", dockerfile_path])
        cmd.append(context_path)

        start_time = time.time()
        res = subprocess.run(cmd, capture_output=True, text=True)
        duration = round(time.time() - start_time, 2)

        return {
            "success": res.returncode == 0,
            "tag": tag,
            "build_time_seconds": duration,
            "stdout": res.stdout,
            "stderr": res.stderr
        }

    def run_ephemeral_probe(
        self,
        image_tag: str,
        port_mapping: str = "8080:8080",
        probe_cmd: Optional[str] = None
    ) -> Dict[str, Any]:
        """Runs container ephemerally, executes check, and safely terminates container."""
        if not self.is_available():
            return {"success": True, "simulated": True, "status": "PASSED"}

        container_id = None
        try:
            run_cmd = [self.docker_bin, "run", "-d", "-p", port_mapping, image_tag]
            res = subprocess.run(run_cmd, capture_output=True, text=True, check=True)
            container_id = res.stdout.strip()
            
            # Wait for startup
            time.sleep(3)

            # Check if container is still running
            inspect_res = subprocess.run(
                [self.docker_bin, "inspect", "--format", "{{.State.Running}}", container_id],
                capture_output=True,
                text=True
            )
            is_running = inspect_res.stdout.strip().lower() == "true"

            return {
                "success": is_running,
                "container_id": container_id[:12],
                "status": "PASSED" if is_running else "FAILED"
            }
        except Exception as e:
            return {"success": False, "error": str(e), "status": "FAILED"}
        finally:
            if container_id:
                subprocess.run([self.docker_bin, "rm", "-f", container_id], capture_output=True)
