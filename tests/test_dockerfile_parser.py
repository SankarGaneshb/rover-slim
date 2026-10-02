from rover_slim.parsers.dockerfile_parser import DockerfileParser

def test_dockerfile_parser_parses_multistage_and_warnings():
    dockerfile_content = """
FROM python:3.11 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM python:3.11-slim AS runtime
WORKDIR /app
COPY --from=builder /root/.local /root/.local
EXPOSE 8080 9000
RUN apt-get update && apt-get install -y curl
USER appuser
CMD ["python", "server.py"]
"""
    parser = DockerfileParser()
    analysis = parser.parse(content=dockerfile_content)

    assert analysis.is_multistage is True
    assert len(analysis.base_images) == 2
    assert "python:3.11" in analysis.base_images
    assert "python:3.11-slim" in analysis.base_images
    assert 8080 in analysis.exposed_ports
    assert 9000 in analysis.exposed_ports
    assert analysis.runs_as_root is False
    assert analysis.cmd == '["python", "server.py"]'
    assert len(analysis.warnings) > 0  # pip without --no-cache-dir, apt without cache clean

def test_dockerfile_parser_flags_single_stage_and_root():
    dockerfile_content = """
FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "app.py"]
"""
    parser = DockerfileParser()
    analysis = parser.parse(content=dockerfile_content)

    assert analysis.is_multistage is False
    assert analysis.runs_as_root is True
    assert analysis.copies_root_context is True
    assert any("Single-stage build" in w for w in analysis.warnings)
    assert any("root user" in w for w in analysis.warnings)
