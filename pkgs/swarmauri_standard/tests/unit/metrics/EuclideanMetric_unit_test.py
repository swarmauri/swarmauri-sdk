import pytest
import numpy as np
from swarmauri_standard.swarmauri_standard.metrics import EuclideanMetric
from typing import Union, Tuple, Sequence, Optional
import logging

logger = logging.getLogger(__name__)

@pytest.fixture
def euclidean_metric():
    """Fixture to provide a EuclideanMetric instance for testing."""
    return EuclideanMetric()

@pytest.mark.unit
def test_euclidean_metric_initialization(euclidean_metric):
    """Test that the EuclideanMetric class initializes correctly."""
    assert isinstance(euclidean_metric, EuclideanMetric)
    assert isinstance(euclidean_metric, EuclideanMetric.MetricBase)

@pytest.mark.unit
def test_euclidean_metric_type():
    """Test that the type property is correctly set."""
    assert EuclideanMetric.type == "EuclideanMetric"

@pytest.mark.unit
def test_euclidean_metric_resource():
    """Test that the resource property is correctly set."""
    assert EuclideanMetric.resource == "Metric"

@pytest.mark.unit
@pytest.mark.parametrize("x,y,expected_distance", [
    # Test with lists
    ([1, 2, 3], [4, 5, 6], np.sqrt(3**2 + 2**2 + 3**2)),
    # Test with tuples
    ((1, 2), (3, 4), np.sqrt(2**2 + 2**2)),
    # Test with numpy arrays
    (np.array([1, 2, 3]), np.array([4, 5, 6]), np.sqrt(3**2 + 2**2 + 3**2)),
    # Test with different dimensions
    ([1, 2], [3, 4, 5], None),
])
def test_euclidean_metric_distance(euclidean_metric, x, y, expected_distance):
    """Test the distance method with various input types and edge cases."""
    if expected_distance is not None:
        distance = euclidean_metric.distance(x, y)
        assert np.isclose(distance, expected_distance)
    else:
        with pytest.raises(ValueError):
            euclidean_metric.distance(x, y)

@pytest.mark.unit
@pytest.mark.parametrize("x,ys,expected_result", [
    # Test with single vector
    ([1, 2], None, 0.0),
    # Test with multiple vectors
    ([1, 2], [(3, 4), (5, 6)], [np.sqrt(8), np.sqrt(32)]),
    # Test with invalid dimensions
    ([1, 2], [(3, 4, 5)], None),
])
def test_euclidean_metric_distances(euclidean_metric, x, ys, expected_result):
    """Test the distances method with various input types and edge cases."""
    if expected_result is not None:
        result = euclidean_metric.distances(x, ys)
        if isinstance(result, Sequence):
            for res, exp in zip(result, expected_result):
                assert np.isclose(res, exp)
        else:
            assert np.isclose(result, expected_result)
    else:
        with pytest.raises(ValueError):
            euclidean_metric.distances(x, ys)

@pytest.mark.unit
@pytest.mark.parametrize("x,y", [
    ([1, 2], [3, 4]),
    ((5, 6), (7, 8)),
    (np.array([9, 10]), np.array([11, 12])),
])
def test_euclidean_metric_non_negativity(euclidean_metric, x, y):
    """Test the non-negativity property of the metric."""
    distance = euclidean_metric.distance(x, y)
    assert distance >= 0

@pytest.mark.unit
@pytest.mark.parametrize("x,y", [
    ([1, 2], [1, 2]),
    ((3, 4), (3, 4)),
    (np.array([5, 6]), np.array([5, 6])),
])
def test_euclidean_metric_identity(euclidean_metric, x, y):
    """Test the identity property of the metric."""
    distance = euclidean_metric.distance(x, y)
    assert distance == 0

@pytest.mark.unit
@pytest.mark.parametrize("x,y", [
    ([1, 2], [3, 4]),
    ((5, 6), (7, 8)),
    (np.array([9, 10]), np.array([11, 12])),
])
def test_euclidean_metric_symmetry(euclidean_metric, x, y):
    """Test the symmetry property of the metric."""
    d_xy = euclidean_metric.distance(x, y)
    d_yx = euclidean_metric.distance(y, x)
    assert d_xy == d_yx

@pytest.mark.unit
@pytest.mark.parametrize("x,y,z", [
    ([1, 2], [3, 4], [5, 6]),
    ((7, 8), (9, 10), (11, 12)),
    (np.array([13, 14]), np.array([15, 16]), np.array([17, 18])),
])
def test_euclidean_metric_triangle_inequality(euclidean_metric, x, y, z):
    """Test the triangle inequality property of the metric."""
    d_xz = euclidean_metric.distance(x, z)
    d_xy = euclidean_metric.distance(x, y)
    d_yz = euclidean_metric.distance(y, z)
    assert d_xz <= d_xy + d_yz

@pytest.mark.unit
def test_euclidean_metric_check_non_negativity(euclidean_metric):
    """Test the non-negativity check method."""
    x = [1, 2]
    y = [3, 4]
    result = euclidean_metric.check_non_negativity(x, y)
    assert result is True

@pytest.mark.unit
def test_euclidean_metric_check_identity(euclidean_metric):
    """Test the identity check method."""
    x = [1, 2]
    y = [1, 2]
    result = euclidean_metric.check_identity(x, y)
    assert result is True

@pytest.mark.unit
def test_euclidean_metric_check_symmetry(euclidean_metric):
    """Test the symmetry check method."""
    x = [1, 2]
    y = [3, 4]
    result = euclidean_metric.check_symmetry(x, y)
    assert result is True

@pytest.mark.unit
def test_euclidean_metric_check_triangle_inequality(euclidean_metric):
    """Test the triangle inequality check method."""
    x = [1, 2]
    y = [3, 4]
    z = [5, 6]
    result = euclidean_metric.check_triangle_inequality(x, y, z)
    assert result is True