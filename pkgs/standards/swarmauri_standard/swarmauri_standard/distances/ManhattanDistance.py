from typing import List, Literal
from swarmauri_standard.vectors.Vector import Vector
from swarmauri_base.distances.DistanceBase import DistanceBase

class ManhattanDistance(DistanceBase):
    """
    Concrete implementation of the IDistanceSimiliarity interface using the Manhattan distance.
    
    The Manhattan distance between two points is the sum of the absolute differences of their Cartesian coordinates.
    This is also known as L1 distance.
    """
    type: Literal['ManhattanDistance'] = 'ManhattanDistance'   
    def distance(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes the Manhattan distance between two vectors.

        Args:
            vector_a (Vector): The first vector in the comparison.
            vector_b (Vector): The second vector in the comparison.

        Returns:
            float: The Manhattan distance between vector_a and vector_b.
        """
        if vector_a.shape != vector_b.shape:
            raise ValueError("Vectors must have the same dimensionality.")
        
        return sum(abs(a - b) for a, b in zip(vector_a.value, vector_b.value))

    def similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        The similarity based on Manhattan distance can be inversely related to the distance for some applications,
        but this method intentionally returns NotImplementedError to signal that Manhattan distance is typically
        not directly converted to similarity in the conventional sense used in this context.

        Args:
            vector_a (Vector): The first vector in the comparison.
            vector_b (Vector): The second vector in the comparison.

        Returns:
            NotImplementedError: This is intended as this distance metric doesn't directly offer a similarity metric.
        """
        raise NotImplementedError("ManhattanDistance does not directly provide a similarity metric.")
        
    def distances(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        raise NotImplementedError("ManhattanDistance does not directly provide a similarity metric.")
