from abc import ABC, abstractmethod
from typing import List
from swarmauri_core.vectors.IVector import IVector


class IMetric(ABC):
    """
    Interface for computing distances and similarities between high-dimensional data vectors. This interface
    abstracts the method for calculating the distance and similarity, allowing for the implementation of various 
    distance metrics such as Euclidean, Manhattan, Cosine similarity, etc.
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
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        """
        Computes distances from one vector to a list of vectors.

        Args:
            vector_a (IVector): The reference vector.
            vectors_b (List[IVector]): A list of vectors to compute distances to.

        Returns:
            List[float]: A list of distances.
        """
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
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        """
        Computes similarities from one vector to a list of vectors.

        Args:
            vector_a (IVector): The reference vector.
            vectors_b (List[IVector]): A list of vectors to compute similarities to.

        Returns:
            List[float]: A list of similarity scores.
        """
        pass

    @abstractmethod
    def check_triangle_inequality(self, vector_a: IVector, vector_b: IVector, vector_c: IVector) -> bool:
        """
        Validates the triangle inequality property for three vectors.

        Args:
            vector_a (IVector): The first vector.
            vector_b (IVector): The second vector.
            vector_c (IVector): The third vector.

        Returns:
            bool: True if the triangle inequality holds, False otherwise.
        """
        pass

    @abstractmethod
    def check_non_negativity(self, vector_a: IVector, vector_b: IVector) -> bool:
        """
        Validates the non-negativity property of the metric.

        Args:
            vector_a (IVector): The first vector.
            vector_b (IVector): The second vector.

        Returns:
            bool: True if the non-negativity property holds, False otherwise.
        """
        pass

    @abstractmethod
    def check_identity_of_indiscernibles(self, vector_a: IVector, vector_b: IVector) -> bool:
        """
        Validates the identity of indiscernibles property of the metric.

        Args:
            vector_a (IVector): The first vector.
            vector_b (IVector): The second vector.

        Returns:
            bool: True if the identity of indiscernibles property holds, False otherwise.
        """
        pass

    @abstractmethod
    def check_symmetry(self, vector_a: IVector, vector_b: IVector) -> bool:
        """
        Validates the symmetry property of the metric.

        Args:
            vector_a (IVector): The first vector.
            vector_b (IVector): The second vector.

        Returns:
            bool: True if the symmetry property holds, False otherwise.
        """
        pass

    @abstractmethod
    def check_positivity(self, vector_a: IVector, vector_b: IVector) -> bool:
        """
        Validates the positivity (separation) property of the metric.

        Args:
            vector_a (IVector): The first vector.
            vector_b (IVector): The second vector.

        Returns:
            bool: True if the positivity property holds, False otherwise.
        """
        pass
