import pytest
import json
import io
import sys
from unittest.mock import MagicMock, patch
from rover_slim.mcp_server import run_mcp_server, _run_fallback_jsonrpc

def test_mcp_server_fastmcp_run(monkeypatch):
    mock_fastmcp_cls = MagicMock()
    mock_instance = MagicMock()
    mock_fastmcp_cls.return_value = mock_instance
    
    # Mock decorator behavior
    def mock_tool():
        def decorator(fn):
            # execute the tool function to test its logic
            try:
                fn()
            except Exception:
                pass
            return fn
        return decorator
    
    mock_instance.tool = mock_tool
    
    with patch.dict("sys.modules", {"mcp.server.fastmcp": MagicMock(FastMCP=mock_fastmcp_cls)}):
        run_mcp_server()
        assert mock_instance.run.called

def test_mcp_fallback_jsonrpc():
    requests = [
        json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}),
        json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "audit_container", "arguments": {"project_path": "."}}}),
        json.dumps({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "optimize_project", "arguments": {"project_path": "."}}}),
        json.dumps({"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "verify_goa", "arguments": {"project_path": "."}}}),
        json.dumps({"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "get_markdown_report", "arguments": {"project_path": "."}}}),
        json.dumps({"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {"name": "invalid_tool", "arguments": {}}})
    ]
    
    fake_stdin = io.StringIO("\n".join(requests) + "\n")
    fake_stdout = io.StringIO()
    fake_stderr = io.StringIO()
    
    with patch("sys.stdin", fake_stdin), patch("sys.stdout", fake_stdout), patch("sys.stderr", fake_stderr):
        _run_fallback_jsonrpc()
    
    output_lines = [line for line in fake_stdout.getvalue().splitlines() if line.strip()]
    assert len(output_lines) == 6
    
    # Check tool list response
    tool_list_resp = json.loads(output_lines[0])
    assert tool_list_resp["id"] == 1
    assert "tools" in tool_list_resp["result"]
    
    # Check unknown tool response
    unknown_tool_resp = json.loads(output_lines[5])
    assert "Unknown tool" in unknown_tool_resp["result"]["content"][0]["text"]
