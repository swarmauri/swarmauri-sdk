from abc import ABC, abstractmethod
from typing import List, Literal, Sequence, TypeAlias

ComparableValue: TypeAlias = object
RankingDirection: TypeAlias = Literal["ascending", "descending"]


class IVectorStoreComparator(ABC):
    """Store-facing ranking abstraction for vector retrieval."""

    @property
    @abstractmethod
    def ranking_direction(self) -> RankingDirection:
        """Return the preferred ordering for scores."""

    @abstractmethod
    def score(self, query: ComparableValue, candidate: ComparableValue) -> float:
        """Compute a single retrieval score."""

    @abstractmethod
    def score_many(
        self, query: ComparableValue, candidates: Sequence[ComparableValue]
    ) -> List[float]:
        """Compute retrieval scores for multiple candidates."""
