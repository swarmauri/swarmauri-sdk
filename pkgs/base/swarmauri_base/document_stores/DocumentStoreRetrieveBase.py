from abc import abstractmethod
from typing import List, Literal

from pydantic import ConfigDict, Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.document_stores.IDocumentRetrieve import IDocumentRetrieve
from swarmauri_core.documents.IDocument import IDocument


@ComponentBase.register_model()
class DocumentStoreRetrieveBase(IDocumentRetrieve, ComponentBase):
    resource: ResourceTypes = Field(default=ResourceTypes.DOCUMENT_STORE.value)
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["DocumentStoreRetrieveBase"] = "DocumentStoreRetrieveBase"

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        """
        Retrieve the top_k most relevant documents based on the given query.

        Args:
            query (str): The query string used for document retrieval.
            top_k (int): The number of top relevant documents to retrieve.

        Returns:
            List[IDocument]: A list of the top_k most relevant documents.
        """
        pass
