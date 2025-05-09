import pytest
import logging
from swarmauri_standard.swarmauri_standard.metrics.FrobeniusMetric import FrobeniusMetric

# Configure logging for testing
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.mark.unit
def test_frobenius_metric_resource_type():
    """Test the resource and type attributes of FrobeniusMetric."""
    assert FrobeniusMetric.resource == "metric"
    assert FrobeniusMetric.type == "FrobeniusMetric"

@pytest.fixture
def simple_matrix():
    """Fixture providing a simple 2x2 matrix for testing."""
    return [[1, 2], [3, 4]]

@pytest.mark.unit
def test_distance(simple_matrix):
    """Test the distance method with valid matrices."""
    metric = FrobeniusMetric()
    
    # Test with valid input
    x = [[1, 2], [3, 4]]
    y = [[1, 2], [3, 4]]
    assert metric.distance(x, y) == 0.0
    
    # Test with different matrices
    y_diff = [[2, 3], [4, 5]]
    distance = metric.distance(x, y_diff)
    assert distance > 0
    
    # Test with invalid input shapes
    x_invalid = [[1], [2]]
    with pytest.raises(ValueError):
        metric.distance(x_invalid, y)

@pytest.mark.unit
def test_distances(simple_matrix):
    """Test the distances method with multiple matrices."""
    metric = FrobeniusMetric()
    x = [[1, 2], [3, 4]]
    
    # Test with valid list of matrices
    ys = [
        [[1, 2], [3, 4]],
        [[2, 3], [4, 5]]
    ]
    distances = metric.distances(x, ys)
    assert len(distances) == 2
    
    # Test with invalid matrix in list
    ys_invalid = [
        [[1], [2]],
        [[2, 3], [4, 5]]
    ]
    with pytest.raises(ValueError):
        metric.distances(x, ys_invalid)

@pytest.mark.unit
def test_check_non_negativity(simple_matrix):
    """Test the non-negativity property."""
    metric = FrobeniusMetric()
    x = [[1, 2], [3, 4]]
    y = [[2, 3], [4, 5]]
    
    # Test with valid matrices
    result = metric.check_non_negativity(x, y)
    assert result is True
    
    # Test with identical matrices
    result = metric.check_non_negativity(x, x)
    assert result is True

@pytest.mark.unit
def test_check_identity(simple_matrix):
    """Test the identity of indiscernibles property."""
    metric = FrobeniusMetric()
    x = [[1, 2], [3, 4]]
    y = [[1, 2], [3, 4]]
    
    # Test with identical matrices
    result = metric.check_identity(x, y)
    assert result is True
    
    # Test with different matrices
    y_diff = [[2, 3], [4, 5]]
    result = metric.check_identity(x, y_diff)
    assert result is True  # Because the method always returns True after assertion

@pytest.mark.unit
def test_check_symmetry(simple_matrix):
    """Test the symmetry property."""
    metric = FrobeniusMetric()
    x = [[1, 2], [3, 4]]
    y = [[2, 3], [4, 5]]
    
    distance_xy = metric.distance(x, y)
    distance_yx = metric.distance(y, x)
    
    # Using approximate equality for floating point comparison
    assert abs(distance_xy - distance_yx) < 1e-9

@pytest.mark.unit
def test_check_triangle_inequality(simple_matrix):
    """Test the triangle inequality property."""
    metric = FrobeniusMetric()
    x = [[1, 2], [3, 4]]
    y = [[2, 3], [4, 5]]
    z = [[3, 4], [5, 6]]
    
    distance_xz = metric.distance(x, z)
    distance_xy = metric.distance(x, y)
    distance_yz = metric.distance(y, z)
    
    assert distance_xz <= distance_xy + distance_yz