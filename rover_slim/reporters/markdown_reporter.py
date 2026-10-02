import os
from rover_slim.models import OptimizationReport

class MarkdownReporter:
    """Generates GitHub PR markdown tables, diff summaries, and GoA sentinel badge reports."""

    def generate_markdown(self, report: OptimizationReport) -> str:
        reduction_mb = report.baseline.uncompressed_size_mb - report.optimized.uncompressed_size_mb
        reduction_pct = (
            (reduction_mb / report.baseline.uncompressed_size_mb * 100)
            if report.baseline.uncompressed_size_mb > 0
            else 0.0
        )
        badge_status = "🟢 Passed" if report.status == "PASSED" else "🔴 Failed"

        md = []
        md.append(f"## 🚀 Rover-Slim Optimization Report: `{report.project}`\n")
        md.append(f"> **Status**: {badge_status} | **Generated**: {report.timestamp}\n")
        md.append(f"### 📊 Key Container Metrics\n")
        md.append("| Metric | Baseline (Fat Image) | Optimized (Slim Multi-Stage) | Delta / Savings |")
        md.append("| :--- | :--- | :--- | :--- |")
        md.append(f"| **Uncompressed Size** | `{report.baseline.uncompressed_size_mb:.1f} MB` | `{report.optimized.uncompressed_size_mb:.1f} MB` | **-{reduction_mb:.1f} MB (-{reduction_pct:.1f}%)** |")
        md.append(f"| **Registry Transfer (Comp.)** | `{report.baseline.compressed_size_mb:.1f} MB` | `{report.optimized.compressed_size_mb:.1f} MB` | -{(report.baseline.compressed_size_mb - report.optimized.compressed_size_mb):.1f} MB |")
        md.append(f"| **Build Context** | `{report.baseline.build_context_mb:.1f} MB` | `{report.optimized.build_context_mb:.1f} MB` | -{(report.baseline.build_context_mb - report.optimized.build_context_mb):.1f} MB |")
        md.append(f"| **Layer Count** | {report.baseline.layer_count} | {report.optimized.layer_count} | -{report.baseline.layer_count - report.optimized.layer_count} layers |")
        md.append(f"| **Wasted Layer Space** | {report.baseline.wasted_percent:.1f}% ({report.baseline.wasted_space_mb:.1f} MB) | {report.optimized.wasted_percent:.1f}% ({report.optimized.wasted_space_mb:.1f} MB) | -{(report.baseline.wasted_space_mb - report.optimized.wasted_space_mb):.1f} MB |")
        md.append(f"| **Installed Packages** | {report.baseline.total_packages} | {report.optimized.total_packages} | -{report.baseline.total_packages - report.optimized.total_packages} pkgs |\n")

        if report.pruned_dependencies:
            md.append("### ✂️ Pruned Dependencies (Moved to `requirements-dev.txt`)\n")
            md.append("<details><summary><b>Click to view details of pruned packages</b></summary>\n")
            md.append("| Package | Action | Reason | Est. Savings |")
            md.append("| :--- | :--- | :--- | :--- |")
            for p in report.pruned_dependencies:
                md.append(f"| `{p.package}` | {p.action} | {p.reason} | ~{p.estimated_size_mb:.1f} MB |")
            md.append("\n</details>\n")

        md.append("### 🛡️ Green-on-Arrival (GoA) Sentinel Verification\n")
        goa = report.goa_verification
        md.append(f"- **Overall Status**: `{goa.get('overall_status', 'UNKNOWN')}`")
        startup = goa.get("startup_integrity", {})
        md.append(f"- **Startup Integrity**: `{startup.get('status', 'PASSED')}` (Command: `{startup.get('command', 'N/A')}`)")
        for probe in goa.get("probes", []):
            md.append(f"- **Probe `{probe.get('probe')}`**: `{probe.get('status')}` ({probe.get('type')})")
        assets = goa.get("static_assets", {})
        md.append(f"- **Static Assets**: `{assets.get('status', 'PASSED')}` ({assets.get('details', '')})\n")

        md.append("---\n*Generated autonomously by [Rover-Slim](https://github.com/market-rover/rover-slim)*")
        return "\n".join(md)

    def write_markdown(self, report: OptimizationReport, output_path: str = ".rover-slim/summary.md") -> str:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        content = self.generate_markdown(report)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return output_path
