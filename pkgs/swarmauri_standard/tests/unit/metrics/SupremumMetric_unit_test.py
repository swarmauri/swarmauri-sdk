import pytest
from swarmauri_standard.metrics.SupremumMetric import SupremumMetric
import logging


@pytest.fixture
def supremum_metric():
    """Fixture to provide a SupremumMetric instance for testing."""
    return SupremumMetric()


@pytest.mark.unit
def test_supremum_metric_class_attributes(supremum_metric):
    """Test that class attributes are correctly set."""
    assert SupremumMetric.type == "SupremumMetric"
    assert SupremumMetric.resource == "metric"


@pytest.mark.unit
def test_supremum_metric_initialization(supremum_metric):
    """Test that the SupremumMetric instance initializes correctly."""
    assert supremum_metric.logger is not None
    assert isinstance(supremum_metric.logger, logging.Logger)


@pytest.mark.unit
def test_supremum_metric_distance(supremum_metric):
    """Test the distance method with various input types and edge cases."""
    # Test with valid vectors of the same length
    x = [1, 2, 3]
    y = [4, 5, 6]
    expected_distance = 3.0
    assert supremum_metric.distance(x, y) == expected_distance

    # Test with different lengths
    x = [1, 2]
    y = [3, 4, 5]
    with pytest.raises(ValueError):
        supremum_metric.distance(x, y)

    # Test with non-sequence inputs
    x = "test_string"
    y = "test_string"
    supremum_metric.distance(x, y)


@pytest.mark.unit
def test_supremum_metric_distances(supremum_metric):
    """Test the distances method with multiple points."""
    xs = [[1, 2], [3, 4]]
    ys = [[5, 6], [7, 8]]
    expected_distances = [
        [max(abs(1 - 5), abs(2 - 6)), max(abs(1 - 7), abs(2 - 8))],
        [max(abs(3 - 5), abs(4 - 6)), max(abs(3 - 7), abs(4 - 8))],
    ]
    result = supremum_metric.distances(xs, ys)
    assert result == expected_distances


@pytest.mark.unit
def test_supremum_metric_check_non_negativity(supremum_metric):
    """Test the non-negativity check."""
    x = [1, 2, 3]
    y = [1, 2, 3]
    supremum_metric.check_non_negativity(x, y)

    x = [1, 2, 3]
    y = [4, 5, 6]
    supremum_metric.check_non_negativity(x, y)


@pytest.mark.unit
def test_supremum_metric_check_identity(supremum_metric):
    """Test the identity check."""
    x = [1, 2, 3]
    y = [1, 2, 3]
    supremum_metric.check_identity(x, y)

    x = [1, 2, 3]
    y = [4, 5, 6]
    supremum_metric.check_identity(x, y)


@pytest.mark.unit
def test_supremum_metric_check_symmetry(supremum_metric):
    """Test the symmetry check."""
    x = [1, 2, 3]
    y = [4, 5, 6]
    supremum_metric.check_symmetry(x, y)


@pytest.mark.unit
def test_supremum_metric_check_triangle_inequality(supremum_metric):
    """Test the triangle inequality check."""
    x = [1, 2, 3]
    y = [4, 5, 6]
    z = [7, 8, 9]
    supremum_metric.check_triangle_inequality(x, y, z)


@pytest.mark.unit
def test_supremum_metric_distance_parameterized(supremum_metric):
    """Test distance method with different input types."""
    test_cases = [
        ([[1, 2], [3, 4]], 2.0),
        ((1, 2), (3, 4), 2.0),
        ([1, 2, 3], [4, 5, 6], 3.0),
    ]

    for x, y, expected in test_cases:
        assert supremum_metric.distance(x, y) == expected


@pytest.mark.unit
def test_supremum_metric_distance_edge_cases(supremum_metric):
    """Test edge cases for the distance method."""
    # Zero difference
    x = [1, 1, 1]
    y = [1, 1, 1]
    assert supremum_metric.distance(x, y) == 0.0

    # Single element vectors
    x = [5]
    y = [10]
    assert supremum_metric.distance(x, y) == 5.0

    # Empty vectors (should raise ValueError)
    x = []
    y = []
    with pytest.raises(ValueError):
        supremum_metric.distance(x, y)
