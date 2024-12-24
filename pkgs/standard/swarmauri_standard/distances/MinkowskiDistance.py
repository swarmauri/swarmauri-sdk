from typing import List, Literal
from scipy.spatial.distance import minkowski
from swarmauri_standard.vectors.Vector import Vector
from swarmauri_base.distances.DistanceBase import DistanceBase

class MinkowskiDistance(DistanceBase):
    """
    Implementation of the IDistanceSimiliarity interface using the Minkowski distance metric.
    Minkowski distance is a generalized metric form that includes Euclidean distance,
    Manhattan distance, and others depending on the order (p) parameter.

    The class provides methods to compute the Minkowski distance between two vectors.

    Parameters:
    - p (int): The order of the Minkowski distance. p=2 corresponds to the Euclidean distance,
               while p=1 corresponds to the Manhattan distance. Default is 
    """
    type: Literal['MinkowskiDistance'] = 'MinkowskiDistance'
    p: int = 2

    def distance(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes the Minkowski distance between two vectors.

        Args:
            vector_a (Vector): The first vector in the comparison.
            vector_b (Vector): The second vector in the comparison.

        Returns:
            float: The computed Minkowski distance between vector_a and vector_b.
        """
        # Check if both vectors have the same dimensionality
        if vector_a.shape != vector_b.shape:
            raise ValueError("Vectors must have the same dimensionality.")

        # Extract data from Vector instances
        data_a = vector_a.value
        data_b = vector_b.value

        # Calculate and return the Minkowski distance
        return minkowski(data_a, data_b, p=self.p)

    def similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Compute the similarity between two vectors based on the Minkowski distance.
        The similarity is inversely related to the distance.

        Args:
            vector_a (Vector): The first vector to compare for similarity.
            vector_b (Vector): The second vector to compare with the first vector.

        Returns:
            float: A similarity score between vector_a and vector_b.
        """
        dist = self.distance(vector_a, vector_b)
        return 1 / (1 + dist)  # An example similarity score
    
    def distances(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities
