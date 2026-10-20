from rover_slim.verifiers.goa_sentinel import GoASentinelVerifier
from rover_slim.models import RoverSlimConfig, ProbeConfig

def test_goa_sentinel_simulation_run():
    config = RoverSlimConfig(project_name="unit-test-app")
    sentinel = GoASentinelVerifier(config)

    res = sentinel.run_full_goa_verification()
    assert "overall_status" in res
    assert "startup_integrity" in res
    assert "probes" in res
    assert "static_assets" in res
    assert "GREEN" in res["overall_status"]

def test_goa_sentinel_real_script_probe():
    config = RoverSlimConfig(project_name="script-probe-app")
    config.verification.probes = [
        ProbeConfig(name="Passing Script", type="script", command='python -c "print(123)"', timeout_seconds=5),
        ProbeConfig(name="Failing Script", type="script", command='python -c "import sys; sys.exit(1)"', timeout_seconds=5),
    ]
    sentinel = GoASentinelVerifier(config)
    results = sentinel.verify_probes()
    assert len(results) == 2
    assert results[0]["status"] == "PASSED"
    assert results[1]["status"] == "FAILED"

def test_goa_sentinel_failing_probes_impact_overall():
    config = RoverSlimConfig(project_name="probe-fail-app")
    config.verification.probes = [
        # Port 59123 is closed locally, TCP connection should fail
        ProbeConfig(name="Unreachable TCP", type="tcp", port=59123, timeout_seconds=1)
    ]
    sentinel = GoASentinelVerifier(config)
    res = sentinel.run_full_goa_verification()
    assert res["overall_status"] == "RED (FAILED)"
    assert res["probes"][0]["status"] == "FAILED"
