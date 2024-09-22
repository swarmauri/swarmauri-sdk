from abc import ABC, abstractmethod
from typing import Dict, Any

class IChainContext(ABC):
    
    @abstractmethod
    def update(self, **kwargs) -> None:
        pass

    def get_value(self, key: str) -> Any:
        pass