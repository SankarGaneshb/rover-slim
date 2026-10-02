from rover_slim.auditors.layer_auditor import LayerAuditor

def test_layer_auditor_baseline_and_optimized_estimates():
    auditor = LayerAuditor()
    
    baseline = auditor.estimate_baseline_metrics("python:3.11", packages_count=30, pruned_packages_mb=150.0, context_leakage_mb=25.0)
    assert baseline.uncompressed_size_mb > 1000.0
    assert baseline.wasted_percent > 10.0
    assert baseline.layer_count > 10

    optimized = auditor.estimate_optimized_metrics("python:3.11-slim", prod_packages_count=10)
    assert optimized.uncompressed_size_mb < 300.0
    assert optimized.wasted_percent < 5.0
    assert optimized.layer_count < 10
