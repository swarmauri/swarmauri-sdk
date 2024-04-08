from abc import ABC, abstractmethod
from typing import Dict
from swarmauri.core.vectors.IVector import IVector

class IEmbed(ABC):
    @property
    @abstractmethod
    def embedding(self) -> IVector:
        """
        Get the document's embedding.
        """
        pass

    @embedding.setter
    @abstractmethod
    def embedding(self, value: IVector) -> None:
        """
        Set the document's embedding.
        """
        pass

