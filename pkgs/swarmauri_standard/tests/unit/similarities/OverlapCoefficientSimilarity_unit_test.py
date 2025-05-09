import pytest
from swarmauri_standard.similarities.OverlapCoefficientSimilarity import (
    OverlapCoefficientSimilarity,
)
import logging


@pytest.fixture(autouse=True)
def setup_logging():
    """Set up logging configuration for tests"""
    logging.basicConfig(level=logging.DEBUG)
    yield
    logging.basicConfig(level=logging.NOTSET)


@pytest.fixture
def overlap_coefficient_similarity():
    """Fixture providing an instance of OverlapCoefficientSimilarity"""
    return OverlapCoefficientSimilarity()


@pytest.mark.unit
def test_similarity_same_elements(overlap_coefficient_similarity):
    """Test similarity calculation with identical elements"""
    x = "test"
    y = "test"
    similarity = overlap_coefficient_similarity.similarity(x, y)
    assert similarity == 1.0


@pytest.mark.unit
def test_similarity_different_elements(overlap_coefficient_similarity):
    """Test similarity calculation with different elements"""
    x = "test"
    y = "example"
    similarity = overlap_coefficient_similarity.similarity(x, y)
    assert similarity == 0.0


@pytest.mark.unit
def test_similarity_partial_overlap(overlap_coefficient_similarity):
    """Test similarity calculation with partial overlap"""
    x = [1, 2, 3]
    y = [2, 3, 4]
    similarity = overlap_coefficient_similarity.similarity(x, y)
    assert similarity == 2 / 3


@pytest.mark.unit
def test_similarities(overlap_coefficient_similarity):
    """Test multiple similarity calculations"""
    xs = ["a", "b", "c"]
    ys = ["a", "b", "d"]
    similarities = overlap_coefficient_similarity.similarities(xs, ys)
    assert len(similarities) == 3


@pytest.mark.unit
def test_dissimilarity(overlap_coefficient_similarity):
    """Test dissimilarity calculation"""
    x = "test"
    y = "example"
    dissimilarity = overlap_coefficient_similarity.dissimilarity(x, y)
    assert dissimilarity == 1.0


@pytest.mark.unit
def test_dissimilarities(overlap_coefficient_similarity):
    """Test multiple dissimilarity calculations"""
    xs = ["a", "b", "c"]
    ys = ["a", "b", "d"]
    dissimilarities = overlap_coefficient_similarity.dissimilarities(xs, ys)
    assert len(dissimilarities) == 3


@pytest.mark.unit
def test_check_boundedness(overlap_coefficient_similarity):
    """Test if similarity measure is bounded"""
    assert overlap_coefficient_similarity.check_boundedness() is True


@pytest.mark.unit
def test_check_reflexivity(overlap_coefficient_similarity):
    """Test if similarity measure satisfies reflexivity"""
    assert overlap_coefficient_similarity.check_reflexivity() is True


@pytest.mark.unit
def test_check_symmetry(overlap_coefficient_similarity):
    """Test if similarity measure is symmetric"""
    assert overlap_coefficient_similarity.check_symmetry() is True


@pytest.mark.unit
def test_check_identity(overlap_coefficient_similarity):
    """Test if similarity measure satisfies identity of discernibles"""
    assert overlap_coefficient_similarity.check_identity() is False


@pytest.mark.unit
def test_similarity_empty_inputs(overlap_coefficient_similarity):
    """Test similarity calculation with empty inputs"""
    x = ""
    y = ""
    with pytest.raises(ValueError):
        overlap_coefficient_similarity.similarity(x, y)


@pytest.mark.unit
def test_similarity_sequence_inputs(overlap_coefficient_similarity):
    """Test similarity calculation with sequence inputs"""
    x = [1, 2, 3]
    y = [3, 2, 1]
    similarity = overlap_coefficient_similarity.similarity(x, y)
    assert similarity == 1.0


@pytest.mark.unit
def test_similarity_mixed_types(overlap_coefficient_similarity):
    """Test similarity calculation with mixed types"""
    x = "test"
    y = ["t", "e", "s", "t"]
    similarity = overlap_coefficient_similarity.similarity(x, y)
    assert similarity == 0.5
