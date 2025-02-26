import warnings

from abc import abstractmethod
from typing import List, Optional, Literal
from pydantic import Field

from swarmauri_standard.vectors.Vector import Vector
from swarmauri_core.distances.IDistanceSimilarity import IDistanceSimilarity
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


warnings.warn(
    "Importing ComponentBase from swarmauri_core is deprecated and will be "
    "removed in a future version. Please use 'from swarmauri_base import "
    "ComponentBase'",
    DeprecationWarning,
    stacklevel=2,
)



@ComponentBase.register_model()
class DistanceBase(IDistanceSimilarity, ComponentBase):
    """
    Implements cosine distance calculation as an IDistanceSimiliarity interface.
    Cosine distance measures the cosine of the angle between two non-zero vectors
    of an inner product space, capturing the orientation rather than the magnitude
    of these vectors.
    """

    resource: Optional[str] = Field(default=ResourceTypes.DISTANCE.value, frozen=True)
    type: Literal["DistanceBase"] = "DistanceBase"

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
