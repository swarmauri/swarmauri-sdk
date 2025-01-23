import numpy as np
from typing import List, Literal
from swarmauri.vectors.concrete.Vector import Vector
from swarmauri.distances.base.DistanceBase import DistanceBase


class WeightedHarmonicMetric(DistanceBase):
    """
    Concrete implementation of the IDistanceSimilarity interface using the
    Weighted Harmonic Metric.

    """
    type: Literal['WeightedHarmonicMetric'] = 'WeightedHarmonicMetric'

    def distance(self, vector_a: Vector, vector_b: Vector, weights: List[float]) -> float:
        """
        Computes the Weighted Harmonic Metric distance between two vectors.
        
        Args:
            vector_a (Vector): The first vector in the comparison.
            vector_b (Vector): The second vector in the comparison.
            weights (List[float]): Weights for each dimension.
        
        Returns:
            float: The computed distance.
        """
        data_a = np.array(vector_a.value)
        data_b = np.array(vector_b.value)

        if data_a.shape != data_b.shape or len(weights) != len(data_a):
            raise ValueError("Vectors and weights must have the same dimensionality.")
        
        differences = np.abs(data_a - data_b)
        weighted_distances = 1 / (1 + differences * np.array(weights))
        return np.sum(weighted_distances)

    def distances(self, vector_a: Vector, vectors_b: List[Vector], weights: List[float]) -> List[float]:
        """
        Computes distances from one vector to a list of vectors.
        """
        return [self.distance(vector_a, vector_b, weights) for vector_b in vectors_b]

    def similarity(self, vector_a: Vector, vector_b: Vector, weights: List[float]) -> float:
        """
        Computes a similarity score derived from the Weighted Harmonic Metric.
        
        Args:
            vector_a (Vector): The first vector.
            vector_b (Vector): The second vector.
            weights (List[float]): Weights for each dimension.
        
        Returns:
            float: A similarity score (0 to 1).
        """
        dist = self.distance(vector_a, vector_b, weights)
        return 1 / (1 + dist)

    def similarities(self, vector_a: Vector, vectors_b: List[Vector], weights: List[float]) -> List[float]:
        """
        Computes similarities from one vector to a list of vectors.
        """
        return [self.similarity(vector_a, vector_b, weights) for vector_b in vectors_b]

    def triangle_inequality(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, weights: List[float]) -> bool:
        """
        Validates the triangle inequality for three vectors.
        
        Args:
            vector_a (Vector): The first vector.
            vector_b (Vector): The second vector.
            vector_c (Vector): The third vector.
            weights (List[float]): Weights for each dimension.
        
        Returns:
            bool: True if the inequality holds, False otherwise.
        """
        dist_ab = self.distance(vector_a, vector_b, weights)
        dist_bc = self.distance(vector_b, vector_c, weights)
        dist_ac = self.distance(vector_a, vector_c, weights)

        return dist_ac <= dist_ab + dist_bc
