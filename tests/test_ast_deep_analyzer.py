import os
import tempfile
from rover_slim.parsers.ast_deep_analyzer import FrameworkDetector

def test_framework_detector_finds_fastapi_and_routes():
    with tempfile.TemporaryDirectory() as tmpdir:
        server_py = os.path.join(tmpdir, "server.py")
        with open(server_py, "w", encoding="utf-8") as f:
            f.write("""
from fastapi import FastAPI, APIRouter

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/v1/users")
def get_users():
    return []
""")
        detector = FrameworkDetector(tmpdir)
        analysis = detector.analyze_repository()

        assert "fastapi" in analysis["detected_frameworks"]
        assert "/health" in analysis["discovered_routes"]
        assert "/api/v1/users" in analysis["discovered_routes"]
        assert "server.py" in analysis["entrypoint_candidates"]
        assert analysis["recommended_port"] == 8080
        assert len(analysis["recommended_probes"]) > 0
        assert analysis["recommended_probes"][0].path == "/health"
