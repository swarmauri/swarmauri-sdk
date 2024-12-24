from abc import ABC, abstractmethod
from typing import List
from swarmauri_core.document_stores.IDocumentRetrieve import IDocumentRetrieve
from swarmauri_core.documents.IDocument import IDocument
from swarmauri_base.document_stores.DocumentStoreBase import DocumentStoreBase

class DocumentStoreRetrieveBase(DocumentStoreBase, IDocumentRetrieve, ABC):

        
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