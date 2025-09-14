import pytest
import numpy as np
from DistanceMetrics import cosine


@pytest.mark.unit
def test_cosine_similarity_identical_vectors():
    """Test cosine similarity for identical vectors."""
    vec1 = np.array([1.0, 2.0, 3.0])
    vec2 = np.array([1.0, 2.0, 3.0])
    result = cosine.cosine_similarity(vec1, vec2)
    expected = 1.0
    assert np.isclose(result, expected), f"Expected {expected}, got {result}"


@pytest.mark.unit
def test_cosine_similarity_orthogonal_vectors():
    """Test cosine similarity for orthogonal vectors."""
    vec1 = np.array([1.0, 0.0, 0.0])
    vec2 = np.array([0.0, 1.0, 0.0])
    result = cosine.cosine_similarity(vec1, vec2)
    expected = 0.0
    assert np.isclose(result, expected), f"Expected {expected}, got {result}"


@pytest.mark.unit
def test_cosine_similarity_opposite_vectors():
    """Test cosine similarity for opposite vectors."""
    vec1 = np.array([1.0, 2.0, 3.0])
    vec2 = np.array([-1.0, -2.0, -3.0])
    result = cosine.cosine_similarity(vec1, vec2)
    expected = -1.0
    assert np.isclose(result, expected), f"Expected {expected}, got {result}"


@pytest.mark.unit
def test_cosine_similarity_zero_vector():
    """Test cosine similarity with one zero vector."""
    vec1 = np.array([0.0, 0.0, 0.0])
    vec2 = np.array([1.0, 2.0, 3.0])
    result = cosine.cosine_similarity(vec1, vec2)
    expected = 0.0
    assert np.isclose(result, expected), f"Expected {expected}, got {result}"


@pytest.mark.unit
def test_cosine_similarity_different_lengths():
    """Test cosine similarity for vectors of different lengths."""
    vec1 = np.array([1.0, 2.0])
    vec2 = np.array([1.0, 2.0, 3.0])
    with pytest.raises(ValueError, match="Vectors must be of the same length."):
        cosine.cosine_similarity(vec1, vec2)


@pytest.mark.unit
def test_cosine_similarity_non_list_input():
    """Test cosine similarity with non-list input."""
    vec1 = 1.0
    vec2 = 2.0
    with pytest.raises(TypeError, match="Expected lists for vectors."):
        cosine.cosine_similarity(vec1, vec2)
