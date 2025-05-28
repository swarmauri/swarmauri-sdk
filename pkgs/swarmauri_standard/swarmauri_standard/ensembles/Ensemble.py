from typing import Any, Dict, Literal

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.ensembles.EnsembleBase import EnsembleBase


@ComponentBase.register_type(EnsembleBase, "Ensemble")
class Ensemble(EnsembleBase):
    """Generic weighted voting ensemble."""

    type: Literal["Ensemble"] = "Ensemble"

    def combine_predictions(self, predictions: Dict[str, Any]) -> Any:
        scores: Dict[Any, float] = {}
        for name, prediction in predictions.items():
            weight = self.weights.get(name, 1.0)
            scores[prediction] = scores.get(prediction, 0.0) + weight
        if not scores:
            return None
        return max(scores.items(), key=lambda item: item[1])[0]
