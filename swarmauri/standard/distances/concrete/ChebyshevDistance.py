from typing import List
from swarmauri.core.vectors.IVector import IVector
from swarmauri.core.vector_stores.IDistanceSimilarity import IDistanceSimilarity

class ChebyshevDistance(IDistanceSimilarity):
    """
    Concrete implementation of the IDistanceSimiliarity interface using the Chebyshev distance metric.
    Chebyshev distance is the maximum absolute distance between two vectors' elements.
    """

    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the Chebyshev distance between two vectors.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector in the comparison.

        Returns:
            float: The computed Chebyshev distance between vector_a and vector_b.
        """
        max_distance = 0
        for a, b in zip(vector_a.data, vector_b.data):
            max_distance = max(max_distance, abs(a - b))
        return max_distance

    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the similarity between two vectors based on the Chebyshev distance.

        Args:
            vector_a (IVector): The first vector.
            vector_b (IVector): The second vector.

        Returns:
            float: The similarity score between the two vectors.
        """

        return 1 / (1 + self.distance(vector_a, vector_b))
    
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities