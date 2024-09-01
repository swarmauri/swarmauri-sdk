from abc import ABC, abstractmethod
from typing import Optional
from pydantic import Field


class IPersistentVectorStore(ABC):
    """
    Interface for a persitent-based vector store responsible for storing, indexing, and retrieving documents.
    """

    collection_name: str
    url: Optional[str] = Field(
        None, description="URL of the persistent-based store to connect to"
    )

    vector_size: Optional[int] = Field(
        None, description="Size of the vectors used in the store"
    )
    client: Optional[object] = Field(
        None,
        description="Client object for interacting with the persistent-based store",
    )

    vectorizer: Optional[object] = Field(
        None, description="Vectorizer object for converting documents to vectors"
    )

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
