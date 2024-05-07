from abc import ABC, abstractmethod
from typing import List
from swarmauri.core.documents.IDocument import IDocument

class IAgentRetrieve(ABC):

    @property
    @abstractmethod
    def last_retrieved(self) -> List[IDocument]:
        pass

    @last_retrieved.setter
    @abstractmethod
    def last_retrieved(self) -> List[IDocument]:
        pass