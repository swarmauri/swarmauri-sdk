from abc import ABC, abstractmethod
from typing import Dict, Any


class ITool(ABC):
    @abstractmethod
    def call(self, *args, **kwargs):
        pass

    @abstractmethod
    def __call__(self, *args, **kwargs) -> Dict[str, Any]:
        pass
