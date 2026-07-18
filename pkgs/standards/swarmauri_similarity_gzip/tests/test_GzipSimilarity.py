import pytest

from swarmauri_base.similarities.SimilarityBase import SimilarityBase
from swarmauri_similarity_gzip import GzipSimilarity


def test_inherits_similarity_base():
    assert isinstance(GzipSimilarity(), SimilarityBase)


def test_identical_values_are_maximally_similar():
    comparator = GzipSimilarity()

    assert comparator.similarity("same value", "same value") == 1.0


def test_similarity_is_bounded():
    comparator = GzipSimilarity()

    score = comparator.similarity("alpha", "beta")

    assert 0.0 <= score <= 1.0


def test_symmetric_comparison_is_order_independent():
    comparator = GzipSimilarity(symmetric=True)

    assert comparator.similarity("alpha", "beta") == comparator.similarity(
        "beta", "alpha"
    )


def test_text_and_utf8_bytes_are_equivalent():
    comparator = GzipSimilarity()

    assert comparator.similarity("hello", "world") == comparator.similarity(
        b"hello", b"world"
    )


def test_invalid_compression_level_is_rejected():
    with pytest.raises(ValueError):
        GzipSimilarity(compresslevel=10)
