import os
import tempfile
import json
from rover_slim.core.engine import RoverSlimEngine

def test_all_report_generators():
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = RoverSlimEngine(root_dir=tmpdir)
        report = engine.audit()

        # JSON
        json_str = engine.json_reporter.generate_json(report)
        data = json.loads(json_str)
        assert data["status"] in ["PASSED", "FAILED"]
        assert "baseline" in data
        assert "optimized" in data

        # Markdown
        md_str = engine.md_reporter.generate_markdown(report)
        assert "## 🚀 Rover-Slim Optimization Report" in md_str
        assert "Uncompressed Size" in md_str

        # HTML
        html_str = engine.html_reporter.generate_html(report)
        assert "<!DOCTYPE html>" in html_str
        assert "Rover-Slim Optimization Report" in html_str
