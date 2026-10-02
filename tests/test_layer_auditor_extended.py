import pytest
import json
import subprocess
from unittest.mock import MagicMock, patch
from rover_slim.auditors.layer_auditor import LayerAuditor
from rover_slim.models import ImageMetrics

def test_layer_auditor_sdk_success_alpine(monkeypatch):
    auditor = LayerAuditor()
    
    mock_docker = MagicMock()
    mock_client = MagicMock()
    mock_img = MagicMock()
    mock_img.attrs = {"Size": 50 * 1024 * 1024, "RootFS": {"Layers": ["sha256:1", "sha256:2"]}}
    mock_img.history.return_value = [{"size": 50 * 1024 * 1024}]
    mock_client.images.get.return_value = mock_img
    mock_docker.from_env.return_value = mock_client
    
    monkeypatch.setattr("docker.from_env", mock_docker.from_env)
    
    metrics = auditor.audit_image("alpine:latest")
    assert metrics is not None
    assert metrics.uncompressed_size_mb == 50.0
    assert metrics.wasted_space_mb == 0.0
    assert metrics.wasted_percent == 0.0

def test_layer_auditor_sdk_success_fat_image(monkeypatch):
    auditor = LayerAuditor()
    
    mock_docker = MagicMock()
    mock_client = MagicMock()
    mock_img = MagicMock()
    mock_img.attrs = {"Size": 800 * 1024 * 1024}
    # 12 layers -> wasted_percent = 12.5
    mock_img.history.return_value = [{"size": 50 * 1024 * 1024}] * 12
    mock_client.images.get.return_value = mock_img
    mock_docker.from_env.return_value = mock_client
    
    monkeypatch.setattr("docker.from_env", mock_docker.from_env)
    
    metrics = auditor.audit_image("my-fat-image:latest")
    assert metrics is not None
    assert metrics.uncompressed_size_mb == 800.0
    assert metrics.layer_count == 12
    assert metrics.wasted_percent == 12.5
    assert metrics.wasted_space_mb == 100.0

def test_layer_auditor_subprocess_fallback(monkeypatch):
    auditor = LayerAuditor()
    
    # Force SDK import / call to fail
    monkeypatch.setattr("docker.from_env", MagicMock(side_effect=Exception("Docker SDK error")))
    
    def mock_subprocess_run(cmd, *args, **kwargs):
        res = MagicMock()
        if cmd[1] == "inspect":
            res.returncode = 0
            res.stdout = json.dumps([{"Size": 200 * 1024 * 1024}])
        elif cmd[1] == "history":
            res.returncode = 0
            res.stdout = "50MB\n50MB\n50MB\n50MB\n50MB\n"
        return res

    monkeypatch.setattr(subprocess, "run", mock_subprocess_run)
    
    metrics = auditor.audit_image("my-custom-image:1.0")
    assert metrics is not None
    assert metrics.uncompressed_size_mb == 200.0
    assert metrics.layer_count == 5
    assert metrics.wasted_percent == 4.0

def test_layer_auditor_all_fallbacks_fail(monkeypatch):
    auditor = LayerAuditor()
    monkeypatch.setattr("docker.from_env", MagicMock(side_effect=Exception("Docker SDK error")))
    monkeypatch.setattr(subprocess, "run", MagicMock(side_effect=Exception("Subprocess error")))
    
    metrics = auditor.audit_image("invalid-image:tag")
    assert metrics is None

def test_layer_auditor_estimate_metrics():
    auditor = LayerAuditor()
    baseline = auditor.estimate_baseline_metrics(base_image="python:3.11", packages_count=20, context_leakage_mb=15.0)
    assert baseline.uncompressed_size_mb > 1000.0
    assert baseline.layer_count == 18
    
    optimized = auditor.estimate_optimized_metrics(base_image="python:3.11-slim", prod_packages_count=10)
    assert optimized.uncompressed_size_mb < 300.0
    assert optimized.layer_count == 8
