from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ProbeConfig(BaseModel):
    name: str
    type: str = Field("http", description="http | script | tcp")
    path: Optional[str] = "/health"
    port: Optional[int] = 8080
    command: Optional[str] = None
    expected_status: int = 200
    timeout_seconds: int = 15

class VerificationConfig(BaseModel):
    auto_discover: bool = True
    startup_command: Optional[str] = "python -c 'import server'"
    probes: List[ProbeConfig] = Field(default_factory=list)

class OptimizationThresholds(BaseModel):
    max_image_size_mb: float = 350.0
    max_wasted_percent: float = 10.0
    max_cold_start_seconds: float = 2.5
    fail_on_cve_severity: List[str] = Field(default_factory=lambda: ["CRITICAL"])

class BuildConfig(BaseModel):
    target_base_image: str = "python:3.11-slim"
    enable_multistage: bool = True
    strip_node_runtime: bool = True
    frontend_dist_path: str = "static/"

class ReportingConfig(BaseModel):
    formats: List[str] = Field(default_factory=lambda: ["terminal", "markdown", "html", "json"])
    json_output_path: str = ".rover-slim/report.json"
    html_output_path: str = ".rover-slim/report.html"
    markdown_output_path: str = ".rover-slim/summary.md"

class RoverSlimConfig(BaseModel):
    version: str = "1.0"
    project_name: str = "default-project"
    thresholds: OptimizationThresholds = Field(default_factory=OptimizationThresholds)
    build: BuildConfig = Field(default_factory=BuildConfig)
    verification: VerificationConfig = Field(default_factory=VerificationConfig)
    dependencies: Dict[str, List[str]] = Field(
        default_factory=lambda: {
            "always_production": [],
            "always_development": []
        }
    )
    reporting: ReportingConfig = Field(default_factory=ReportingConfig)

class PrunedPackage(BaseModel):
    package: str
    action: str  # "MOVED_TO_DEV" | "EXCLUDED"
    reason: str
    estimated_size_mb: float

class ImageMetrics(BaseModel):
    uncompressed_size_mb: float
    compressed_size_mb: float
    build_context_mb: float
    build_time_seconds: float
    layer_count: int
    wasted_space_mb: float
    wasted_percent: float
    total_packages: int
    cve_summary: Dict[str, int] = Field(default_factory=dict)

class OptimizationReport(BaseModel):
    project: str
    timestamp: str
    status: str  # "PASSED" | "FAILED"
    baseline: ImageMetrics
    optimized: ImageMetrics
    pruned_dependencies: List[PrunedPackage]
    goa_verification: Dict[str, Any]
