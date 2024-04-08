from abc import ABC, abstractmethod
from typing import List, Dict, Union
from ..vectors.IVector import IVector

class IVectorStore(ABC):
    """
    Interface for a vector store that allows the storage, retrieval,
    and management of high-dimensional vector data used in search and machine learning applications.
    """

    @abstractmethod
    def add_vector(self, vector_id: str, vector: IVector, metadata: Dict = None) -> None:
        """
        Store a vector along with its identifier and optional metadata.

        Args:
            vector_id (str): Unique identifier for the vector.
            vector (List[float]): The high-dimensional vector to be stored.
            metadata (Dict, optional): Optional metadata related to the vector.
        """
        pass

    @abstractmethod
    def get_vector(self, vector_id: str) -> Union[List[float], None]:
        """
        Retrieve a vector by its identifier.

        Args:
            vector_id (str): The unique identifier for the vector.

        Returns:
            Union[List[float], None]: The vector associated with the given ID, or None if not found.
        """
        pass

    @abstractmethod
    def delete_vector(self, vector_id: str) -> None:
        """
        Delete a vector by its identifier.

        Args:
            vector_id (str): The unique identifier for the vector to be deleted.
        """
        pass

    @abstractmethod
    def update_vector(self, vector_id: str, new_vector: IVector, new_metadata: Dict = None) -> None:
        """
        Update the vector and metadata for a given vector ID.

        Args:
            vector_id (str): The unique identifier for the vector to update.
            new_vector (List[float]): The new vector data to store.
            new_metadata (Dict, optional): Optional new metadata related to the vector.
        """
        pass