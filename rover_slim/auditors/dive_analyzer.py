from typing import List, Dict, Any, Optional

class LayerEfficiencyDetail:
    def __init__(self, layer_id: str, size_mb: float, instruction: str, wasted_mb: float = 0.0, score: float = 1.0):
        self.layer_id = layer_id
        self.size_mb = size_mb
        self.instruction = instruction
        self.wasted_mb = wasted_mb
        self.score = score

class DiveLayerAnalyzer:
    """Simulates deep layer efficiency and file duplication analysis inspired by Wagoodman's Dive."""

    def analyze_layers(self, raw_history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        layers: List[LayerEfficiencyDetail] = []
        
        if not raw_history:
            # Typical unoptimized single-stage layer profile
            layers = [
                LayerEfficiencyDetail("sha256:1a2b...", 125.0, "FROM python:3.11", wasted_mb=0.0, score=1.0),
                LayerEfficiencyDetail("sha256:2b3c...", 340.0, "RUN apt-get update && apt-get install -y gcc ...", wasted_mb=85.0, score=0.75),
                LayerEfficiencyDetail("sha256:3c4d...", 450.0, "RUN pip install -r requirements.txt", wasted_mb=95.0, score=0.78),
                LayerEfficiencyDetail("sha256:4d5e...", 12.0, "COPY . /app", wasted_mb=3.5, score=0.70)
            ]
        else:
            for idx, item in enumerate(raw_history):
                sz = item.get("Size", 0) / (1024 * 1024)
                inst = item.get("CreatedBy", f"Layer {idx}")
                wasted = sz * 0.15 if "pip" in inst or "apt" in inst else 0.0
                layers.append(LayerEfficiencyDetail(
                    layer_id=f"layer_{idx}",
                    size_mb=round(sz, 2),
                    instruction=inst[:60],
                    wasted_mb=round(wasted, 2),
                    score=0.85 if wasted > 0 else 1.0
                ))

        total_size = sum(l.size_mb for l in layers)
        total_wasted = sum(l.wasted_mb for l in layers)
        efficiency_score = (1.0 - (total_wasted / total_size)) if total_size > 0 else 1.0

        return {
            "total_layers": len(layers),
            "total_size_mb": round(total_size, 2),
            "wasted_space_mb": round(total_wasted, 2),
            "efficiency_percentage": round(efficiency_score * 100, 1),
            "inefficient_layers": [
                {
                    "layer": l.layer_id,
                    "instruction": l.instruction,
                    "size_mb": l.size_mb,
                    "wasted_mb": l.wasted_mb
                }
                for l in layers if l.wasted_mb > 0
            ]
        }
