from abc import ABC, abstractmethod
from swarmauri.core.documents.IDocument import IDocument

class IAgentRetrieve(ABC):
    
    @property
    @abstractmethod
    def retrieve(self) -> List[IDocument]:
        pass

    @retriever.setter
    @abstractmethod
    def retrieve(self) -> List[IDocument]:
        pass

    @property
    @abstractmethod
    def last_retrieved(self) -> List[IDocument]:
        pass

    @last_retrieved.setter
    @abstractmethod
    def last_retrieved(self) -> List[IDocument]:
        pass