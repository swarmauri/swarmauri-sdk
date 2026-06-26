from abc import abstractmethod
from typing import List, Optional, Literal
import warnings
from pydantic import Field

from swarmauri_standard.vectors.Vector import Vector
from swarmauri_core.distances.IDistanceSimilarity import IDistanceSimilarity
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


warnings.warn(
    "DistanceBase is deprecated and will be removed from the active Swarmauri workspace by v0.12.0.",
    DeprecationWarning,
    stacklevel=2,
)


@ComponentBase.register_model()
class DistanceBase(IDistanceSimilarity, ComponentBase):
    """
    Deprecated compatibility base for bundled distance/similarity components.

    New code should model precise mathematical families directly and use
    vector-store comparators for retrieval ranking.
    """

    resource: Optional[str] = Field(
        default=ResourceTypes.DISTANCE.value, frozen=True
    )
    type: Literal["DistanceBase"] = "DistanceBase"

    @abstractmethod
    def distance(self, vector_a: Vector, vector_b: Vector) -> float:
        pass

    @abstractmethod
    def similarity(self, vector_a: Vector, vector_b: Vector) -> float:
        pass

    @abstractmethod
    def distances(
        self, vector_a: Vector, vectors_b: List[Vector]
    ) -> List[float]:
        pass

    @abstractmethod
    def similarities(
        self, vector_a: Vector, vectors_b: List[Vector]
    ) -> List[float]:
        pass
