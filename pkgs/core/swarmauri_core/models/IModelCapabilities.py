"""Interface describing model capabilities."""

from abc import ABC, abstractmethod
from typing import FrozenSet


class IModelCapabilities(ABC):
    input_modalities: frozenset[str]
    output_modalities: frozenset[str]
    features: frozenset[str]

    @abstractmethod
    def supports(self, feature: str) -> bool: ...
