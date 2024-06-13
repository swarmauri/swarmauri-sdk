from typing import List

from swarmauri.standard.vectors.concrete.Vector import Vector
from swarmauri.standard.distances.base.DistanceBase import DistanceBase

class ChiSquaredDistance(DistanceBase):
    """
    Implementation of the IDistanceSimilarity interface using Chi-squared distance metric.
    """

    def distance(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes the Chi-squared distance between two vectors.
        """
        if len(vector_a.data) != len(vector_b.data):
            raise ValueError("Vectors must have the same dimensionality.")

        chi_squared_distance = 0
        for a, b in zip(vector_a.data, vector_b.data):
            if (a + b) != 0:
                chi_squared_distance += (a - b) ** 2 / (a + b)

        return 0.5 * chi_squared_distance

    def similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Compute the similarity between two vectors based on the Chi-squared distance.
        """
        return 1 / (1 + self.distance(vector_a, vector_b))
    
    def distances(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities

