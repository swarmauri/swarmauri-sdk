import numpy as np
from typing import List, Literal
from swarmauri.vectors.concrete.Vector import Vector
from swarmauri.distances.base.DistanceBase import DistanceBase

class WassersteinDistance(DistanceBase):
    """
    Concrete implementation of the IDistanceSimilarity interface using the Wasserstein (Earth Mover's) Distance metric.
    This class processes Vector instances to compute the Wasserstein Distance.
    """
    type: Literal['WassersteinDistance'] = 'WassersteinDistance'

    def distance(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes the Wasserstein Distance between two Vector instances.

        Args:
            vector_a (Vector): The first vector in the comparison.
            vector_b (Vector): The second vector in the comparison.

        Returns:
            float: The computed Wasserstein Distance between the vectors.

        Raises:
            ValueError: If the input vectors are None or empty.
        """
        if vector_a is None or vector_b is None:
            raise ValueError("Input vectors cannot be None.")
        if not vector_a.value or not vector_b.value:
            raise ValueError("Input vectors cannot be empty.")

        # Extract data from Vector and sort them
        data_a = np.sort(np.array(vector_a.value))
        data_b = np.sort(np.array(vector_b.value))

        # Ensure the vectors have the same length for simplicity
        if len(data_a) != len(data_b):
            raise ValueError("Vectors must have the same length for 1-dimensional Wasserstein distance.")

        # Compute cumulative distributions
        cum_a = np.cumsum(data_a) / np.sum(data_a)
        cum_b = np.cumsum(data_b) / np.sum(data_b)

        # Calculate the Wasserstein Distance as the sum of absolute differences
        wasserstein_distance = np.sum(np.abs(cum_a - cum_b)) / len(data_a)

        return wasserstein_distance

    def distances(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        """
        Computes the distances between the input vector and a list of vectors.

        Args:
            vector_a (Vector): The vector to compare with the list of vectors.
            vectors_b (List[Vector]): The list of vectors to compare with the input vector.

        Returns:
            List[float]: A list of Wasserstein distances between the input vector and each vector in the list.
        """
        return [self.distance(vector_a, vector_b) for vector_b in vectors_b]

    def similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Compute similarity using the Wasserstein Distance. Since this distance metric isn't
        directly interpretable as a similarity, a transformation is applied to map the distance
        to a similarity score.

        Args:
            vector_a (Vector): The first vector in the comparison.
            vector_b (Vector): The second vector to compare with the first vector.

        Returns:
            float: A similarity score between vector_a and vector_b.

        Raises:
            ValueError: If the input vectors are None or empty.
        """
        # Compute the Wasserstein distance
        distance = self.distance(vector_a, vector_b)

        # Transform the distance into a similarity score
        # Using an exponential decay transformation for similarity
        similarity = np.exp(-distance)

        return similarity

    def similarities(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        """
        Computes the similarities between the input vector and a list of vectors using the Wasserstein Distance metric.

        Args:
            vector_a (Vector): The vector to compare with the list of vectors.
            vectors_b (List[Vector]): The list of vectors to compare with the input vector.

        Returns:
            List[float]: A list of similarities between the input vector and each vector in the list.
        """
        return [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
