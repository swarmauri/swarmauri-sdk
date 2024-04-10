from abc import ABC, abstractmethod
from swarmauri.core.vector_stores.IVectorStore import IVectorStore

class IAgentVectorStore(ABC):
    
    @property
    @abstractmethod
    def vector_store(self) -> IVectorStore:
        pass

    @vector_store.setter
    @abstractmethod
    def vector_store(self) -> IVectorStore:
        pass