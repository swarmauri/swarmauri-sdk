from abc import ABC, abstractmethod
from typing import Dict, Any

class IChainContext(ABC):
    @property
    @abstractmethod
    def context(self) -> Dict[str, Any]:
        pass

    @context.setter
    @abstractmethod
    def context(self, value: Dict[str, Any]) -> None:
        pass