"""Authentication contract for model providers."""

from abc import ABC, abstractmethod
from collections.abc import Mapping


class IProviderAuth(ABC):
    """Apply provider credentials to request metadata."""

    @abstractmethod
    def apply(self, headers: Mapping[str, str]) -> Mapping[str, str]:
        pass

    @abstractmethod
    def apply_query(self, query: Mapping[str, str]) -> Mapping[str, str]:
        pass
