from abc import ABC, abstractmethod
from swarmauri.core.retrievers.IRetriever import IRetriever 

class IAgentRetriever(ABC):
    
    @property
    @abstractmethod
    def retriever(self) -> IRetriever:
        pass

    @retriever.setter
    @abstractmethod
    def retriever(self) -> IRetriever:
        pass