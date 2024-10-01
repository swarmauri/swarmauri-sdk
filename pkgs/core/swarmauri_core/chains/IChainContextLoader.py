from abc import ABC, abstractmethod
from typing import Dict, Any

class IChainContextLoader(ABC):
    @abstractmethod
    def load_context(self, context_id: str) -> Dict[str, Any]:
        """Load the execution context by its identifier."""
        pass