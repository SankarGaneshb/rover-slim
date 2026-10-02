import pytest
import os
from typer.testing import CliRunner
from unittest.mock import MagicMock, patch
from rover_slim.cli import app
from rover_slim.models import OptimizationReport, ImageMetrics, PrunedPackage

runner = CliRunner()

def test_cli_invalid_path():
    result = runner.invoke(app, ["audit", "/non/existent/path/for/test"])
    assert result.exit_code != 0
    assert "Error: Target path" in result.output

def test_cli_audit_with_image_and_config(tmp_path):
    config_file = tmp_path / ".rover-slim.yaml"
    config_file.write_text("version: '1.0'\nproject_name: 'test-cli'\n", encoding="utf-8")
    
    result = runner.invoke(app, ["audit", str(tmp_path), "--config", str(config_file), "--image", "redis:7-alpine"])
    assert result.exit_code == 0
    assert "ROVER-SLIM OPTIMIZATION REPORT" in result.output

def test_cli_optimize_multiarch_no_goa(tmp_path):
    result = runner.invoke(app, ["optimize", str(tmp_path), "--no-verify-goa", "--multi-arch"])
    assert result.exit_code == 0
    assert "Optimization complete" in result.output

def test_cli_optimize_failed_rollback(tmp_path, monkeypatch):
    mock_report = OptimizationReport(
        project="fail-test",
        timestamp="2026-10-02T12:00:00Z",
        status="FAILED",
        baseline=ImageMetrics(
            uncompressed_size_mb=100.0,
            compressed_size_mb=40.0,
            build_context_mb=10.0,
            build_time_seconds=10.0,
            layer_count=10,
            wasted_space_mb=10.0,
            wasted_percent=10.0,
            total_packages=10,
            cve_summary={}
        ),
        optimized=ImageMetrics(
            uncompressed_size_mb=80.0,
            compressed_size_mb=30.0,
            build_context_mb=2.0,
            build_time_seconds=5.0,
            layer_count=5,
            wasted_space_mb=1.0,
            wasted_percent=1.0,
            total_packages=5,
            cve_summary={}
        ),
        pruned_dependencies=[],
        goa_verification={"overall_status": "RED (FAILED)"}
    )
    
    monkeypatch.setattr("rover_slim.core.engine.RoverSlimEngine.optimize", lambda *args, **kwargs: mock_report)
    result = runner.invoke(app, ["optimize", str(tmp_path)])
    assert result.exit_code == 1
    assert "Optimization failed runtime GoA verification" in result.output

def test_cli_diff_command(tmp_path):
    result = runner.invoke(app, ["diff", str(tmp_path)])
    assert result.exit_code == 0
    assert "CONTAINER DOCKERFILE COMPARISON DIFF" in result.output

def test_cli_sbom_command(tmp_path):
    out_dir = tmp_path / "custom_sbom"
    result = runner.invoke(app, ["sbom", str(tmp_path), "--output", str(out_dir)])
    assert result.exit_code == 0
    assert "Generated Software Bill of Materials" in result.output

def test_cli_rollback_command(tmp_path):
    result = runner.invoke(app, ["rollback", str(tmp_path)])
    assert result.exit_code == 0
    assert "No valid checkpoint" in result.output or "Successfully restored" in result.output

def test_cli_verify_command(tmp_path):
    result = runner.invoke(app, ["verify", str(tmp_path)])
    assert result.exit_code == 0
    assert "GoA Sentinel Result" in result.output

def test_cli_init_command(tmp_path):
    result = runner.invoke(app, ["init", str(tmp_path)])
    assert result.exit_code == 0
    assert "Initialized .rover-slim.yaml" in result.output
    
    result2 = runner.invoke(app, ["init", str(tmp_path)])
    assert result2.exit_code == 0
    assert "already exists" in result2.output

def test_cli_mcp_command(monkeypatch):
    mock_mcp = MagicMock()
    monkeypatch.setattr("rover_slim.mcp_server.run_mcp_server", mock_mcp)
    result = runner.invoke(app, ["mcp"])
    assert result.exit_code == 0
    assert mock_mcp.called

def test_cli_watch_command(tmp_path, monkeypatch):
    # Test keyboard interrupt
    monkeypatch.setattr("rover_slim.core.engine.RoverSlimEngine.watch", MagicMock(side_effect=KeyboardInterrupt()))
    result = runner.invoke(app, ["watch", str(tmp_path)])
    assert result.exit_code == 0
    assert "Watcher stopped" in result.output

    # Test error
    monkeypatch.setattr("rover_slim.core.engine.RoverSlimEngine.watch", MagicMock(side_effect=Exception("Watch error")))
    result2 = runner.invoke(app, ["watch", str(tmp_path)])
    assert result2.exit_code == 1
    assert "Watcher error" in result2.output

def test_cli_error_branches(tmp_path, monkeypatch):
    # Audit error
    monkeypatch.setattr("rover_slim.core.engine.RoverSlimEngine.audit", MagicMock(side_effect=Exception("Audit err")))
    result = runner.invoke(app, ["audit", str(tmp_path)])
    assert result.exit_code == 1
    assert "Audit failed" in result.output

    # Diff error
    monkeypatch.setattr("rover_slim.core.engine.RoverSlimEngine.show_diff", MagicMock(side_effect=Exception("Diff err")))
    result = runner.invoke(app, ["diff", str(tmp_path)])
    assert result.exit_code == 1
    assert "Diff failed" in result.output

    # SBOM error
    monkeypatch.setattr("rover_slim.parsers.req_parser.RequirementsParser.segregate_dependencies", MagicMock(side_effect=Exception("SBOM err")))
    result = runner.invoke(app, ["sbom", str(tmp_path)])
    assert result.exit_code == 1
    assert "SBOM generation failed" in result.output

    # Rollback error
    monkeypatch.setattr("rover_slim.core.checkpoint.CheckpointSentinel.restore_checkpoint", MagicMock(side_effect=Exception("Rollback err")))
    result = runner.invoke(app, ["rollback", str(tmp_path)])
    assert result.exit_code == 1
    assert "Rollback failed" in result.output

    # Verify error
    monkeypatch.setattr("rover_slim.verifiers.goa_sentinel.GoASentinelVerifier.run_full_goa_verification", MagicMock(side_effect=Exception("Verify err")))
    result = runner.invoke(app, ["verify", str(tmp_path)])
    assert result.exit_code == 1
    assert "Verification failed" in result.output

