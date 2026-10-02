import os
from rover_slim.synthesizers.multistage import MultiStageSynthesizer
from rover_slim.models import RoverSlimConfig

def test_multistage_dockerfile_rendering():
    config = RoverSlimConfig(
        project_name="test-service"
    )
    synth = MultiStageSynthesizer(config)
    dockerfile = synth.synthesize()

    # Verify both stages exist
    assert "FROM python:3.11-slim AS builder" in dockerfile
    assert "FROM python:3.11-slim AS runtime" in dockerfile

    # Verify no-cache pip and rootless user
    assert "--no-cache-dir" in dockerfile
    assert "useradd" in dockerfile
    assert "USER appuser" in dockerfile
    assert "HEALTHCHECK" in dockerfile
