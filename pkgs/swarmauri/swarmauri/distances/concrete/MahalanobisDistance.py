import numpy as np
from typing import List, Literal
from swarmauri.vectors.concrete.Vector import Vector
from swarmauri.distances.base.DistanceBase import DistanceBase


class MahalanobisDistance(DistanceBase):
    """
    Concrete implementation of the IDistanceSimiliarity interface using the Mahalanobis distance metric.
    This class processes Vector instances with covariance matrices instead of raw lists.

    The Mahalanobis distance :math:`D_{M}(x, y)` between two points :math:`x` and :math:`y` is computed using
    the following formula:

    .. math::
        D_{M}(x, y) = \sqrt{(x-y)^{T} \Sigma^{-1} (x-y)}

    Where :math:`\Sigma` is the covariance matrix of the dataset.

    :math:`\Sigma` is an n x n symmetric positive semi-definite matrix that can be used to calculate the variance
    of any subset of the data.

    The Mahalanobis distance is invariant under a linear transformation of the data but not under translation.

    For more information about Mahalanobis distance, refer to :ref:`mahalanobis_distance`.
    """
    type: Literal['MahalanobisDistance'] = 'MahalanobisDistance'   

    def __init__(self, cov_matrix: np.ndarray):
        """
        Initialize Mahalanobis distance with the inverse covariance matrix of the population.
        :param cov_matrix: Inverse of the covariance matrix of the population.
        """
        self.cov_inv = np.linalg.inv(cov_matrix)

    def distance(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes the Mahalanobis distance between two Vector instances.

        Args:
            vector_a (Vector): The first vector in the comparison.
            vector_b (Vector): The second vector to compare with the first vector.

        Returns:
            float: The computed Mahalanobis distance between the vectors.
        """
        # Extract data from Vector
        data_a = np.array(vector_a.value)
        data_b = np.array(vector_b.value)

        # Computing Mahalanobis distance
        distance = np.sqrt((data_a - data_b).T @ self.cov_inv @ (data_a - data_b))
        
        return distance
    
    def similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Compute similarity using the Mahalanobis distance. Since this distance metric isn't
        directly interpretable as a similarity, a transformation is applied to map the distance
        to a similarity score.

        Args:
            vector_a (Vector): The first vector in the comparison.
            vector_b (Vector): The second vector to compare with the first vector.

        Returns:
            float: A similarity score between vector_a and vector_b.
        """
        # One way to derive a similarity from distance is through inversion or transformation.
        # Here we use an exponential decay based on the computed distance. This is a placeholder
        # that assumes closer vectors (smaller distance) are more similar.
        distance = self.distance(vector_a, vector_b)

        # Transform the distance into a similarity score
        similarity = np.exp(-distance)

        return similarity
    
    def distances(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities
