from abc import ABC, abstractmethod
from swarmauri.core.document_stores.IDocumentStore import IDocumentStore

class IAgentDocumentStore(ABC):
    
    @property
    @abstractmethod
    def document_store(self) -> IDocumentStore:
        pass

    @document_store.setter
    @abstractmethod
    def document_store(self) -> IDocumentStore:
        pass