"""Authentication contract for model providers."""

from abc import ABC, abstractmethod
from collections.abc import Mapping


class IProviderAuth(ABC):
    """Apply provider credentials to request headers."""

    @abstractmethod
    def apply(self, headers: Mapping[str, str]) -> Mapping[str, str]:
        pass
