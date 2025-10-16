"""Billing provider metadata interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Sequence, Tuple, Type

from .enums import Capability


class IBillingProvider(ABC):
    """Shared interface for all billing providers."""

    @property
    @abstractmethod
    def capabilities(self) -> Sequence[Capability]:
        """Return provider capabilities as capability identifiers."""

    @property
    @abstractmethod
    def api_strategies(self) -> Tuple[Type[Any], ...]:
        """Return strategy interfaces supported by the provider."""
