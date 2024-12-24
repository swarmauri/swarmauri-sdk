from abc import ABC, abstractmethod
from typing import List
from pydantic import BaseModel
from swarmauri_standard.documents.Document import Document
from swarmauri_core.vector_stores.IVectorStoreRetrieve import IVectorStoreRetrieve


class VectorStoreRetrieveMixin(IVectorStoreRetrieve, BaseModel):
    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[Document]:
        """
        Retrieve the top_k most relevant documents based on the given query.

        Args:
            query (str): The query string used for document retrieval.
            top_k (int): The number of top relevant documents to retrieve.

        Returns:
            List[IDocument]: A list of the top_k most relevant documents.
        """
        pass