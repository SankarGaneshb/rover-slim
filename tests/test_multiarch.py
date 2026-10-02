from rover_slim.synthesizers.multiarch import MultiArchSynthesizer

def test_multiarch_synthesizer_generates_buildx_template():
    synth = MultiArchSynthesizer()
    dockerfile = synth.synthesize()

    assert "FROM --platform=$BUILDPLATFORM" in dockerfile
    assert "ARG TARGETPLATFORM" in dockerfile
    assert "FROM python:3.11-slim AS runtime" in dockerfile

    cmd = synth.generate_buildx_command("my-org/my-image:latest", platforms=["linux/amd64", "linux/arm64"])
    assert "docker buildx build" in cmd
    assert "--platform linux/amd64,linux/arm64" in cmd
    assert "-t my-org/my-image:latest" in cmd
