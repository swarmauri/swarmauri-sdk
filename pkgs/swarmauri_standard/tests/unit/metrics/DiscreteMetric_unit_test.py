import pytest
import logging
from swarmauri_standard.metrics.DiscreteMetric import DiscreteMetric
from unittest.mock import patch


@pytest.fixture
def discrete_metric():
    """Fixture to provide a DiscreteMetric instance for testing."""
    return DiscreteMetric()


@pytest.mark.unit
def test_distance(discrete_metric):
    """Test the distance method with various inputs."""
    # Test with same inputs
    assert discrete_metric.distance(1, 1) == 0.0
    assert discrete_metric.distance("test", "test") == 0.0
    assert discrete_metric.distance([1, 2], [1, 2]) == 0.0

    # Test with different inputs
    assert discrete_metric.distance(1, 2) == 1.0
    assert discrete_metric.distance("test", "different") == 1.0
    assert discrete_metric.distance([1, 2], [2, 3]) == 1.0


@pytest.mark.unit
def test_distances(discrete_metric):
    """Test the distances method with various input combinations."""
    # Test with empty lists
    assert discrete_metric.distances([], []) == []

    # Test with single elements
    assert discrete_metric.distances([1], [1]) == [[0.0]]
    assert discrete_metric.distances([1], [2]) == [[1.0]]

    # Test with multiple elements
    xs = [1, 2, 3]
    ys = [1, 2, 4]
    expected = [[0.0, 1.0, 1.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0]]
    assert discrete_metric.distances(xs, ys) == expected


@pytest.mark.unit
def test_check_non_negativity(discrete_metric):
    """Test the non-negativity check."""
    # Test with valid distance
    discrete_metric.check_non_negativity(1, 1)
    discrete_metric.check_non_negativity(1, 2)

    # Test with negative distance (should raise exception)
    with patch.object(discrete_metric, "distance", return_value=-1.0):
        with pytest.raises(MetricViolationError):
            discrete_metric.check_non_negativity(1, 2)


@pytest.mark.unit
def test_check_identity(discrete_metric):
    """Test the identity axiom check."""
    # Test with identical inputs
    discrete_metric.check_identity(1, 1)
    discrete_metric.check_identity("test", "test")

    # Test with different inputs
    with pytest.raises(MetricViolationError):
        discrete_metric.check_identity(1, 2)

    with pytest.raises(MetricViolationError):
        discrete_metric.check_identity(1, 1)  # Shouldn't raise
        discrete_metric.distance = lambda x, y: 1.0
        with pytest.raises(MetricViolationError):
            discrete_metric.check_identity(1, 1)


@pytest.mark.unit
def test_check_symmetry(discrete_metric):
    """Test the symmetry axiom check."""
    # Test symmetric distances
    discrete_metric.check_symmetry(1, 2)
    discrete_metric.check_symmetry("a", "b")

    # Test asymmetric distances (should raise exception)
    with patch.object(discrete_metric, "distance", side_effect=[1.0, 2.0]):
        with pytest.raises(MetricViolationError):
            discrete_metric.check_symmetry(1, 2)


@pytest.mark.unit
def test_check_triangle_inequality(discrete_metric):
    """Test the triangle inequality check."""
    # Test valid triangle inequality
    discrete_metric.check_triangle_inequality(1, 2, 3)

    # Test violation of triangle inequality
    with patch.object(discrete_metric, "distance", side_effect=[0.0, 0.0, 2.0]):
        with pytest.raises(MetricViolationError):
            discrete_metric.check_triangle_inequality(1, 2, 3)


@pytest.mark.unit
def test_logging(discrete_metric):
    """Test if logging is properly implemented."""
    with patch("logging.Logger.debug") as mock_debug:
        # Test distance method logging
        discrete_metric.distance(1, 2)
        mock_debug.assert_called_once()

        # Test distances method logging
        discrete_metric.distances([1], [2])
        mock_debug.assert_called_again()

        # Test check methods logging
        discrete_metric.check_non_negativity(1, 2)
        mock_debug.assert_called_again()
