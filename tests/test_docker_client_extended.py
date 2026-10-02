import pytest
import subprocess
import time
from unittest.mock import MagicMock
from rover_slim.core.docker_client import DockerClientWrapper

def test_docker_client_is_available_true(monkeypatch):
    client = DockerClientWrapper()
    client.docker_bin = "/usr/bin/docker"
    
    mock_run = MagicMock()
    mock_run.returncode = 0
    monkeypatch.setattr(subprocess, "run", MagicMock(return_value=mock_run))
    
    assert client.is_available() is True

def test_docker_client_is_available_false(monkeypatch):
    client = DockerClientWrapper()
    client.docker_bin = None
    assert client.is_available() is False
    
    client.docker_bin = "/usr/bin/docker"
    monkeypatch.setattr(subprocess, "run", MagicMock(side_effect=Exception("error")))
    assert client.is_available() is False

def test_docker_client_build_image(monkeypatch):
    client = DockerClientWrapper()
    client.docker_bin = "/usr/bin/docker"
    
    # Unavailable case
    monkeypatch.setattr(client, "is_available", lambda: False)
    res = client.build_image(".", "test:latest")
    assert res["success"] is False
    assert res["simulated"] is True
    
    # Available success case
    monkeypatch.setattr(client, "is_available", lambda: True)
    mock_run = MagicMock()
    mock_run.returncode = 0
    mock_run.stdout = "Successfully built 12345"
    mock_run.stderr = ""
    monkeypatch.setattr(subprocess, "run", MagicMock(return_value=mock_run))
    
    res = client.build_image(".", "test:latest", dockerfile_path="Dockerfile.custom")
    assert res["success"] is True
    assert res["tag"] == "test:latest"
    assert "build_time_seconds" in res

def test_docker_client_run_ephemeral_probe(monkeypatch):
    client = DockerClientWrapper()
    client.docker_bin = "/usr/bin/docker"
    
    # Unavailable case
    monkeypatch.setattr(client, "is_available", lambda: False)
    res = client.run_ephemeral_probe("test:latest")
    assert res["status"] == "PASSED"
    assert res["simulated"] is True
    
    # Available success case
    monkeypatch.setattr(client, "is_available", lambda: True)
    monkeypatch.setattr(time, "sleep", lambda s: None)
    
    def mock_subprocess_run(cmd, *args, **kwargs):
        res = MagicMock()
        if cmd[1] == "run":
            res.returncode = 0
            res.stdout = "container1234567890\n"
        elif cmd[1] == "inspect":
            res.returncode = 0
            res.stdout = "true\n"
        elif cmd[1] == "rm":
            res.returncode = 0
        return res

    monkeypatch.setattr(subprocess, "run", mock_subprocess_run)
    
    res = client.run_ephemeral_probe("test:latest")
    assert res["success"] is True
    assert res["status"] == "PASSED"
    assert res["container_id"] == "container123"

def test_docker_client_run_ephemeral_probe_failure(monkeypatch):
    client = DockerClientWrapper()
    client.docker_bin = "/usr/bin/docker"
    monkeypatch.setattr(client, "is_available", lambda: True)
    monkeypatch.setattr(subprocess, "run", MagicMock(side_effect=Exception("Docker run failed")))
    
    res = client.run_ephemeral_probe("test:latest")
    assert res["success"] is False
    assert res["status"] == "FAILED"
