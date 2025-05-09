import pytest
from swarmauri_standard.swarmauri_standard.metrics.DiscreteMetric import DiscreteMetric
import logging

logger = logging.getLogger(__name__)

@pytest.mark.unit
def test_type():
    """Test the type property of the DiscreteMetric class."""
    assert DiscreteMetric.type == "DiscreteMetric"

@pytest.mark.unit
def test_distance_same_objects():
    """Test distance method with identical objects."""
    obj = "test_object"
    assert DiscreteMetric().distance(obj, obj) == 0.0

@pytest.mark.unit
def test_distance_different_objects():
    """Test distance method with different objects."""
    obj1 = "object1"
    obj2 = "object2"
    assert DiscreteMetric().distance(obj1, obj2) == 1.0

@pytest.mark.unit
def test_distance_different_types():
    """Test distance method with different types."""
    obj1 = 123
    obj2 = "456"
    assert DiscreteMetric().distance(obj1, obj2) == 1.0

@pytest.mark.unit
def test_distances_single():
    """Test distances method with single point."""
    obj = "test_point"
    metric = DiscreteMetric()
    assert metric.distances(obj, None) == 0.0

@pytest.mark.unit
def test_distances_multiple():
    """Test distances method with multiple points."""
    obj = "test_point"
    other1 = "different_point"
    other2 = "another_point"
    metric = DiscreteMetric()
    distances = metric.distances(obj, [other1, other2])
    assert all(d == 1.0 for d in distances)

@pytest.mark.unit
def test_non_negativity():
    """Test non-negativity property."""
    obj1 = "obj1"
    obj2 = "obj2"
    assert DiscreteMetric().check_non_negativity(obj1, obj2)

@pytest.mark.unit
def test_identity_true():
    """Test identity check when objects are the same."""
    obj = [1, 2, 3]
    assert DiscreteMetric().check_identity(obj, obj)

@pytest.mark.unit
def test_identity_false():
    """Test identity check when objects are different."""
    obj1 = [1, 2, 3]
    obj2 = [1, 2, 4]
    assert not DiscreteMetric().check_identity(obj1, obj2)

@pytest.mark.unit
def test_symmetry():
    """Test symmetry property."""
    obj1 = {"a": 1}
    obj2 = {"a": 2}
    metric = DiscreteMetric()
    assert metric.check_symmetry(obj1, obj2)

@pytest.mark.unit
def test_triangle_inequality():
    """Test triangle inequality property."""
    obj1 = "point1"
    obj2 = "point2"
    obj3 = "point3"
    metric = DiscreteMetric()
    assert metric.check_triangle_inequality(obj1, obj2, obj3)