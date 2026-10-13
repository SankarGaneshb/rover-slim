import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
from rover_slim.core.engine import RoverSlimEngine

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
                else:
                    res = f"Unknown tool: {tool_name}"
                
                resp = {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": res}]}}
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
        except Exception as e:
            sys.stderr.write(f"Error handling request: {e}\n")

if __name__ == "__main__":
    run_mcp_server()
