from typing import List
from scipy.spatial.distance import minkowski
from swarmauri.core.vector_stores.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector

class MinkowskiDistance(IDistanceSimilarity):
    """
    Implementation of the IDistanceSimiliarity interface using the Minkowski distance metric.
    Minkowski distance is a generalized metric form that includes Euclidean distance,
    Manhattan distance, and others depending on the order (p) parameter.

    The class provides methods to compute the Minkowski distance between two vectors.
    """

    def __init__(self, p: int = 2):
        """
        Initializes the MinkowskiDistance calculator with the specified order.

        Parameters:
        - p (int): The order of the Minkowski distance. p=2 corresponds to the Euclidean distance,
                   while p=1 corresponds to the Manhattan distance. Default is 2.
        """
        self.p = p

    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the Minkowski distance between two vectors.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector in the comparison.

        Returns:
            float: The computed Minkowski distance between vector_a and vector_b.
        """
        # Check if both vectors have the same dimensionality
        if vector_a.dimensions != vector_b.dimensions:
            raise ValueError("Vectors must have the same dimensionality.")

        # Extract data from IVector instances
        data_a = vector_a.data
        data_b = vector_b.data

        # Calculate and return the Minkowski distance
        return minkowski(data_a, data_b, p=self.p)

    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Compute the similarity between two vectors based on the Minkowski distance.
        The similarity is inversely related to the distance.

        Args:
            vector_a (IVector): The first vector to compare for similarity.
            vector_b (IVector): The second vector to compare with the first vector.

        Returns:
            float: A similarity score between vector_a and vector_b.
        """
        dist = self.distance(vector_a, vector_b)
        return 1 / (1 + dist)  # An example similarity score
    
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities