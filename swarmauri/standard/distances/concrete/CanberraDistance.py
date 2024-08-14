import numpy as np
from typing import List
from swarmauri.core.vector_stores.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector


class CanberraDistance(IDistanceSimilarity):
    """
    Concrete implementation of the IDistanceSimiliarity interface using the Canberra distance metric.
    This class now processes IVector instances instead of raw lists.
    """

    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the Canberra distance between two IVector instances.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector in the comparison.

        Returns:
            float: The computed Canberra distance between the vectors.
        """
        # Extract data from IVector
        data_a = np.array(vector_a.data)
        data_b = np.array(vector_b.data)

        # Checking dimensions match
        if data_a.shape != data_b.shape:
            raise ValueError("Vectors must have the same dimensionality.")

        # Computing Canberra distance
        distance = np.sum(np.abs(data_a - data_b) / (np.abs(data_a) + np.abs(data_b)))
        # Handling the case where both vectors have a zero value for the same dimension
        distance = np.nan_to_num(distance)
        return distance
    
    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Compute similarity using the Canberra distance. Since this distance metric isn't
        directly interpretable as a similarity, a transformation is applied to map the distance
        to a similarity score.

        Args:
            vector_a (IVector): The first vector in the comparison.
            vector_b (IVector): The second vector to compare with the first vector.

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
    
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities