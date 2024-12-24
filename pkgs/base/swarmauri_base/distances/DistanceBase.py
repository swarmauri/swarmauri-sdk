from abc import abstractmethod
from numpy.linalg import norm
from typing import List, Optional, Literal
from pydantic import Field
from swarmauri_core.distances.IDistanceSimilarity import IDistanceSimilarity
from swarmauri_standard.vectors.Vector import Vector
from swarmauri_standard.vectors.VectorProductMixin import VectorProductMixin
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes

class DistanceBase(IDistanceSimilarity, VectorProductMixin, ComponentBase):
    """
    Implements cosine distance calculation as an IDistanceSimiliarity interface.
    Cosine distance measures the cosine of the angle between two non-zero vectors
    of an inner product space, capturing the orientation rather than the magnitude 
    of these vectors.
    """
    resource: Optional[str] =  Field(default=ResourceTypes.DISTANCE.value, frozen=True)
    type: Literal['DistanceBase'] = 'DistanceBase'
    @abstractmethod
    def distance(self, vector_a: Vector, vector_b: Vector) -> float:
        pass
    
    @abstractmethod
    def similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        pass
       

    @abstractmethod
    def distances(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        pass
        
    @abstractmethod
    def similarities(self, vector_a: Vector, vectors_b: List[Vector]) -> List[float]:
        pass
        