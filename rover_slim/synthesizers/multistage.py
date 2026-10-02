import os
from typing import Optional, Dict, Any
from jinja2 import Environment, FileSystemLoader, select_autoescape
from rover_slim.models import RoverSlimConfig
from rover_slim.parsers.dockerfile_parser import DockerfileParser, DockerfileAnalysis

class MultiStageSynthesizer:
    """Generates deterministic, hardened multi-stage Dockerfiles for lean runtime."""

    def __init__(self, config: Optional[RoverSlimConfig] = None):
        self.config = config or RoverSlimConfig(project_name="rover-slim-app")
        template_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html", "xml"])
        )

    def synthesize(
        self,
        existing_dockerfile_path: Optional[str] = None,
        template_name: str = "python_slim.dockerfile.j2",
        overrides: Optional[Dict[str, Any]] = None
    ) -> str:
        """Renders the optimized multi-stage Dockerfile."""
        overrides = overrides or {}
        analysis = DockerfileAnalysis()
        
        if existing_dockerfile_path and os.path.exists(existing_dockerfile_path):
            parser = DockerfileParser(existing_dockerfile_path)
            analysis = parser.parse()

        port = (
            overrides.get("port")
            or (analysis.exposed_ports[0] if analysis.exposed_ports else 8080)
        )
        
        target_base_image = (
            overrides.get("target_base_image")
            or self.config.build.target_base_image
        )

        frontend_dist = (
            self.config.build.frontend_dist_path
            if self.config.build.strip_node_runtime
            else None
        )

        template = self.env.get_template(template_name)
        rendered = template.render(
            target_base_image=target_base_image,
            port=port,
            frontend_dist_path=frontend_dist,
            cmd=overrides.get("cmd") or analysis.cmd,
            entrypoint=overrides.get("entrypoint") or analysis.entrypoint
        )
        return rendered

    def write_dockerfile(
        self,
        output_path: str,
        existing_dockerfile_path: Optional[str] = None,
        template_name: str = "python_slim.dockerfile.j2",
        overrides: Optional[Dict[str, Any]] = None
    ) -> str:
        """Renders and writes Dockerfile to disk."""
        content = self.synthesize(
            existing_dockerfile_path=existing_dockerfile_path,
            template_name=template_name,
            overrides=overrides
        )
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return output_path
