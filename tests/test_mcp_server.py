import io
import sys
import json
from rover_slim.mcp_server import _run_fallback_jsonrpc

def test_mcp_fallback_jsonrpc_list_and_call(monkeypatch):
    req_list = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}})
    req_audit = json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "audit_container", "arguments": {"project_path": "."}}})
    input_data = f"{req_list}\n{req_audit}\n"

    fake_stdin = io.StringIO(input_data)
    fake_stdout = io.StringIO()
    fake_stderr = io.StringIO()

    monkeypatch.setattr(sys, "stdin", fake_stdin)
    monkeypatch.setattr(sys, "stdout", fake_stdout)
    monkeypatch.setattr(sys, "stderr", fake_stderr)

    _run_fallback_jsonrpc()

    output_lines = [json.loads(line) for line in fake_stdout.getvalue().splitlines() if line.strip()]
    assert len(output_lines) == 2
    assert "tools" in output_lines[0]["result"]
    assert len(output_lines[0]["result"]["tools"]) == 4
    assert output_lines[1]["result"]["content"][0]["type"] == "text"
