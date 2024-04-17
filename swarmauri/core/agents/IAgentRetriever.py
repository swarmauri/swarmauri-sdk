from abc import ABC, abstractmethod
from swarmauri.core.document_stores.IDocumentRetrieve import IDocumentRetrieve

class IAgentRetriever(ABC):
    
    @property
    @abstractmethod
    def retriever(self) -> IDocumentRetrieve:
        pass

    @retriever.setter
    @abstractmethod
    def retriever(self) -> IDocumentRetrieve:
        pass