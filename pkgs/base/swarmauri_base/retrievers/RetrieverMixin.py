from abc import abstractmethod
from typing import List

from pydantic import BaseModel
from swarmauri_core.documents.IDocument import IDocument
from swarmauri_core.retrievers.IRetriever import IRetriever


class RetrieverMixin(IRetriever, BaseModel):
    """Composable retrieval contract for document-owning components."""

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        """Return up to ``top_k`` documents relevant to ``query``."""
        pass
