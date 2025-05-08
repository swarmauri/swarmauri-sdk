import pytest
import logging
from typing import Any, List, Tuple

from swarmauri_standard.metrics.DiscreteMetric import DiscreteMetric

# Configure logger
logger = logging.getLogger(__name__)


@pytest.fixture
def discrete_metric() -> DiscreteMetric:
    """
    Fixture that returns a DiscreteMetric instance.
    
    Returns
    -------
    DiscreteMetric
        A new instance of the DiscreteMetric class
    """
    return DiscreteMetric()


@pytest.mark.unit
def test_type():
    """
    Test that the type attribute is correctly set.
    """
    assert DiscreteMetric.type == "DiscreteMetric"


@pytest.mark.unit
def test_resource():
    """
    Test that the resource attribute is correctly inherited from MetricBase.
    """
    assert DiscreteMetric.resource == "Metric"


@pytest.mark.unit
@pytest.mark.parametrize("x, y, expected", [
    (1, 1, 0.0),
    (1, 2, 1.0),
    ("a", "a", 0.0),
    ("a", "b", 1.0),
    (True, True, 0.0),
    (True, False, 1.0),
    ((1, 2), (1, 2), 0.0),
    ((1, 2), (2, 1), 1.0),
    ([1, 2], [1, 2], 0.0),  # Lists with same elements in same order
    ([1, 2], [2, 1], 1.0),  # Lists with same elements in different order
])
def test_distance(discrete_metric: DiscreteMetric, x: Any, y: Any, expected: float):
    """
    Test the distance method with various inputs.
    
    Parameters
    ----------
    discrete_metric : DiscreteMetric
        The discrete metric instance
    x : Any
        First input value
    y : Any
        Second input value
    expected : float
        Expected distance value
    """
    assert discrete_metric.distance(x, y) == expected


@pytest.mark.unit
@pytest.mark.parametrize("x, y, expected", [
    (1, 1, True),
    (1, 2, False),
    ("a", "a", True),
    ("a", "b", False),
    (True, True, True),
    (True, False, False),
    ((1, 2), (1, 2), True),
    ((1, 2), (2, 1), False),
    ([1, 2], [1, 2], True),
    ([1, 2], [2, 1], False),
])
def test_are_identical(discrete_metric: DiscreteMetric, x: Any, y: Any, expected: bool):
    """
    Test the are_identical method with various inputs.
    
    Parameters
    ----------
    discrete_metric : DiscreteMetric
        The discrete metric instance
    x : Any
        First input value
    y : Any
        Second input value
    expected : bool
        Expected result
    """
    assert discrete_metric.are_identical(x, y) == expected


@pytest.mark.unit
def test_error_handling(discrete_metric: DiscreteMetric):
    """
    Test error handling in the discrete metric.
    
    Parameters
    ----------
    discrete_metric : DiscreteMetric
        The discrete metric instance
    """
    # Test with unhashable type (mutable dictionary)
    with pytest.raises(Exception):
        discrete_metric.distance({1: 2}, {1: 2})
    
    with pytest.raises(Exception):
        discrete_metric.are_identical({1: 2}, {1: 2})


@pytest.mark.unit
def test_serialization():
    """
    Test serialization and deserialization of DiscreteMetric.
    """
    # Create an instance
    original = DiscreteMetric()
    
    # Serialize to JSON
    json_data = original.model_dump_json()
    
    # Deserialize from JSON
    deserialized = DiscreteMetric.model_validate_json(json_data)
    
    # Check that the deserialized instance has the same type
    assert deserialized.type == original.type
    
    # Test the functionality of the deserialized instance
    assert deserialized.distance(1, 1) == 0.0
    assert deserialized.distance(1, 2) == 1.0


@pytest.mark.unit
def test_triangle_inequality(discrete_metric: DiscreteMetric):
    """
    Test that the discrete metric satisfies the triangle inequality.
    
    For any three points x, y, z, the distance from x to z should be less than
    or equal to the sum of the distance from x to y and the distance from y to z.
    
    Parameters
    ----------
    discrete_metric : DiscreteMetric
        The discrete metric instance
    """
    test_points = [1, 2, 3, "a", "b", True, False]
    
    for x in test_points:
        for y in test_points:
            for z in test_points:
                d_xz = discrete_metric.distance(x, z)
                d_xy = discrete_metric.distance(x, y)
                d_yz = discrete_metric.distance(y, z)
                
                # Check triangle inequality: d(x,z) ≤ d(x,y) + d(y,z)
                assert d_xz <= d_xy + d_yz, f"Triangle inequality failed for {x}, {y}, {z}"


@pytest.mark.unit
def test_symmetry(discrete_metric: DiscreteMetric):
    """
    Test that the discrete metric is symmetric.
    
    For any two points x and y, the distance from x to y should equal
    the distance from y to x.
    
    Parameters
    ----------
    discrete_metric : DiscreteMetric
        The discrete metric instance
    """
    test_points = [1, 2, "a", "b", True, False, (1, 2)]
    
    for x in test_points:
        for y in test_points:
            assert discrete_metric.distance(x, y) == discrete_metric.distance(y, x)