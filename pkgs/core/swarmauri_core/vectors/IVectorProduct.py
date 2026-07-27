from abc import ABC, abstractmethod
from typing import List


class IVectorProduct(ABC):
    """
    Interface for various vector products including dot product, cross product,
    and triple products (vector and scalar).
    """

    @abstractmethod
    def dot_product(
        self, vector_a: list[float], vector_b: list[float]
    ) -> float:
        """
        Calculate the dot product of two vectors.

        Parameters:
        - vector_a (List[float]): The first vector.
        - vector_b (List[float]): The second vector.

        Returns:
        - float: The dot product of the two vectors.
        """

    @abstractmethod
    def cross_product(
        self, vector_a: list[float], vector_b: list[float]
    ) -> list[float]:
        """
        Calculate the cross product of two vectors.

        Parameters:
        - vector_a (List[float]): The first vector.
        - vector_b (List[float]): The second vector.

        Returns:
        - List[float]: The cross product as a new vector.
        """

    @abstractmethod
    def vector_triple_product(
        self,
        vector_a: list[float],
        vector_b: list[float],
        vector_c: list[float],
    ) -> list[float]:
        """
        Calculate the vector triple product of three vectors.

        Parameters:
        - vector_a (List[float]): The first vector.
        - vector_b (List[float]): The second vector.
        - vector_c (List[float]): The third vector.

        Returns:
        - List[float]: The result of the vector triple product as a new vector.
        """

    @abstractmethod
    def scalar_triple_product(
        self,
        vector_a: list[float],
        vector_b: list[float],
        vector_c: list[float],
    ) -> float:
        """
        Calculate the scalar triple product of three vectors.

        Parameters:
        - vector_a (List[float]): The first vector.
        - vector_b (List[float]): The second vector.
        - vector_c (List[float]): The third vector.

        Returns:
        - float: The scalar value result of the scalar triple product.
        """
