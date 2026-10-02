import os
from typing import Optional, Dict, Any, List
from jinja2 import Environment, FileSystemLoader, select_autoescape
from rover_slim.models import RoverSlimConfig

class MultiArchSynthesizer:
    """Generates cross-platform Dockerfiles and Docker Buildx scripts for multi-architecture deployment."""

    def __init__(self, config: Optional[RoverSlimConfig] = None):
        self.config = config or RoverSlimConfig(project_name="rover-slim-multiarch")
        template_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html", "xml"])
        )

    def synthesize(
        self,
        platforms: Optional[List[str]] = None,
        port: int = 8080,
        cmd: Optional[str] = None
    ) -> str:
        """Renders the multi-platform Buildx Dockerfile."""
        target_base = self.config.build.target_base_image
        template = self.env.get_template("multiarch_slim.dockerfile.j2")
        rendered = template.render(
            target_base_image=target_base,
            port=port,
            cmd=cmd
        )
        return rendered

    def generate_buildx_command(
        self,
        image_tag: str,
        platforms: Optional[List[str]] = None,
        push: bool = False
    ) -> str:
        """Generates the recommended CLI command for building multi-arch images."""
        plat_str = ",".join(platforms or ["linux/amd64", "linux/arm64"])
        action = "--push" if push else "--load"
        return f"docker buildx build --platform {plat_str} -t {image_tag} {action} ."

    def write_dockerfile(self, output_path: str, port: int = 8080, cmd: Optional[str] = None) -> str:
        content = self.synthesize(port=port, cmd=cmd)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return output_path
