from abc import ABC, abstractmethod
from typing import Any, Dict

from swarmauri_core.llms.IPredict import IPredict


class IEnsemble(ABC):
    """Interface for routing predictions across multiple providers."""

    @abstractmethod
    def add_model(self, name: str, model: IPredict) -> None:
        """Add a provider to the ensemble."""
        pass

    @abstractmethod
    def remove_model(self, name: str) -> bool:
        """Remove a provider from the ensemble."""
        pass

    @abstractmethod
    def list_models(self) -> Dict[str, IPredict]:
        """Return the registered providers."""
        pass

    @abstractmethod
    def route_by_provider(self, provider: str, prompt: str, **kwargs: Any) -> Any:
        """Route a request to a specific provider."""
        pass

    @abstractmethod
    async def aroute_by_provider(
        self, provider: str, prompt: str, **kwargs: Any
    ) -> Any:
        """Asynchronously route a request to a specific provider."""
        pass

    @abstractmethod
    def route(self, prompt: str, **kwargs: Any) -> Any:
        """Route a request to a chosen provider."""
        pass

    @abstractmethod
    async def aroute(self, prompt: str, **kwargs: Any) -> Any:
        """Asynchronously route a request to a chosen provider."""
        pass

    @abstractmethod
    def broadcast(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Send a request to all providers and return their responses."""
        pass

    @abstractmethod
    async def abroadcast(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Asynchronously broadcast a request to all providers."""
        pass
