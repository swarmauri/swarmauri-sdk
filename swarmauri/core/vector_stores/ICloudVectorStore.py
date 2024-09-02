from abc import ABC, abstractmethod


class ICloudVectorStore(ABC):
    """
    Interface for a cloud-based vector store responsible for storing, indexing, and retrieving documents.
    """

    @abstractmethod
    def connect(self) -> None:
        """
        Connects to the cloud-based vector store using provided credentials.
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """
        Disconnects from the cloud-based vector store.
        """
        pass
