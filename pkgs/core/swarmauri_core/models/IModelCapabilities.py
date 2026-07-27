"""Interface describing model capabilities."""

from abc import ABC, abstractmethod
from typing import FrozenSet


class IModelCapabilities(ABC):
    input_modalities: FrozenSet[str]
    output_modalities: FrozenSet[str]
    features: FrozenSet[str]

    @abstractmethod
    def supports(self, feature: str) -> bool: ...
