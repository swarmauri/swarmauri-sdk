from abc import ABC, abstractmethod
from typing import Dict

class IDocument(ABC):
    @abstractmethod
    def __init__(self, id: str, content: str, metadata: Dict):
        pass

    @property
    @abstractmethod
    def id(self) -> str:
        """
        Get the document's ID.
        """
        pass

    @id.setter
    @abstractmethod
    def id(self, value: str) -> None:
        """
        Set the document's ID.
        """
        pass

    @property
    @abstractmethod
    def content(self) -> str:
        """
        Get the document's content.
        """
        pass

    @content.setter
    @abstractmethod
    def content(self, value: str) -> None:
        """
        Set the document's content.
        """
        pass

    @property
    @abstractmethod
    def metadata(self) -> Dict:
        """
        Get the document's metadata.
        """
        pass

    @metadata.setter
    @abstractmethod
    def metadata(self, value: Dict) -> None:
        """
        Set the document's metadata.
        """
        pass

    # Including the abstract methods __str__ and __repr__ definitions for completeness.
    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass
    
    def __setitem__(self, key, value):
        """Allow setting items like a dict for metadata."""
        self.metadata[key] = value

    def __getitem__(self, key):
        """Allow getting items like a dict for metadata."""
        return self.metadata.get(key)