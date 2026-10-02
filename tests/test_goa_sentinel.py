from rover_slim.verifiers.goa_sentinel import GoASentinelVerifier
from rover_slim.models import RoverSlimConfig

def test_goa_sentinel_simulation_run():
    config = RoverSlimConfig(project_name="unit-test-app")
    sentinel = GoASentinelVerifier(config)

    res = sentinel.run_full_goa_verification()
    assert "overall_status" in res
    assert "startup_integrity" in res
    assert "probes" in res
    assert "static_assets" in res
    assert "GREEN" in res["overall_status"]
