"""Endpoint-resolution contract for model providers."""

from abc import ABC, abstractmethod


class IProviderEndpoint(ABC):
    """Resolve a provider capability to a concrete endpoint."""

    @abstractmethod
    def resolve(self, capability: str) -> str:
        pass
