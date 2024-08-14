from typing import List
from swarmauri.core.vector_stores.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector

class SquaredEuclideanDistance(IDistanceSimilarity):
    """
    A concrete class for computing the squared Euclidean distance between two vectors.
    """

    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the squared Euclidean distance between vectors `vector_a` and `vector_b`.

        Parameters:
        - vector_a (IVector): The first vector in the comparison.
        - vector_b (IVector): The second vector in the comparison.

        Returns:
        - float: The computed squared Euclidean distance between vector_a and vector_b.
        """
        if vector_a.dimensions != vector_b.dimensions:
            raise ValueError("Vectors must be of the same dimensionality.")

        squared_distance = sum((a - b) ** 2 for a, b in zip(vector_a.data, vector_b.data))
        return squared_distance

    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Squared Euclidean distance is not used for calculating similarity.
        
        Parameters:
        - vector_a (IVector): The first vector.
        - vector_b (IVector): The second vector.

        Raises:
        - NotImplementedError: Indicates that similarity calculation is not implemented.
        """
        raise NotImplementedError("Similarity calculation is not implemented for Squared Euclidean distance.")
        
        
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        raise NotImplementedError("Similarity calculation is not implemented for Squared Euclidean distance.")