from abc import ABC, abstractmethod


class IPersistentVectorStore(ABC):
    """
    Interface for a persitent-based vector store responsible for storing, indexing, and retrieving documents.
    """

    @abstractmethod
    def connect(self) -> None:
        """
        Connects to the persistent-based vector store using provided credentials.
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """
        Disconnects from the persistent-based vector store.
        """
        pass
