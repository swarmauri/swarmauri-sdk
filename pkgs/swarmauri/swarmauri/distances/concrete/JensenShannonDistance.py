import numpy as np
from typing import List, Literal
from swarmauri.vectors.concrete.Vector import Vector
from swarmauri.distances.base.DistanceBase import DistanceBase

class JensenShannonDistance(DistanceBase):
    """
    Concrete implementation of the IDistanceSimilarity interface using the Jensen-Shannon Distance metric.
    This class processes Vector instances to compute the Jensen-Shannon Distance.
    """
    type: Literal['JensenShannonDistance'] = 'JensenShannonDistance'

    def _kl_divergence(self, p: np.ndarray, q: np.ndarray) -> float:
        """
        Helper function to compute the Kullback-Leibler divergence between two probability distributions.

        Args:
            p (np.ndarray): First probability distribution.
            q (np.ndarray): Second probability distribution.

        Returns:
            float: KL divergence value.
        """
        # Avoid log(0) and division by 0; use np.where to safely handle zeros
        return np.sum(np.where(p != 0, p * np.log(p / q), 0))

    def distance(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes the Jensen-Shannon Distance between two Vector instances.

        Args:
            vector_a (Vector): The first vector in the comparison.
            vector_b (Vector): The second vector in the comparison.

        Returns:
            float: The computed Jensen-Shannon Distance between the vectors.

        Raises:
            ValueError: If the input vectors are None, empty, or not valid probability distributions.
        """
        if vector_a is None or vector_b is None:
            raise ValueError("Input vectors cannot be None.")
        if not vector_a.value or not vector_b.value:
            raise ValueError("Input vectors cannot be empty.")

        # Extract data from Vector
        p = np.array(vector_a.value, dtype=np.float64)
        q = np.array(vector_b.value, dtype=np.float64)

        # Normalize to ensure valid probability distributions
        p /= np.sum(p)
        q /= np.sum(q)

        # Ensure non-negative values (probabilities must be >= 0)
        if np.any(p < 0) or np.any(q < 0):
            raise ValueError("Vectors must contain non-negative values for Jensen-Shannon Distance.")

        # Compute M = (P + Q) / 2
        m = 0.5 * (p + q)

        # Compute Jensen-Shannon Divergence
        js_divergence = 0.5 * self._kl_divergence(p, m) + 0.5 * self._kl_divergence(q, m)

        # Jensen-Shannon Distance is the square root of divergence
        return np.sqrt(js_divergence)

    def distances(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        """
        Computes the distances between the input vector and a list of vectors.

        Args:
            vector_a (Vector): The vector to compare with the list of vectors.
            vectors_b (List[Vector]): The list of vectors to compare with the input vector.

        Returns:
            List[float]: A list of Jensen-Shannon distances between the input vector and each vector in the list.
        """
        return [self.distance(vector_a, vector_b) for vector_b in vectors_b]

    def similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes the Jensen-Shannon similarity between two Vector instances. Similarity is defined as 1 - distance.

        Args:
            vector_a (Vector): The first vector in the comparison.
            vector_b (Vector): The second vector to compare with the first vector.

        Returns:
            float: A similarity score between vector_a and vector_b.

        Raises:
            ValueError: If the input vectors are None, empty, or not valid probability distributions.
        """
        return 1 - self.distance(vector_a, vector_b)

    def similarities(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        """
        Computes the similarities between the input vector and a list of vectors using the Jensen-Shannon Distance metric.

        Args:
            vector_a (Vector): The vector to compare with the list of vectors.
            vectors_b (List[Vector]): The list of vectors to compare with the input vector.

        Returns:
            List[float]: A list of Jensen-Shannon similarities between the input vector and each vector in the list.
        """
        return [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
