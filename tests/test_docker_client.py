from rover_slim.core.docker_client import DockerClientWrapper

def test_docker_client_wrapper_graceful_fallback():
    client = DockerClientWrapper()
    # Should safely return status without throwing exceptions
    res = client.run_ephemeral_probe("non-existent-image:test")
    assert "status" in res
