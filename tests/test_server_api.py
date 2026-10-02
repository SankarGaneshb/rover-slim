import pytest
import os
import json
from fastapi.testclient import TestClient
from rover_slim.server.app import create_app

@pytest.fixture
def client(tmp_path):
    # Setup a sample repository in tmp_path
    sample_py = tmp_path / "server.py"
    sample_py.write_text("import fastapi\nimport uvicorn\napp = fastapi.FastAPI()\n", encoding="utf-8")
    
    sample_req = tmp_path / "requirements.txt"
    sample_req.write_text("fastapi==0.100.0\nuvicorn==0.22.0\npytest==7.4.0\n", encoding="utf-8")
    
    sample_df = tmp_path / "Dockerfile"
    sample_df.write_text("FROM python:3.11\nWORKDIR /app\nCOPY . .\nRUN pip install -r requirements.txt\nCMD [\"python\", \"server.py\"]\n", encoding="utf-8")

    app = create_app()
    return TestClient(app), str(tmp_path)

def test_health_check(client):
    test_client, _ = client
    res = test_client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["python_version"] == "3.13"

def test_list_docker_images(client):
    test_client, _ = client
    res = test_client.get("/api/images")
    assert res.status_code == 200
    data = res.json()
    assert "images" in data
    assert isinstance(data["images"], list)

def test_audit_project(client):
    test_client, repo_path = client
    res = test_client.post("/api/audit", json={"path": repo_path})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    report = data["report"]
    assert "baseline" in report
    assert "optimized" in report
    assert "pruned_dependencies" in report

def test_inspect_diff(client):
    test_client, repo_path = client
    res = test_client.post("/api/diff", json={"path": repo_path})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "unified_diff" in data
    assert "improvements" in data
    assert len(data["improvements"]) > 0

def test_apply_and_rollback(client):
    test_client, repo_path = client
    # Apply changes
    res = test_client.post("/api/apply", json={
        "path": repo_path,
        "prod_packages": ["fastapi==0.100.0", "uvicorn==0.22.0"],
        "dev_packages": ["pytest==7.4.0"],
        "write_dockerfile": True,
        "write_ignore": True,
        "write_reqs": True
    })
    assert res.status_code == 200
    apply_data = res.json()
    assert apply_data["status"] == "success"
    assert "checkpoint_id" in apply_data
    checkpoint_id = apply_data["checkpoint_id"]

    # Verify generated files exist
    assert os.path.exists(os.path.join(repo_path, "requirements-prod.txt"))
    assert os.path.exists(os.path.join(repo_path, ".dockerignore"))

    # Rollback changes
    res_rb = test_client.post("/api/rollback", json={"path": repo_path, "checkpoint_id": checkpoint_id})
    assert res_rb.status_code == 200
    rb_data = res_rb.json()
    assert rb_data["status"] == "success"

def test_verify_goa(client):
    test_client, repo_path = client
    res = test_client.post("/api/verify", json={"path": repo_path})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "verification" in data

def test_export_formats(client):
    test_client, repo_path = client
    for fmt in ["markdown", "json", "github_action"]:
        res = test_client.post("/api/export", json={"path": repo_path, "format": fmt})
        assert res.status_code == 200
        data = res.json()
        assert data["format"] == fmt
        assert "content" in data
        assert len(data["content"]) > 0

def test_audit_invalid_path(client):
    test_client, _ = client
    res = test_client.post("/api/audit", json={"path": "non_existent_path_xyz"})
    assert res.status_code == 404
