from abc import ABC, abstractmethod
from typing import List
import warnings
from swarmauri_core.vectors.IVector import IVector


warnings.warn(
    "IDistanceSimilarity is deprecated and will be removed from the active Swarmauri workspace by v0.12.0.",
    DeprecationWarning,
    stacklevel=2,
)


class IDistanceSimilarity(ABC):
    """
    Deprecated compatibility interface for computing both distances and similarities.

    New code should use mathematically precise families such as metrics and
    similarities, plus vector-store comparators for ranking behavior.
    """

    @abstractmethod
    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the distance between two vectors.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector in the comparison.

        Returns:
            float: The computed distance between vector_a and vector_b.
        """
        pass

    @abstractmethod
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> float:
        pass

    @abstractmethod
    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Compute the similarity between two vectors. The definition of similarity (e.g., cosine similarity)
        should be implemented in concrete classes.

        Args:
            vector_a (IVector): The first vector.
            vector_b (IVector): The second vector to compare with the first vector.

        Returns:
            float: A similarity score between vector_a and vector_b.
        """
        pass

    @abstractmethod
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> float:
        pass
