from rover_slim.reporters.diff_inspector import ContainerDiffInspector

def test_diff_inspector_identifies_improvements():
    inspector = ContainerDiffInspector()
    orig = "FROM python:3.11\nRUN apt-get update && apt-get install -y gcc\nRUN pip install -r requirements.txt\n"
    opt = "FROM python:3.11-slim AS builder\nRUN pip install --no-cache-dir --user -r requirements-prod.txt\nFROM python:3.11-slim AS runtime\nUSER appuser\nHEALTHCHECK CMD curl -f http://localhost:8080/health\n"

    diff = inspector.generate_unified_diff(orig, opt)
    assert "--- Dockerfile.baseline" in diff
    assert "+++ Dockerfile.optimized" in diff

    improvements = inspector.analyze_structural_improvements(orig, opt)
    titles = [imp["title"] for imp in improvements]
    assert "Non-Root User Enforcement" in titles
    assert "Disabled Pip Wheel Cache" in titles
    assert "Docker Healthcheck Sentinel" in titles
    assert "2-Stage Multi-Stage Build" in titles
