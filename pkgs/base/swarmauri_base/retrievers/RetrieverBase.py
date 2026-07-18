from abc import abstractmethod
from typing import List, Literal, Optional

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.documents.IDocument import IDocument
from swarmauri_core.retrievers.IRetriever import IRetriever


@ComponentBase.register_model()
class RetrieverBase(IRetriever, ComponentBase):
    """Base class for document retrievers."""

    resource: Optional[str] = Field(default=ResourceTypes.RETRIEVER.value)
    type: Literal["RetrieverBase"] = "RetrieverBase"

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        """Return up to ``top_k`` documents relevant to ``query``."""
        pass
