import numpy as np
from typing import List, Literal
from swarmauri.vectors.concrete.Vector import Vector
from swarmauri.distances.base.DistanceBase import DistanceBase


class AdaptiveWeightedMetric(DistanceBase):
    """
    Concrete implementation of the IDistanceSimilarity interface using the
    Adaptive Weighted Metric.
    """
    type: Literal['AdaptiveWeightedMetric'] = 'AdaptiveWeightedMetric'

    def distance(self, vector_a: Vector, vector_b: Vector, alphas: List[float]) -> float:
        """
        Computes the Adaptive Weighted Metric distance between two vectors.
        
        Args:
            vector_a (Vector): The first vector in the comparison.
            vector_b (Vector): The second vector in the comparison.
            alphas (List[float]): Adaptive weights for each dimension.
        
        Returns:
            float: The computed distance.
        """
        data_a = np.array(vector_a.value)
        data_b = np.array(vector_b.value)

        if data_a.shape != data_b.shape or len(alphas) != len(data_a):
            raise ValueError("Vectors and weights must have the same dimensionality.")
        
        differences = np.abs(data_a - data_b)
        weighted_distances = differences / (1 + alphas * np.abs(data_a))
        return np.sum(weighted_distances)

    def distances(self, vector_a: Vector, vectors_b: List[Vector], alphas: List[float]) -> List[float]:
        """
        Computes distances from one vector to a list of vectors.
        """
        return [self.distance(vector_a, vector_b, alphas) for vector_b in vectors_b]

    def similarity(self, vector_a: Vector, vector_b: Vector, alphas: List[float]) -> float:
        """
        Computes a similarity score derived from the Adaptive Weighted Metric.
        
        Args:
            vector_a (Vector): The first vector.
            vector_b (Vector): The second vector.
            alphas (List[float]): Adaptive weights for each dimension.
        
        Returns:
            float: A similarity score (0 to 1).
        """
        dist = self.distance(vector_a, vector_b, alphas)
        return 1 / (1 + dist)

    def similarities(self, vector_a: Vector, vectors_b: List[Vector], alphas: List[float]) -> List[float]:
        """
        Computes similarities from one vector to a list of vectors.
        """
        return [self.similarity(vector_a, vector_b, alphas) for vector_b in vectors_b]

    def triangle_inequality(self, vector_a: Vector, vector_b: Vector, vector_c: Vector, alphas: List[float]) -> bool:
        """
        Validates the triangle inequality for three vectors.
        
        Args:
            vector_a (Vector): The first vector.
            vector_b (Vector): The second vector.
            vector_c (Vector): The third vector.
            alphas (List[float]): Adaptive weights for each dimension.
        
        Returns:
            bool: True if the inequality holds, False otherwise.
        """
        dist_ab = self.distance(vector_a, vector_b, alphas)
        dist_bc = self.distance(vector_b, vector_c, alphas)
        dist_ac = self.distance(vector_a, vector_c, alphas)

        return dist_ac <= dist_ab + dist_bc

    def check_non_negativity(self, vector_a: Vector, vector_b: Vector, alphas: List[float]) -> bool:
        """
        Validates the non-negativity property of the metric.
        """
        distance = self.distance(vector_a, vector_b, alphas)
        return distance >= 0

    def check_identity_of_indiscernibles(self, vector_a: Vector, vector_b: Vector, alphas: List[float]) -> bool:
        """
        Validates the identity of indiscernibles property of the metric.
        """
        distance = self.distance(vector_a, vector_b, alphas)
        if vector_a.value == vector_b.value:
            return distance == 0
        else:
            return distance > 0

    def check_symmetry(self, vector_a: Vector, vector_b: Vector, alphas: List[float]) -> bool:
        """
        Validates the symmetry property of the metric.
        """
        distance_ab = self.distance(vector_a, vector_b, alphas)
        distance_ba = self.distance(vector_b, vector_a, alphas)
        return distance_ab == distance_ba

    def check_positivity(self, vector_a: Vector, vector_b: Vector, alphas: List[float]) -> bool:
        """
        Validates the positivity (separation) property of the metric.
        """
        if vector_a.value == vector_b.value:
            return self.distance(vector_a, vector_b, alphas) == 0
        else:
            return self.distance(vector_a, vector_b, alphas) > 0
