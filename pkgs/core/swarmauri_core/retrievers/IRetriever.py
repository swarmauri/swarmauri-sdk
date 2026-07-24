from abc import ABC, abstractmethod
from typing import List

from swarmauri_core.documents.IDocument import IDocument


class IRetriever(ABC):
    """Interface for components that retrieve documents for a query."""

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        """Return up to ``top_k`` documents relevant to ``query``."""
        pass
