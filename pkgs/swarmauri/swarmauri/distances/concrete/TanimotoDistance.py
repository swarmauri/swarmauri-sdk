import numpy as np
from typing import List, Literal
from swarmauri.vectors.concrete.Vector import Vector
from swarmauri.distances.base.DistanceBase import DistanceBase

class TanimotoDistance(DistanceBase):
    """
    Concrete implementation of the IDistanceSimilarity interface using the Tanimoto Distance metric.
    This class processes Vector instances to compute the Tanimoto Distance.
    """
    type: Literal['TanimotoDistance'] = 'TanimotoDistance'

    def distance(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes the Tanimoto Distance between two Vector instances.

        Args:
            vector_a (Vector): The first vector in the comparison.
            vector_b (Vector): The second vector in the comparison.

        Returns:
            float: The computed Tanimoto Distance between the vectors.

        Raises:
            ValueError: If the input vectors are None, empty, or contain negative values.
        """
        if vector_a is None or vector_b is None:
            raise ValueError("Input vectors cannot be None.")
        if not vector_a.value or not vector_b.value:
            raise ValueError("Input vectors cannot be empty.")

        # Extract data from Vector
        data_a = np.array(vector_a.value)
        data_b = np.array(vector_b.value)

        # Checking dimensions match
        if data_a.shape != data_b.shape:
            raise ValueError("Vectors must have the same dimensionality.")

        # Check if vectors contain only non-negative values
        if np.any(data_a < 0) or np.any(data_b < 0):
            raise ValueError("Tanimoto Distance is defined only for non-negative values.")

        # Compute dot products and squared norms
        dot_product = np.dot(data_a, data_b)
        norm_a = np.sum(data_a ** 2)
        norm_b = np.sum(data_b ** 2)

        # Compute Tanimoto Coefficient
        denominator = norm_a + norm_b - dot_product
        if denominator == 0:
            return 0.0  # If both vectors are zero, define distance as 0.

        tanimoto_coefficient = dot_product / denominator

        # Compute Tanimoto Distance
        distance = 1 - tanimoto_coefficient

        return distance

    def distances(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        """
        Computes the distances between the input vector and a list of vectors.

        Args:
            vector_a (Vector): The vector to compare with the list of vectors.
            vectors_b (List[Vector]): The list of vectors to compare with the input vector.

        Returns:
            List[float]: A list of Tanimoto distances between the input vector and each vector in the list.
        """
        return [self.distance(vector_a, vector_b) for vector_b in vectors_b]

    def similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes the Tanimoto similarity between two Vector instances. Similarity is defined as 1 - distance.

        Args:
            vector_a (Vector): The first vector in the comparison.
            vector_b (Vector): The second vector to compare with the first vector.

        Returns:
            float: A similarity score between vector_a and vector_b.

        Raises:
            ValueError: If the input vectors are None, empty, or contain negative values.
        """
        return 1 - self.distance(vector_a, vector_b)

    def similarities(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        """
        Computes the similarities between the input vector and a list of vectors using the Tanimoto Distance metric.

        Args:
            vector_a (Vector): The vector to compare with the list of vectors.
            vectors_b (List[Vector]): The list of vectors to compare with the input vector.

        Returns:
            List[float]: A list of Tanimoto similarities between the input vector and each vector in the list.
        """
        return [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
