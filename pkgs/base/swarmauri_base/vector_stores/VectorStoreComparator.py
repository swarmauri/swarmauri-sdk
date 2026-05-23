from typing import List, Sequence

from swarmauri_core.metrics.IMetric import IMetric
from swarmauri_core.similarities.ISimilarity import ISimilarity
from swarmauri_core.vector_stores.IVectorStoreComparator import (
    ComparableValue,
    IVectorStoreComparator,
    RankingDirection,
)


def _coerce_comparable(value: ComparableValue) -> ComparableValue:
    """Normalize vector-like wrappers into values understood by metric/similarity APIs."""
    if hasattr(value, "to_numpy"):
        try:
            return value.to_numpy()
        except TypeError:
            pass
    if hasattr(value, "value"):
        return getattr(value, "value")
    return value


class VectorStoreComparator(IVectorStoreComparator):
    """Reusable base class for vector-store ranking helpers."""

    @property
    def ranking_direction(self) -> RankingDirection:
        raise NotImplementedError

    def score(self, query: ComparableValue, candidate: ComparableValue) -> float:
        raise NotImplementedError

    def score_many(
        self, query: ComparableValue, candidates: Sequence[ComparableValue]
    ) -> List[float]:
        return [self.score(query, candidate) for candidate in candidates]

    def top_k_indices(
        self,
        query: ComparableValue,
        candidates: Sequence[ComparableValue],
        top_k: int,
    ) -> List[int]:
        scores = self.score_many(query, candidates)
        reverse = self.ranking_direction == "descending"
        return sorted(
            range(len(scores)), key=lambda index: scores[index], reverse=reverse
        )[:top_k]


class MetricVectorStoreComparator(VectorStoreComparator):
    """Adapter that ranks candidates by a metric in ascending order."""

    def __init__(self, metric: IMetric):
        self.metric = metric

    @property
    def ranking_direction(self) -> RankingDirection:
        return "ascending"

    def score(self, query: ComparableValue, candidate: ComparableValue) -> float:
        return self.metric.distance(
            _coerce_comparable(query),
            _coerce_comparable(candidate),
        )

    def score_many(
        self, query: ComparableValue, candidates: Sequence[ComparableValue]
    ) -> List[float]:
        normalized_query = _coerce_comparable(query)
        normalized_candidates = [
            _coerce_comparable(candidate) for candidate in candidates
        ]
        return [
            self.metric.distance(normalized_query, candidate)
            for candidate in normalized_candidates
        ]


class SimilarityVectorStoreComparator(VectorStoreComparator):
    """Adapter that ranks candidates by a similarity in descending order."""

    def __init__(self, similarity: ISimilarity):
        self.similarity = similarity

    @property
    def ranking_direction(self) -> RankingDirection:
        return "descending"

    def score(self, query: ComparableValue, candidate: ComparableValue) -> float:
        return self.similarity.similarity(
            _coerce_comparable(query),
            _coerce_comparable(candidate),
        )

    def score_many(
        self, query: ComparableValue, candidates: Sequence[ComparableValue]
    ) -> List[float]:
        normalized_query = _coerce_comparable(query)
        normalized_candidates = [
            _coerce_comparable(candidate) for candidate in candidates
        ]
        return self.similarity.similarities(normalized_query, normalized_candidates)
