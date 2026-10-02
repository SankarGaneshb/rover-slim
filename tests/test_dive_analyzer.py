from rover_slim.auditors.dive_analyzer import DiveLayerAnalyzer

def test_dive_layer_analyzer_calculates_efficiency():
    analyzer = DiveLayerAnalyzer()
    res = analyzer.analyze_layers()
    assert res["total_layers"] > 0
    assert "efficiency_percentage" in res
    assert res["wasted_space_mb"] > 0
    assert len(res["inefficient_layers"]) > 0
