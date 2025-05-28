from abc import ABC, abstractmethod
from typing import Any

from swarmauri_core.llms.IPredict import IPredict


class IEnsemble(ABC):
    """Interface for ensembles of prediction models."""

    @abstractmethod
    def add_model(self, name: str, model: IPredict, weight: float = 1.0) -> None:
        """Add a model to the ensemble."""
        pass

    @abstractmethod
    def remove_model(self, name: str) -> bool:
        """Remove a model from the ensemble."""
        pass

    @abstractmethod
    def predict(self, prompt: str, **kwargs: Any) -> Any:
        """Generate a prediction using the ensemble."""
        pass

    @abstractmethod
    async def apredict(self, prompt: str, **kwargs: Any) -> Any:
        """Asynchronously generate a prediction using the ensemble."""
        pass
