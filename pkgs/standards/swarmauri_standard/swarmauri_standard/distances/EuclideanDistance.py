from math import sqrt
from typing import List, Literal
from swarmauri_standard.vectors.Vector import Vector
from swarmauri_base.distances.DistanceBase import DistanceBase

class EuclideanDistance(DistanceBase):
    """
    Class to compute the Euclidean distance between two vectors.
    Implements the IDistanceSimiliarity interface.
    """    
    type: Literal['EuclideanDistance'] = 'EuclideanDistance'
    
    def distance(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes the Euclidean distance between two vectors.

        Args:
            vector_a (Vector): The first vector in the comparison.
            vector_b (Vector): The second vector in the comparison.

        Returns:
            float: The computed Euclidean distance between vector_a and vector_b.
        """
        if len(vector_a.value) != len(vector_b.value):
            raise ValueError("Vectors do not have the same dimensionality.")
        
        distance = sqrt(sum((a - b) ** 2 for a, b in zip(vector_a.value, vector_b.value)))
        return distance

    def similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes the similarity score as the inverse of the Euclidean distance between two vectors.

        Args:
            vector_a (Vector): The first vector in the comparison.
            vector_b (Vector): The second vector in the comparison.

        Returns:
            float: The similarity score between vector_a and vector_b.
        """
        distance = self.distance(vector_a, vector_b)
        return 1 / (1 + distance)
    
    def distances(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities