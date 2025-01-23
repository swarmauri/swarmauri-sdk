import numpy as np
from typing import List, Literal
from swarmauri.vectors.concrete.Vector import Vector
from swarmauri.distances.base.DistanceBase import DistanceBase


class GeneralizedCosineMetric(DistanceBase):
    """
    Concrete implementation of the IDistanceSimilarity interface using the
    Generalized Cosine Metric.
    """
    type: Literal['GeneralizedCosineMetric'] = 'GeneralizedCosineMetric'

    def distance(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes the Generalized Cosine Metric distance between two vectors.
        
        Args:
            vector_a (Vector): The first vector in the comparison.
            vector_b (Vector): The second vector in the comparison.
        
        Returns:
            float: The computed distance.
        """
        data_a = np.array(vector_a.value)
        data_b = np.array(vector_b.value)

        if data_a.shape != data_b.shape:
            raise ValueError("Vectors must have the same dimensionality.")
        
        total_difference = np.sum(np.abs(data_a - data_b))
        distance = 1 - np.cos(total_difference)
        return distance

    def distances(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        """
        Computes distances from one vector to a list of vectors.
        """
        return [self.distance(vector_a, vector_b) for vector_b in vectors_b]

    def similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes a similarity score derived from the Generalized Cosine Metric.
        
        Args:
            vector_a (Vector): The first vector.
            vector_b (Vector): The second vector.
        
        Returns:
            float: A similarity score (0 to 1).
        """
        dist = self.distance(vector_a, vector_b)
        return 1 / (1 + dist)

    def similarities(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        """
        Computes similarities from one vector to a list of vectors.
        """
        return [self.similarity(vector_a, vector_b) for vector_b in vectors_b]

    def triangle_inequality(self, vector_a: Vector, vector_b: Vector, vector_c: Vector) -> bool:
        """
        Validates the triangle inequality for three vectors.
        
        Args:
            vector_a (Vector): The first vector.
            vector_b (Vector): The second vector.
            vector_c (Vector): The third vector.
        
        Returns:
            bool: True if the inequality holds, False otherwise.
        """
        dist_ab = self.distance(vector_a, vector_b)
        dist_bc = self.distance(vector_b, vector_c)
        dist_ac = self.distance(vector_a, vector_c)

        return dist_ac <= dist_ab + dist_bc
