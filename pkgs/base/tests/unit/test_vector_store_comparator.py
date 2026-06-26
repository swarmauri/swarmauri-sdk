import warnings

import pytest

from swarmauri_base.vector_stores.VectorStoreComparator import (
    MetricVectorStoreComparator,
    SimilarityVectorStoreComparator,
)
from swarmauri_standard.metrics.EuclideanMetric import EuclideanMetric
from swarmauri_standard.similarities.CosineSimilarity import CosineSimilarity


@pytest.mark.unit
def test_metric_comparator_ranks_ascending():
    comparator = MetricVectorStoreComparator(EuclideanMetric())
    indices = comparator.top_k_indices(
        [0.0, 0.0], [[2.0, 0.0], [1.0, 0.0]], top_k=2
    )
    assert comparator.ranking_direction == "ascending"
    assert indices == [1, 0]


@pytest.mark.unit
def test_similarity_comparator_ranks_descending():
    comparator = SimilarityVectorStoreComparator(CosineSimilarity())
    indices = comparator.top_k_indices(
        [1.0, 0.0], [[0.0, 1.0], [1.0, 0.0]], top_k=2
    )
    assert comparator.ranking_direction == "descending"
    assert indices == [1, 0]


@pytest.mark.unit
def test_deprecated_distance_contract_modules_warn():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", DeprecationWarning)
        import importlib
        import swarmauri_core.distances.IDistanceSimilarity as deprecated_core
        import swarmauri_base.distances.DistanceBase as deprecated_base
        import swarmauri_base.distances.VisionDistanceBase as deprecated_vision

        importlib.reload(deprecated_core)
        importlib.reload(deprecated_base)
        importlib.reload(deprecated_vision)

    assert (
        len([item for item in caught if item.category is DeprecationWarning])
        >= 3
    )
