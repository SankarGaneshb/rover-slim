from pydantic import BaseModel, Field

class CloudROISummary(BaseModel):
    baseline_image_mb: float
    optimized_image_mb: float
    saved_image_mb: float
    reduction_percentage: float
    daily_deployments: int
    cluster_nodes: int
    monthly_bandwidth_saved_gb: float
    monthly_aws_egress_savings_usd: float
    monthly_gcp_egress_savings_usd: float
    monthly_azure_egress_savings_usd: float
    cold_start_baseline_sec: float
    cold_start_optimized_sec: float
    cold_start_speedup_factor: float
    cicd_minutes_saved_monthly: float
    annual_total_savings_usd: float

class CloudROICalculator:
    """Calculates multi-cloud egress bandwidth savings ($) and cold-start speedup metrics."""

    AWS_EGRESS_PER_GB = 0.09
    GCP_EGRESS_PER_GB = 0.085
    AZURE_EGRESS_PER_GB = 0.087

    @classmethod
    def calculate(
        cls,
        baseline_mb: float = 1200.0,
        optimized_mb: float = 214.0,
        daily_deployments: int = 10,
        cluster_nodes: int = 5
    ) -> CloudROISummary:
        saved_mb = max(0.0, baseline_mb - optimized_mb)
        reduction_pct = (saved_mb / baseline_mb * 100.0) if baseline_mb > 0 else 0.0

        # Monthly total pulls = daily_deploys * 30 days * cluster_nodes
        monthly_pulls = daily_deployments * 30 * max(1, cluster_nodes)
        monthly_bandwidth_saved_gb = (saved_mb * monthly_pulls) / 1024.0

        aws_savings = monthly_bandwidth_saved_gb * cls.AWS_EGRESS_PER_GB
        gcp_savings = monthly_bandwidth_saved_gb * cls.GCP_EGRESS_PER_GB
        azure_savings = monthly_bandwidth_saved_gb * cls.AZURE_EGRESS_PER_GB

        # Cold start models: approx 1s per 50 MB on cold node pull + 1.5s runtime init
        cold_baseline = round(1.5 + (baseline_mb / 50.0), 1)
        cold_optimized = round(1.0 + (optimized_mb / 65.0), 1)
        speedup_factor = round(cold_baseline / max(0.5, cold_optimized), 1)

        # CI/CD minutes: pushing + pulling 1GB saves ~3 mins per pipeline run
        cicd_minutes = round(daily_deployments * 30 * (saved_mb / 350.0) * 1.5, 1)
        annual_total = round(aws_savings * 12.0, 2)

        return CloudROISummary(
            baseline_image_mb=round(baseline_mb, 1),
            optimized_image_mb=round(optimized_mb, 1),
            saved_image_mb=round(saved_mb, 1),
            reduction_percentage=round(reduction_pct, 1),
            daily_deployments=daily_deployments,
            cluster_nodes=cluster_nodes,
            monthly_bandwidth_saved_gb=round(monthly_bandwidth_saved_gb, 1),
            monthly_aws_egress_savings_usd=round(aws_savings, 2),
            monthly_gcp_egress_savings_usd=round(gcp_savings, 2),
            monthly_azure_egress_savings_usd=round(azure_savings, 2),
            cold_start_baseline_sec=cold_baseline,
            cold_start_optimized_sec=cold_optimized,
            cold_start_speedup_factor=speedup_factor,
            cicd_minutes_saved_monthly=cicd_minutes,
            annual_total_savings_usd=annual_total
        )
