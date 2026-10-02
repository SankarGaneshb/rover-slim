import pytest
import json
import subprocess
from unittest.mock import MagicMock
from rover_slim.auditors.cve_auditor import CVEAuditor

def test_cve_auditor_trivy_success(monkeypatch):
    auditor = CVEAuditor()
    auditor.trivy_path = "/usr/local/bin/trivy"
    
    mock_json = {
        "Results": [
            {
                "Vulnerabilities": [
                    {"Severity": "CRITICAL"},
                    {"Severity": "HIGH"},
                    {"Severity": "HIGH"},
                    {"Severity": "MEDIUM"},
                    {"Severity": "LOW"}
                ]
            }
        ]
    }
    
    mock_run = MagicMock()
    mock_run.returncode = 0
    mock_run.stdout = json.dumps(mock_json)
    
    monkeypatch.setattr(subprocess, "run", MagicMock(return_value=mock_run))
    
    res = auditor.scan_image("test:tag")
    assert res["CRITICAL"] == 1
    assert res["HIGH"] == 2
    assert res["MEDIUM"] == 1
    assert res["LOW"] == 1

def test_cve_auditor_trivy_exception(monkeypatch):
    auditor = CVEAuditor()
    auditor.trivy_path = "/usr/local/bin/trivy"
    monkeypatch.setattr(subprocess, "run", MagicMock(side_effect=Exception("Timeout")))
    
    res = auditor.scan_image("my-image-slim:latest")
    assert res["CRITICAL"] == 0
    assert res["LOW"] == 1

def test_cve_auditor_thresholds():
    auditor = CVEAuditor()
    
    summary_clean = {"LOW": 2, "MEDIUM": 1, "HIGH": 0, "CRITICAL": 0}
    assert auditor.check_thresholds(summary_clean, ["CRITICAL", "HIGH"]) is True
    
    summary_vuln = {"LOW": 5, "MEDIUM": 2, "HIGH": 1, "CRITICAL": 0}
    assert auditor.check_thresholds(summary_vuln, ["HIGH"]) is False
