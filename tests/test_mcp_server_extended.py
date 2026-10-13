import pytest
import json
import io
import sys
try:
    import pydantic.root_model
except ImportError:
    pass
from unittest.mock import MagicMock, patch
from rover_slim.mcp_server import run_mcp_server, _run_fallback_jsonrpc

def test_mcp_server_fastmcp_run(monkeypatch):
    mock_fastmcp_cls = MagicMock()
    mock_instance = MagicMock()
    mock_fastmcp_cls.return_value = mock_instance
    captured_annotations = []
    
    # Mock decorator behavior
    def mock_tool(*args, **kwargs):
        if "annotations" in kwargs:
            captured_annotations.append(kwargs["kwargs"]["annotations"] if "kwargs" in kwargs else kwargs["annotations"])
        def decorator(fn):
            # execute the tool function to test its logic
            try:
                fn()
            except Exception:
                pass
            return fn
        return decorator
    
    mock_instance.tool = mock_tool
    
    with patch.dict("sys.modules", {
        "mcp.server.fastmcp": MagicMock(FastMCP=mock_fastmcp_cls),
        "mcp.types": MagicMock(ToolAnnotations=lambda **kw: kw),
    }):
        run_mcp_server()
        assert mock_instance.run.called
        assert len(captured_annotations) == 4

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
    tools = tool_list_resp["result"]["tools"]
    assert len(tools) == 4
    for tool in tools:
        assert "annotations" in tool
        for hint in ["readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint"]:
            assert isinstance(tool["annotations"][hint], bool)
    
    # Check unknown tool response
    unknown_tool_resp = json.loads(output_lines[5])
    assert "Unknown tool" in unknown_tool_resp["result"]["content"][0]["text"]

def test_fastmcp_real_tool_annotations():
    try:
        from mcp.server.fastmcp import FastMCP
        from mcp.types import ToolAnnotations
    except ImportError:
        pytest.skip("mcp package not installed")

    import asyncio
    from rover_slim.mcp_server import TOOL_ANNOTATIONS

    mcp = FastMCP("rover-slim-test")

    for name, hints in TOOL_ANNOTATIONS.items():
        ann = ToolAnnotations(**hints)
        def _dummy():
            return "ok"
        _dummy.__name__ = name
        mcp.tool(name=name, annotations=ann)(_dummy)

    tools = asyncio.run(mcp.list_tools())
    assert len(tools) == 4
    for t in tools:
        assert t.annotations is not None
        assert isinstance(t.annotations.readOnlyHint, bool)
        assert isinstance(t.annotations.destructiveHint, bool)
        assert isinstance(t.annotations.idempotentHint, bool)
        assert isinstance(t.annotations.openWorldHint, bool)
    
    by_name = {t.name: t.annotations for t in tools}
    assert by_name["audit_container"].readOnlyHint is True
    assert by_name["audit_container"].destructiveHint is False
    assert by_name["optimize_project"].readOnlyHint is False
    assert by_name["optimize_project"].destructiveHint is True
    assert by_name["verify_goa"].readOnlyHint is True
    assert by_name["get_markdown_report"].readOnlyHint is True
