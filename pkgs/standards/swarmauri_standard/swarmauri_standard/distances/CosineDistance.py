from numpy.linalg import norm
from typing import List, Literal
from swarmauri_standard.vectors.Vector import Vector
from swarmauri_base.distances.DistanceBase import DistanceBase

class CosineDistance(DistanceBase):
    """
    Implements cosine distance calculation as an IDistanceSimiliarity interface.
    Cosine distance measures the cosine of the angle between two non-zero vectors
    of an inner product space, capturing the orientation rather than the magnitude 
    of these vectors.
    """
    type: Literal['CosineDistance'] = 'CosineDistance'   
       
    def distance(self, vector_a: Vector, vector_b: Vector) -> float:
        """ 
        Computes the cosine distance between two vectors: 1 - cosine similarity.
    
        Args:
            vector_a (Vector): The first vector in the comparison.
            vector_b (Vector): The second vector in the comparison.
    
        Returns:
            float: The computed cosine distance between vector_a and vector_b.
                   It ranges from 0 (completely similar) to 2 (completely dissimilar).
        """
        norm_a = norm(vector_a.value)
        norm_b = norm(vector_b.value)
    
        # Check if either of the vector norms is close to zero
        if norm_a < 1e-10 or norm_b < 1e-10:
            return 1.0  # Return maximum distance for cosine which varies between -1 to 1, so 1 indicates complete dissimilarity
    
        # Compute the cosine similarity between the vectors
        cos_sim = self.dot_product(vector_a, vector_b) / (norm_a * norm_b)
    
        # Covert cosine similarity to cosine distance
        cos_distance = 1 - cos_sim
    
        return cos_distance
    
    def similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes the cosine similarity between two vectors.

        Args:
            vector_a (Vector): The first vector in the comparison.
            vector_b (Vector): The second vector in the comparison.

        Returns:
            float: The cosine similarity between vector_a and vector_b.
        """
        return 1 - self.distance(vector_a, vector_b)

    def distances(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        similarities = [self.similarity(vector_a, vector_b) for vector_b in vectors_b]
        return similarities