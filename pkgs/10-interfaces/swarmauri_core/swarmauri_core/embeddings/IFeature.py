from abc import ABC, abstractmethod
from typing import Any


class IFeature(ABC):
    @abstractmethod
    def extract_features(self) -> list[Any]:
        pass
