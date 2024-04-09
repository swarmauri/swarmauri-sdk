from abc import ABC, abstractmethod
from swarmauri.core.document_stores.IDocumentRetriever import IDocumentRetriever 

class IAgentRetriever(ABC):
    
    @property
    @abstractmethod
    def retriever(self) -> IDocumentRetriever:
        pass

    @retriever.setter
    @abstractmethod
    def retriever(self) -> IDocumentRetriever:
        pass