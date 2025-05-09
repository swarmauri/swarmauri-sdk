import pytest
import logging
from swarmauri_standard.swarmauri_standard.metrics.EuclideanMetric import EuclideanMetric

@pytest.fixture
def euclidean_metric():
    """Fixture to provide a EuclideanMetric instance for testing."""
    return EuclideanMetric()

@pytest.mark.unit
def test_euclidean_metric_initialization(euclidean_metric):
    """Test the initialization of the EuclideanMetric class."""
    assert euclidean_metric.type == "EuclideanMetric"
    assert euclidean_metric.resource == "metric"

@pytest.mark.unit
def test_distance_valid_vectors(euclidean_metric):
    """Test the distance method with valid vector inputs."""
    x = [1.0, 2.0, 3.0]
    y = [4.0, 5.0, 6.0]
    distance = euclidean_metric.distance(x, y)
    assert isinstance(distance, float)
    assert distance >= 0.0

@pytest.mark.unit
def test_distance_different_lengths(euclidean_metric):
    """Test the distance method with vectors of different lengths."""
    x = [1.0, 2.0]
    y = [3.0, 4.0, 5.0]
    with pytest.raises(ValueError):
        euclidean_metric.distance(x, y)

@pytest.mark.unit
def test_distance_empty_vectors(euclidean_metric):
    """Test the distance method with empty vectors."""
    x = []
    y = []
    distance = euclidean_metric.distance(x, y)
    assert distance == 0.0

@pytest.mark.unit
def test_distances_multiple_vectors(euclidean_metric):
    """Test the distances method with multiple vector inputs."""
    x = [1.0, 2.0]
    ys = [[3.0, 4.0], [5.0, 6.0]]
    distances = euclidean_metric.distances(x, ys)
    assert len(distances) == 2
    assert all(isinstance(d, float) for d in distances)

@pytest.mark.unit
def test_check_non_negativity(euclidean_metric):
    """Test the non-negativity property check."""
    x = [1.0, 2.0]
    y = [3.0, 4.0]
    result = euclidean_metric.check_non_negativity(x, y)
    assert result is True

@pytest.mark.unit
def test_check_identity(euclidean_metric):
    """Test the identity property check."""
    x = [1.0, 2.0]
    y = [1.0, 2.0]
    result = euclidean_metric.check_identity(x, y)
    assert result is True

@pytest.mark.unit
def test_check_symmetry(euclidean_metric):
    """Test the symmetry property check."""
    x = [1.0, 2.0]
    y = [3.0, 4.0]
    result = euclidean_metric.check_symmetry(x, y)
    assert result is True

@pytest.mark.unit
def test_check_triangle_inequality(euclidean_metric):
    """Test the triangle inequality property check."""
    x = [1.0, 2.0]
    y = [3.0, 4.0]
    z = [5.0, 6.0]
    result = euclidean_metric.check_triangle_inequality(x, y, z)
    assert result is True

@pytest.mark.unit
def test_distance_same_vectors(euclidean_metric):
    """Test the distance method with identical vectors."""
    x = [1.0, 2.0, 3.0]
    y = [1.0, 2.0, 3.0]
    distance = euclidean_metric.distance(x, y)
    assert distance == 0.0

@pytest.mark.unit
def test_distance_zero_vectors(euclidean_metric):
    """Test the distance method with zero vectors."""
    x = [0.0, 0.0]
    y = [0.0, 0.0]
    distance = euclidean_metric.distance(x, y)
    assert distance == 0.0
    assert isinstance(distance, float)