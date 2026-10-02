from rover_slim.auditors.cve_auditor import CVEAuditor

def test_cve_auditor_baseline_and_thresholds():
    auditor = CVEAuditor()
    
    # Slim image baseline
    slim_cve = auditor.scan_image("my-service:slim")
    assert slim_cve.get("CRITICAL", 0) == 0
    assert auditor.check_thresholds(slim_cve, fail_on=["CRITICAL"]) is True

    # Fat image baseline
    fat_cve = auditor.scan_image("my-service:latest")
    assert fat_cve.get("CRITICAL", 0) > 0
    assert auditor.check_thresholds(fat_cve, fail_on=["CRITICAL"]) is False
