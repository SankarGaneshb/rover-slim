import os
import tempfile
import pytest
from rover_slim.languages.registry import LanguageRegistry
from rover_slim.languages.python_adapter import PythonLanguageAdapter
from rover_slim.models import RoverSlimConfig

def test_language_registry_detection():
    registry = LanguageRegistry()
    registry.register(PythonLanguageAdapter())

    with tempfile.TemporaryDirectory() as tmpdir:
        # Python repo with requirements.txt
        req_path = os.path.join(tmpdir, "requirements.txt")
        with open(req_path, "w") as f:
            f.write("fastapi==0.100.0\nuvicorn>=0.20.0\npytest==7.4.0\n")

        adapter = registry.detect_language(tmpdir)
        assert adapter is not None
        assert adapter.name == "python"
        assert adapter.display_name == "Python 3.x (AST-Driven)"

def test_python_adapter_analysis():
    adapter = PythonLanguageAdapter()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        app_code = """
import os
import fastapi
import uvicorn

app = fastapi.FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}
"""
        with open(os.path.join(tmpdir, "app.py"), "w") as f:
            f.write(app_code)

        with open(os.path.join(tmpdir, "requirements.txt"), "w") as f:
            f.write("fastapi==0.100.0\nuvicorn>=0.20.0\npytest==7.4.0\nblack==23.1.0\n")

        assert adapter.detect(tmpdir) is True
        prod, dev, pruned = adapter.segregate_dependencies(tmpdir)
        
        prod_names = [p.name.lower() for p in prod]
        dev_names = [d.name.lower() for d in dev]
        
        assert "fastapi" in prod_names
        assert "uvicorn" in prod_names
        assert "pytest" in dev_names or any(p.package.lower() == "pytest" for p in pruned)
        
        # Test Dockerfile synthesis
        config = RoverSlimConfig()
        df = adapter.synthesize_dockerfile(config, tmpdir)
        assert "FROM" in df
        assert "USER appuser" in df

        # Test probe discovery
        probes = adapter.discover_health_probes(tmpdir)
        assert isinstance(probes, list)

def test_python_adapter_empty_repo():
    adapter = PythonLanguageAdapter()
    with tempfile.TemporaryDirectory() as tmpdir:
        # Empty dir has no python files
        assert adapter.detect(tmpdir) is False
