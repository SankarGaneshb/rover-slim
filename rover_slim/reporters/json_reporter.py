import os
import json
from rover_slim.models import OptimizationReport

class JSONReporter:
    """Exports structured, machine-readable JSON metrics for CI pipelines and dashboards."""

    def generate_json(self, report: OptimizationReport) -> str:
        return report.model_dump_json(indent=2)

    def write_json(self, report: OptimizationReport, output_path: str = ".rover-slim/report.json") -> str:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        content = self.generate_json(report)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return output_path
