import pytest
import os
import json
import time
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from rover_slim.reporters.diff_inspector import ContainerDiffInspector
from rover_slim.synthesizers.dockerignore_gen import DockerignoreGenerator
from rover_slim.core.watcher import ProjectWatcher
from rover_slim.verifiers.goa_sentinel import GoASentinelVerifier
from rover_slim.server.app import app

client = TestClient(app)

def test_diff_inspector_print_diff():
    inspector = ContainerDiffInspector()
    orig = "FROM python:3.11\nRUN pip install -r reqs.txt\nCMD python main.py\n"
    opt = "FROM python:3.11 AS builder\nRUN pip install --no-cache-dir -r reqs.txt\nFROM python:3.11\nUSER appuser\nHEALTHCHECK CMD curl -f http://localhost:8080/health\nCMD [\"python\", \"main.py\"]\n"
    
    imps = inspector.analyze_structural_improvements(orig, opt)
    assert len(imps) == 4
    inspector.print_diff(orig, opt)

def test_dockerignore_generator(tmp_path):
    gen = DockerignoreGenerator(str(tmp_path))
    content = gen.generate(custom_rules=["custom_secret.key"])
    assert "custom_secret.key" in content
    
    out_file, count = gen.write(str(tmp_path / ".dockerignore"), force=True)
    assert os.path.exists(out_file)

def test_watcher_sync_once_and_get_files(tmp_path):
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("fastapi==0.110.0\n", encoding="utf-8")
    
    py_file = tmp_path / "main.py"
    py_file.write_text("import fastapi\n", encoding="utf-8")
    
    watcher = ProjectWatcher(root_dir=str(tmp_path))
    files = watcher._get_tracked_files()
    assert len(files) >= 1
    
    assert watcher.sync_once() is True

def test_watcher_start_watch_loop(tmp_path, monkeypatch):
    watcher = ProjectWatcher(root_dir=str(tmp_path), poll_interval=0.01)
    
    # Simulate single iteration and break
    iteration = [0]
    def mock_sleep(interval):
        iteration[0] += 1
        if iteration[0] > 1:
            watcher.stop()
    
    monkeypatch.setattr(time, "sleep", mock_sleep)
    watcher.start_watch()
    assert not watcher._is_running

def test_goa_sentinel_full_verification(tmp_path):
    sentinel = GoASentinelVerifier(root_dir=str(tmp_path))
    
    with patch.object(sentinel, "is_docker_available", return_value=False):
        results = sentinel.run_full_goa_verification(image_tag="test:latest")
        assert "overall_status" in results
        assert results["overall_status"] == "GREEN (PASSED)"

def test_server_api_endpoints(tmp_path):
    # Health
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"
    
    # Images
    res = client.get("/api/images")
    assert res.status_code == 200
    assert "images" in res.json()
    
    # Audit
    res = client.post("/api/audit", json={"path": str(tmp_path)})
    assert res.status_code == 200
    assert res.json()["status"] == "success"
    
    # Diff
    res = client.post("/api/diff", json={"path": str(tmp_path)})
    assert res.status_code == 200
    assert "unified_diff" in res.json()
    assert "improvements" in res.json()
    
    # Optimize
    res = client.post("/api/optimize", json={
        "path": str(tmp_path),
        "verify_goa": False,
        "prod_packages": ["fastapi>=0.110.0"],
        "dev_packages": ["pytest>=7.0.0"]
    })
    assert res.status_code == 200
    assert res.json()["status"] == "success"
    
    # Apply
    res = client.post("/api/apply", json={
        "path": str(tmp_path),
        "prod_packages": ["fastapi>=0.110.0"],
        "dev_packages": ["pytest>=7.0.0"]
    })
    assert res.status_code == 200
    assert res.json()["status"] == "success"
    
    # Rollback
    res = client.post("/api/rollback", json={"path": str(tmp_path)})
    assert res.status_code == 200
    
    # Verify
    res = client.post("/api/verify", json={"path": str(tmp_path)})
    assert res.status_code == 200
    
    # Export formats
    for fmt in ["markdown", "github_action", "gitlab_ci", "json"]:
        res = client.post("/api/export", json={"path": str(tmp_path), "format": fmt})
        assert res.status_code == 200
        assert "content" in res.json()

def test_server_api_404_handling():
    res = client.post("/api/audit", json={"path": "/non/existent/path/for/404"})
    assert res.status_code == 404
    
    res = client.post("/api/optimize", json={"path": "/non/existent/path/for/404"})
    assert res.status_code == 404
    
    res = client.post("/api/apply", json={"path": "/non/existent/path/for/404"})
    assert res.status_code == 404
    
    res = client.post("/api/rollback", json={"path": "/non/existent/path/for/404"})
    assert res.status_code == 404
    
    res = client.post("/api/verify", json={"path": "/non/existent/path/for/404"})
    assert res.status_code == 404
