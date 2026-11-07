from abc import abstractmethod
from typing import Literal

from pydantic import Field
from swarmauri_core.documents.IDocument import IDocument
from swarmauri_core.retrievers.IRetriever import IRetriever

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class RetrieverBase(IRetriever, ComponentBase):
    """Base class for document retrievers."""

    resource: str | None = Field(default=ResourceTypes.RETRIEVER.value)
    type: Literal["RetrieverBase"] = "RetrieverBase"

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> list[IDocument]:
        """Return up to ``top_k`` documents relevant to ``query``."""
