import asyncio
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional
from rover_slim.core.engine import RoverSlimEngine
from rover_slim.synthesizers.decoupling import (
    DecouplingSynthesizer,
    AssetSpec,
    OrasConfig,
)

TOOL_ANNOTATIONS: Dict[str, Dict[str, bool]] = {
    "audit_container": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    "optimize_project": {
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    "verify_goa": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    "get_markdown_report": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    "decouple_project": {
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
}

def run_mcp_server():
    """Starts the Rover-Slim Model Context Protocol (MCP) server over stdin/stdout JSON-RPC."""
    try:
        from mcp.server.fastmcp import FastMCP
        from mcp.types import ToolAnnotations
    except ImportError:
        # Fallback lightweight JSON-RPC loop if mcp package is missing
        _run_fallback_jsonrpc()
        return

    mcp = FastMCP("rover-slim")

    @mcp.tool(annotations=ToolAnnotations(**TOOL_ANNOTATIONS["audit_container"]))
    def audit_container(project_path: str = ".", image_tag: Optional[str] = None) -> str:
        """Audits a project directory or Docker image for bloat, wasted layers, context leakage, and CVEs."""
        engine = RoverSlimEngine(root_dir=project_path)
        report = engine.audit(existing_image=image_tag)
        return report.model_dump_json(indent=2)

    @mcp.tool(annotations=ToolAnnotations(**TOOL_ANNOTATIONS["optimize_project"]))
    def optimize_project(project_path: str = ".", verify_goa: bool = True) -> str:
        """Runs end-to-end container optimization, segregating requirements, writing multi-stage Dockerfile, and verifying GoA."""
        engine = RoverSlimEngine(root_dir=project_path)
        report = engine.optimize(target_dir=project_path, verify_goa=verify_goa)
        return report.model_dump_json(indent=2)

    @mcp.tool(annotations=ToolAnnotations(**TOOL_ANNOTATIONS["verify_goa"]))
    def verify_goa(project_path: str = ".", image_tag: Optional[str] = None) -> str:
        """Runs Green-on-Arrival (GoA) Sentinel runtime boot integrity and probe checks."""
        engine = RoverSlimEngine(root_dir=project_path)
        results = engine.sentinel.run_full_goa_verification(image_tag=image_tag)
        return json.dumps(results, indent=2)

    @mcp.tool(annotations=ToolAnnotations(**TOOL_ANNOTATIONS["get_markdown_report"]))
    def get_markdown_report(project_path: str = ".") -> str:
        """Generates GitHub PR markdown diff summary for the current container optimization state."""
        engine = RoverSlimEngine(root_dir=project_path)
        report = engine.audit()
        return engine.md_reporter.generate_markdown(report)

    @mcp.tool(annotations=ToolAnnotations(**TOOL_ANNOTATIONS["decouple_project"]))
    def decouple_project(
        asset_path: str = "dist",
        mount_path: str = "/app/static",
        remote_artifact_ref: str = "ghcr.io/myorg/assets:latest",
        name: Optional[str] = None,
        workload_type: str = "Deployment",
        target_container: str = "app",
        output_dir: Optional[str] = None,
        plain_http: bool = False,
        insecure: bool = False,
    ) -> str:
        """Synthesizes Cloud-Native Decoupling manifests: Kubernetes Pod/Deployment patch YAML with shared emptyDir volumes and init containers, plus ORAS push/pull scripts."""
        if name:
            asset_name = name
        else:
            raw_base = os.path.basename(os.path.normpath(asset_path)).strip("-._")
            sanitized = re.sub(r"[^a-zA-Z0-9_.-]", "-", raw_base).strip("-")
            asset_name = sanitized if (sanitized and sanitized[0].isalnum()) else "static-assets"

        if not mount_path or not mount_path.startswith("/"):
            return json.dumps({"error": f"Mount path '{mount_path}' must be an absolute Unix path starting with '/'."})

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

        asset = AssetSpec(
            name=asset_name,
            source_path=asset_path,
            mount_path=mount_path,
            remote_artifact_ref=remote_artifact_ref,
            size_mb=size_mb,
        )

        oras_cfg = OrasConfig(plain_http=plain_http, insecure=insecure)
        synth = DecouplingSynthesizer(oras_config=oras_cfg)

        if output_dir:
            manifest_paths = synth.write_manifests(
                output_dir=output_dir,
                assets=[asset],
                target_container_name=target_container,
            )
            return json.dumps({
                "status": "success",
                "written_files": manifest_paths,
                "estimated_savings_mb": size_mb,
            }, indent=2)
        else:
            bundle = synth.generate_decoupling_bundle(
                assets=[asset],
                target_container_name=target_container,
                base_workload_type=workload_type,
            )
            return json.dumps({
                "status": "success",
                "estimated_savings_mb": bundle.estimated_savings_mb,
                "deployment_patch_yaml": bundle.deployment_patch_yaml,
                "pod_patch_yaml": bundle.pod_patch_yaml,
                "oras_push_commands": bundle.oras_push_commands,
                "oras_pull_commands": bundle.oras_pull_commands,
                "dockerfile_pruning_directives": bundle.dockerfile_pruning_directives,
            }, indent=2)

    mcp.run()

def _run_fallback_jsonrpc():
    """Simple stdio loop responding to MCP-like tool execution if FastMCP not present."""
    sys.stderr.write("[Rover-Slim MCP Server running on stdio]\n")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            method = req.get("method")
            req_id = req.get("id")
            params = req.get("params", {})
            
            if method == "tools/list":
                tools = [
                    {
                        "name": "audit_container",
                        "description": "Audits project container metrics and bloat",
                        "annotations": TOOL_ANNOTATIONS["audit_container"],
                    },
                    {
                        "name": "optimize_project",
                        "description": "Performs AST dependency pruning and multi-stage Dockerfile synthesis",
                        "annotations": TOOL_ANNOTATIONS["optimize_project"],
                    },
                    {
                        "name": "verify_goa",
                        "description": "Runs Green-on-Arrival Sentinel runtime probes",
                        "annotations": TOOL_ANNOTATIONS["verify_goa"],
                    },
                    {
                        "name": "get_markdown_report",
                        "description": "Returns PR markdown diff report",
                        "annotations": TOOL_ANNOTATIONS["get_markdown_report"],
                    },
                    {
                        "name": "decouple_project",
                        "description": "Synthesizes Kubernetes emptyDir and ORAS decoupling manifests and scripts",
                        "annotations": TOOL_ANNOTATIONS["decouple_project"],
                    },
                ]
                resp = {"jsonrpc": "2.0", "id": req_id, "result": {"tools": tools}}
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
            elif method == "tools/call":
                tool_name = params.get("name")
                args = params.get("arguments", {})
                path = args.get("project_path", ".")
                engine = RoverSlimEngine(root_dir=path)
                
                if tool_name == "audit_container":
                    res = engine.audit().model_dump_json(indent=2)
                elif tool_name == "optimize_project":
                    res = engine.optimize(target_dir=path).model_dump_json(indent=2)
                elif tool_name == "verify_goa":
                    res = json.dumps(engine.sentinel.run_full_goa_verification(), indent=2)
                elif tool_name == "get_markdown_report":
                    res = engine.md_reporter.generate_markdown(engine.audit())
                elif tool_name == "decouple_project":
                    asset_p = args.get("asset_path", "dist")
                    mount_p = args.get("mount_path", "/app/static")
                    ref_p = args.get("remote_artifact_ref", "ghcr.io/myorg/assets:latest")
                    name_p = args.get("name")
                    out_p = args.get("output_dir")
                    target_c = args.get("target_container", "app")
                    wl_t = args.get("workload_type", "Deployment")

                    raw_base = os.path.basename(os.path.normpath(asset_p)).strip("-._")
                    sanitized = re.sub(r"[^a-zA-Z0-9_.-]", "-", raw_base).strip("-")
                    asset_name = name_p or (sanitized if (sanitized and sanitized[0].isalnum()) else "static-assets")

                    asset = AssetSpec(
                        name=asset_name,
                        source_path=asset_p,
                        mount_path=mount_p,
                        remote_artifact_ref=ref_p,
                        size_mb=0.0,
                    )
                    synth = DecouplingSynthesizer(oras_config=OrasConfig())
                    if out_p:
                        manifests = synth.write_manifests(output_dir=out_p, assets=[asset], target_container_name=target_c)
                        res = json.dumps({"status": "success", "written_files": manifests}, indent=2)
                    else:
                        bundle = synth.generate_decoupling_bundle(assets=[asset], target_container_name=target_c, base_workload_type=wl_t)
                        res = json.dumps({
                            "status": "success",
                            "estimated_savings_mb": bundle.estimated_savings_mb,
                            "deployment_patch_yaml": bundle.deployment_patch_yaml,
                            "pod_patch_yaml": bundle.pod_patch_yaml,
                            "oras_push_commands": bundle.oras_push_commands,
                            "oras_pull_commands": bundle.oras_pull_commands,
                            "dockerfile_pruning_directives": bundle.dockerfile_pruning_directives,
                        }, indent=2)
                else:
                    res = f"Unknown tool: {tool_name}"
                
                resp = {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": res}]}}
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
        except Exception as e:
            sys.stderr.write(f"Error handling request: {e}\n")

if __name__ == "__main__":
    run_mcp_server()
