from abc import ABC, abstractmethod

class IAgentVectorStore(ABC):
    
    @property
    @abstractmethod
    def vector_store(self):
        pass

    @vector_store.setter
    @abstractmethod
    def vector_store(self):
        pass