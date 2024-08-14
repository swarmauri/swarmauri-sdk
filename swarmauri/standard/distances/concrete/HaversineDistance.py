from typing import List
from math import radians, cos, sin, sqrt, atan2
from swarmauri.core.vector_stores.IDistanceSimilarity import IDistanceSimilarity
from swarmauri.core.vectors.IVector import IVector


class HaversineDistance(IDistanceSimilarity):
    """
    Concrete implementation of IDistanceSimiliarity interface using the Haversine formula.
    
    Haversine formula determines the great-circle distance between two points on a sphere given their 
    longitudes and latitudes. This implementation is particularly useful for geo-spatial data.
    """ 

    def distance(self, vector_a: IVector, vector_b: IVector) -> float:
        """
        Computes the Haversine distance between two geo-spatial points.

        Args:
            vector_a (IVector): The first point in the format [latitude, longitude].
            vector_b (IVector): The second point in the same format [latitude, longitude].

        Returns:
            float: The Haversine distance between vector_a and vector_b in kilometers.
        """
        # Earth radius in kilometers
        R = 6371.0

        lat1, lon1 = map(radians, vector_a.data)
        lat2, lon2 = map(radians, vector_b.data)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        # Haversine formula
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c

        return distance

    def similarity(self, vector_a: IVector, vector_b: IVector) -> float:
        raise NotImplementedError("Similarity not implemented for Haversine distance.")
        
    def distances(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: IVector, vectors_b: List[IVector]) -> List[float]:
        raise NotImplementedError("Similarity not implemented for Haversine distance.")