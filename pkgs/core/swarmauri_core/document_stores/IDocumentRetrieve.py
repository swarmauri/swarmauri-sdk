from abc import ABC, abstractmethod
from typing import List
from swarmauri_core.documents.IDocument import IDocument

class IDocumentRetrieve(ABC):
    """
    Abstract base class for document retrieval operations.
    
    This class defines the interface for retrieving documents based on a query or other criteria.
    Implementations may use various indexing or search technologies to fulfill these retrievals.
    """

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        """
        Retrieve the most relevant documents based on the given query.
        
        Parameters:
            query (str): The query string used for document retrieval.
            top_k (int): The number of top relevant documents to retrieve.
            
        Returns:
            List[Document]: A list of the top_k most relevant documents.
        """
        pass