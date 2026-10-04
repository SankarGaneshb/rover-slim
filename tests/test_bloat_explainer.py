import os
import tempfile
import pytest
from rover_slim.auditors.bloat_explainer import BloatExplainerAuditor, BloatDiagnosticReport

def test_bloat_explainer_analysis():
    with tempfile.TemporaryDirectory() as tmpdir:
        dockerfile_path = os.path.join(tmpdir, "Dockerfile")
        with open(dockerfile_path, "w") as f:
            f.write("""FROM python:3.11
RUN apt-get update && apt-get install -y gcc g++ build-essential
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
""")
        
        auditor = BloatExplainerAuditor(root_dir=tmpdir)
        report = auditor.diagnose(
            dockerfile_path=dockerfile_path,
            pruned_packages_mb=320.0,
            leakage_mb=85.0
        )
        
        assert isinstance(report, BloatDiagnosticReport)
        assert report.total_bloat_mb > 500.0
        assert report.has_single_stage is True
        assert report.has_root_user is True
        assert report.missing_dockerignore is True
        assert len(report.findings) >= 3
        
        categories = [f.category for f in report.findings]
        assert "COMPILER_TOOLCHAIN" in categories
        assert "DEV_DEPENDENCIES" in categories
        assert "CONTEXT_LEAKAGE" in categories
        assert "ROOT_SECURITY" in categories
