from abc import ABC, abstractmethod
from typing import Any


class IChainContext(ABC):
    @abstractmethod
    def update(self, **kwargs) -> None:
        pass

    def get_value(self, key: str) -> Any:
        pass
