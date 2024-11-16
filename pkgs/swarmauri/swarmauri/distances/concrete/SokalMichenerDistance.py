import numpy as np
from typing import List, Literal
from swarmauri.vectors.concrete.Vector import Vector
from swarmauri.distances.base.DistanceBase import DistanceBase

class SokalMichenerDistance(DistanceBase):
    """
    Concrete implementation of the IDistanceSimilarity interface using the Sokal-Michener Distance metric.
    This class processes Vector instances to compute the Sokal-Michener Distance.
    """
    type: Literal['SokalMichenerDistance'] = 'SokalMichenerDistance'

    def distance(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes the Sokal-Michener Distance between two binary Vector instances.

        Args:
            vector_a (Vector): The first vector in the comparison.
            vector_b (Vector): The second vector in the comparison.

        Returns:
            float: The computed Sokal-Michener Distance between the vectors.

        Raises:
            ValueError: If the input vectors are None, empty, or not binary.
        """
        if vector_a is None or vector_b is None:
            raise ValueError("Input vectors cannot be None.")
        if not vector_a.value or not vector_b.value:
            raise ValueError("Input vectors cannot be empty.")

        # Extract data from Vector
        data_a = np.array(vector_a.value, dtype=np.int32)
        data_b = np.array(vector_b.value, dtype=np.int32)

        # Checking dimensions match
        if data_a.shape != data_b.shape:
            raise ValueError("Vectors must have the same dimensionality.")

        # Ensure binary vectors
        if not np.all((data_a == 0) | (data_a == 1)) or not np.all((data_b == 0) | (data_b == 1)):
            raise ValueError("Vectors must be binary (0 or 1).")

        # Compute agreements and disagreements
        a = np.sum((data_a == 1) & (data_b == 1))  # Both 1
        d = np.sum((data_a == 0) & (data_b == 0))  # Both 0
        b = np.sum((data_a == 1) & (data_b == 0))  # 1 in a, 0 in b
        c = np.sum((data_a == 0) & (data_b == 1))  # 0 in a, 1 in b

        # Compute Sokal-Michener Distance
        total = a + b + c + d
        if total == 0:
            return 0.0  # If vectors are all zeros, consider them identical.
        distance = 1 - (a + d) / total

        return distance

    def distances(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        """
        Computes the distances between the input vector and a list of vectors.

        Args:
            vector_a (Vector): The vector to compare with the list of vectors.
            vectors_b (List[Vector]): The list of vectors to compare with the input vector.

        Returns:
            List[float]: A list of Sokal-Michener distances between the input vector and each vector in the list.
        """
        return [self.distance(vector_a, vector_b) for vector_b in vectors_b]

    def similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes the Sokal-Michener similarity between two Vector instances. Similarity is defined as 1 - distance.

        Args:
            vector_a (Vector): The first vector in the comparison.
            vector_b (Vector): The second vector to compare with the first vector.

        Returns:
            float: A similarity score between vector_a and vector_b.

        Raises:
            ValueError: If the input vectors are None, empty, or not binary.
        """
        return 1 - self.distance(vector_a, vector_b)

    def similarities(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        """
        Computes the similarities between the input vector and a list of vectors using the Sokal-Michener Distance metric.

        Args:
            vector_a (Vector): The vector to compare with the list of vectors.
            vectors_b (List[Vector]): The list of vectors to compare with the input vector.

        Returns:
            List[float]: A list of Sokal-Michener similarities between the input vector and each vector in the list.
        """
        return [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
