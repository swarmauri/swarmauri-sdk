from typing import Any, Dict, Optional, Literal

from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.llms.LLMBase import LLMBase
from swarmauri_core.ensembles.IEnsemble import IEnsemble


@ComponentBase.register_model()
class EnsembleBase(IEnsemble, ComponentBase):
    """Base implementation for LLM ensembles."""

    resource: Optional[str] = Field(default=ResourceTypes.ENSEMBLE.value)
    type: Literal["EnsembleBase"] = "EnsembleBase"

    llms: Dict[str, LLMBase] = Field(default_factory=dict)
    weights: Dict[str, float] = Field(default_factory=dict)

    def add_model(self, name: str, model: LLMBase, weight: float = 1.0) -> None:
        if name in self.llms:
            raise ValueError(f"Model '{name}' already exists")
        self.llms[name] = model
        self.weights[name] = weight

    def remove_model(self, name: str) -> bool:
        removed = name in self.llms
        if removed:
            self.llms.pop(name)
            self.weights.pop(name, None)
        return removed

    def predict(self, prompt: str, **kwargs: Any) -> Any:
        predictions = {name: llm.predict(prompt, **kwargs) for name, llm in self.llms.items()}
        return self.combine_predictions(predictions)

    async def apredict(self, prompt: str, **kwargs: Any) -> Any:
        predictions: Dict[str, Any] = {}
        for name, llm in self.llms.items():
            predictions[name] = await llm.apredict(prompt, **kwargs)
        return self.combine_predictions(predictions)

    def combine_predictions(self, predictions: Dict[str, Any]) -> Any:
        """Combine model predictions. Subclasses can override."""
        return next(iter(predictions.values()), None)
