from abc import ABC, abstractmethod
from typing import Dict, Any, List


class ITool(ABC):
    @abstractmethod
    def call(self, *args, **kwargs):
        pass

    @abstractmethod
    def __call__(self, *args, **kwargs) -> Dict[str, Any]:
        pass

    @abstractmethod
    def batch(self, inputs: List[Any], *args, **kwargs) -> List[Any]:
        pass
