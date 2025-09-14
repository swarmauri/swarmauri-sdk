import pytest
import numpy as np
from DistanceMetrics import euclidean_distance


@pytest.mark.unit
def test_euclidean_distance_identical_vectors():
    """Test Euclidean distance between identical vectors."""
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([1.0, 2.0, 3.0])
    expected = 0.0
    result = euclidean_distance(a, b)
    assert np.isclose(result, expected), f"Expected {expected}, got {result}"


@pytest.mark.unit
def test_euclidean_distance_different_vectors():
    """Test Euclidean distance between different vectors."""
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([4.0, 5.0, 6.0])
    expected = np.sqrt(27)  # sqrt((4-1)^2 + (5-2)^2 + (6-3)^2)
    result = euclidean_distance(a, b)
    assert np.isclose(result, expected), f"Expected {expected}, got {result}"


@pytest.mark.unit
def test_euclidean_distance_empty_vectors():
    """Test Euclidean distance between empty vectors."""
    a = np.array([])
    b = np.array([])
    expected = 0.0
    result = euclidean_distance(a, b)
    assert np.isclose(result, expected), f"Expected {expected}, got {result}"


@pytest.mark.unit
def test_euclidean_distance_invalid_shape():
    """Test Euclidean distance with vectors of different shapes."""
    a = np.array([1.0, 2.0])
    b = np.array([1.0, 2.0, 3.0])
    with pytest.raises(ValueError, match="Input arrays must have the same size."):
        euclidean_distance(a, b)
