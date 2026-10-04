import os
import tempfile
import pytest
from rover_slim.auditors.cloud_roi_calculator import CloudROICalculator, CloudROISummary
from rover_slim.auditors.security_scorecard import SecurityScorecardAuditor, SecurityScorecardReport

def test_cloud_roi_calculator():
    summary = CloudROICalculator.calculate(
        baseline_mb=1200.0,
        optimized_mb=200.0,
        daily_deployments=20,
        cluster_nodes=10
    )
    
    assert isinstance(summary, CloudROISummary)
    assert summary.baseline_image_mb == 1200.0
    assert summary.optimized_image_mb == 200.0
    assert summary.saved_image_mb == 1000.0
    assert summary.reduction_percentage > 80.0
    assert summary.cold_start_speedup_factor > 1.0
    assert summary.monthly_aws_egress_savings_usd > 0.0
    assert summary.monthly_gcp_egress_savings_usd > 0.0
    assert summary.monthly_azure_egress_savings_usd > 0.0
    assert summary.annual_total_savings_usd > 0.0

def test_security_scorecard_auditor():
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Compliant Dockerfile
        df_good = os.path.join(tmpdir, "Dockerfile.good")
        with open(df_good, "w") as f:
            f.write("""FROM python:3.11-slim AS builder
RUN apt-get update && apt-get install -y gcc
RUN pip wheel -w /wheels fastapi

FROM python:3.11-slim
RUN groupadd -g 10001 appuser && useradd -u 10001 -g appuser appuser
COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/*
USER appuser
CMD ["python", "app.py"]
""")
        
        auditor = SecurityScorecardAuditor(root_dir=tmpdir)
        report = auditor.audit(dockerfile_path=df_good)
        
        assert isinstance(report, SecurityScorecardReport)
        assert report.hardening_score >= 80
        assert report.is_non_root is True
        assert report.has_zero_compilers is True
        assert report.grade in ["A+", "A"]
        
        # 2. Non-compliant Dockerfile (root + single stage compiler)
        df_bad = os.path.join(tmpdir, "Dockerfile.bad")
        with open(df_bad, "w") as f:
            f.write("""FROM python:3.11
RUN apt-get update && apt-get install -y gcc build-essential
COPY . /app
WORKDIR /app
CMD ["python", "app.py"]
""")
        
        report_bad = auditor.audit(dockerfile_path=df_bad)
        assert report_bad.is_non_root is False
        assert report_bad.has_zero_compilers is False
        assert report_bad.hardening_score < 70
        assert report_bad.grade in ["C", "D", "F"]
