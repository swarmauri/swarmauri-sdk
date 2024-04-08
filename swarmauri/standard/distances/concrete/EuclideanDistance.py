from math import sqrt
from typing import List
from swarmauri.core.distances.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector


class EuclideanDistance(IDistanceSimilarity):
    """
    Class to compute the Euclidean distance between two vectors.
    Implements the IDistanceSimiliarity interface.
    """

    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the Euclidean distance between two vectors.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector in the comparison.

        Returns:
            float: The computed Euclidean distance between vector_a and vector_b.
        """
        if len(vector_a.data) != len(vector_b.data):
            raise ValueError("Vectors do not have the same dimensionality.")
        
        distance = sqrt(sum((a - b) ** 2 for a, b in zip(vector_a.data, vector_b.data)))
        return distance

    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the similarity score as the inverse of the Euclidean distance between two vectors.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector in the comparison.

        Returns:
            float: The similarity score between vector_a and vector_b.
        """
        distance = self.distance(vector_a, vector_b)
        return 1 / (1 + distance)
    
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities