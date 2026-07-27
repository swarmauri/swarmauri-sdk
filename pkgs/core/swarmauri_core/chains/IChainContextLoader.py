from abc import ABC, abstractmethod
from typing import Any, Dict


class IChainContextLoader(ABC):
    @abstractmethod
    def load_context(self, context_id: str) -> dict[str, Any]:
        """Load the execution context by its identifier."""
