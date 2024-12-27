from typing import List, Literal
from math import radians, cos, sin, sqrt, atan2
from swarmauri_standard.vectors.Vector import Vector
from swarmauri_base.distances.DistanceBase import DistanceBase


class HaversineDistance(DistanceBase):
    """
    Concrete implementation of IDistanceSimiliarity interface using the Haversine formula.
    
    Haversine formula determines the great-circle distance between two points on a sphere given their 
    longitudes and latitudes. This implementation is particularly useful for geo-spatial data.
    """ 
    type: Literal['HaversineDistance'] = 'HaversineDistance'   
    def distance(self, vector_a: Vector, vector_b: Vector) -> float:
        """
        Computes the Haversine distance between two geo-spatial points.

        Args:
            vector_a (Vector): The first point in the format [latitude, longitude].
            vector_b (Vector): The second point in the same format [latitude, longitude].

        Returns:
            float: The Haversine distance between vector_a and vector_b in kilometers.
        """
        # Earth radius in kilometers
        R = 6371.0

        lat1, lon1 = map(radians, vector_a.value)
        lat2, lon2 = map(radians, vector_b.value)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        # Haversine formula
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c

        return distance

    def similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        raise NotImplementedError("Similarity not implemented for Haversine distance.")
        
    def distances(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        distances = [self.distance(vector_a, vector_b) for vector_b in vectors_b]
        return distances
    
    def similarities(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        raise NotImplementedError("Similarity not implemented for Haversine distance.")