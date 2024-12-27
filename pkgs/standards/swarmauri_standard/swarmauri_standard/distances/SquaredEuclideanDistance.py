from typing import List, Literal
from swarmauri_standard.vectors.Vector import Vector
from swarmauri_base.distances.DistanceBase import DistanceBase

class SquaredEuclideanDistance(DistanceBase):
    """
    A concrete class for computing the squared Euclidean distance between two vectors.
    """
    type: Literal['SquaredEuclideanDistance'] = 'SquaredEuclideanDistance'
    
    def distance(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes the squared Euclidean distance between vectors `vector_a` and `vector_b`.

        Parameters:
        - vector_a (Vector): The first vector in the comparison.
        - vector_b (Vector): The second vector in the comparison.

        Returns:
        - float: The computed squared Euclidean distance between vector_a and vector_b.
        """
        if vector_a.shape != vector_b.shape:
            raise ValueError("Vectors must be of the same dimensionality.")

        squared_distance = sum((a - b) ** 2 for a, b in zip(vector_a.value, vector_b.value))
        return squared_distance

    def similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Squared Euclidean distance is not used for calculating similarity.
        
        Parameters:
        - vector_a (Vector): The first vector.
        - vector_b (Vector): The second vector.

        Raises:
        - NotImplementedError: Indicates that similarity calculation is not implemented.
        """
        raise NotImplementedError("Similarity calculation is not implemented for Squared Euclidean distance.")
        
        
    def distances(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        raise NotImplementedError("Similarity calculation is not implemented for Squared Euclidean distance.")