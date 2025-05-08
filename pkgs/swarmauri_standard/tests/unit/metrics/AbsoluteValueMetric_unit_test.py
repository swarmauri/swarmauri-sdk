import pytest
import logging
import numpy as np
from typing import Union

from swarmauri_standard.metrics.AbsoluteValueMetric import AbsoluteValueMetric

# Configure logger for testing
logger = logging.getLogger(__name__)


@pytest.fixture
def absolute_value_metric():
    """
    Fixture that provides an instance of AbsoluteValueMetric.
    
    Returns
    -------
    AbsoluteValueMetric
        A new instance of the AbsoluteValueMetric class
    """
    return AbsoluteValueMetric()


@pytest.mark.unit
def test_type():
    """
    Test that the type attribute is set correctly.
    """
    assert AbsoluteValueMetric.type == "AbsoluteValueMetric"


@pytest.mark.unit
def test_resource():
    """
    Test that the resource attribute is set correctly.
    """
    assert AbsoluteValueMetric.resource == "Metric"


@pytest.mark.unit
def test_serialization():
    """
    Test serialization and deserialization of the AbsoluteValueMetric.
    """
    metric = AbsoluteValueMetric()
    serialized = metric.model_dump_json()
    deserialized = AbsoluteValueMetric.model_validate_json(serialized)
    
    assert isinstance(deserialized, AbsoluteValueMetric)
    assert deserialized.type == metric.type


@pytest.mark.unit
@pytest.mark.parametrize("x, y, expected", [
    (5, 10, 5.0),
    (10, 5, 5.0),
    (0, 0, 0.0),
    (-5, 5, 10.0),
    (3.5, 2.5, 1.0),
    (0, -7, 7.0),
])
def test_distance_calculation(absolute_value_metric, x, y, expected):
    """
    Test the distance calculation with various inputs.
    
    Parameters
    ----------
    absolute_value_metric : AbsoluteValueMetric
        The metric instance from the fixture
    x : Union[int, float]
        First scalar value
    y : Union[int, float]
        Second scalar value
    expected : float
        Expected distance value
    """
    result = absolute_value_metric.distance(x, y)
    assert result == expected
    
    # Test symmetry
    result_reversed = absolute_value_metric.distance(y, x)
    assert result == result_reversed


@pytest.mark.unit
def test_distance_with_invalid_inputs(absolute_value_metric):
    """
    Test that the distance method raises TypeError for non-scalar inputs.
    
    Parameters
    ----------
    absolute_value_metric : AbsoluteValueMetric
        The metric instance from the fixture
    """
    with pytest.raises(TypeError):
        absolute_value_metric.distance("string", 5)
    
    with pytest.raises(TypeError):
        absolute_value_metric.distance(5, [1, 2, 3])
    
    with pytest.raises(TypeError):
        absolute_value_metric.distance({}, None)


@pytest.mark.unit
@pytest.mark.parametrize("x, y, expected", [
    (5, 5, True),
    (5, 5.000000001, True),  # Should be within epsilon
    (5, 6, False),
    (0, 0, True),
    (-5, -5, True),
    (-5, 5, False),
    (3.5, 3.5, True),
])
def test_are_identical(absolute_value_metric, x, y, expected):
    """
    Test the are_identical method with various inputs.
    
    Parameters
    ----------
    absolute_value_metric : AbsoluteValueMetric
        The metric instance from the fixture
    x : Union[int, float]
        First scalar value
    y : Union[int, float]
        Second scalar value
    expected : bool
        Expected result
    """
    result = absolute_value_metric.are_identical(x, y)
    assert result == expected


@pytest.mark.unit
def test_are_identical_with_invalid_inputs(absolute_value_metric):
    """
    Test that the are_identical method raises TypeError for non-scalar inputs.
    
    Parameters
    ----------
    absolute_value_metric : AbsoluteValueMetric
        The metric instance from the fixture
    """
    with pytest.raises(TypeError):
        absolute_value_metric.are_identical("string", 5)
    
    with pytest.raises(TypeError):
        absolute_value_metric.are_identical(5, [1, 2, 3])


@pytest.mark.unit
@pytest.mark.parametrize("x, y, z", [
    (0, 5, 10),
    (-5, 0, 5),
    (3.5, 7.2, 10.1),
    (100, 50, 25),
])
def test_validate_metric_axioms(absolute_value_metric, x, y, z):
    """
    Test that the absolute value metric satisfies all metric axioms.
    
    Parameters
    ----------
    absolute_value_metric : AbsoluteValueMetric
        The metric instance from the fixture
    x : Union[int, float]
        First test scalar value
    y : Union[int, float]
        Second test scalar value
    z : Union[int, float]
        Third test scalar value
    """
    assert absolute_value_metric.validate_metric_axioms(x, y, z) is True
    
    # Test non-negativity directly
    assert absolute_value_metric.distance(x, y) >= 0
    
    # Test symmetry directly
    assert absolute_value_metric.distance(x, y) == absolute_value_metric.distance(y, x)
    
    # Test identity of indiscernibles
    assert (absolute_value_metric.distance(x, x) == 0)
    
    # Test triangle inequality directly
    d_xz = absolute_value_metric.distance(x, z)
    d_xy = absolute_value_metric.distance(x, y)
    d_yz = absolute_value_metric.distance(y, z)
    assert d_xz <= d_xy + d_yz


@pytest.mark.unit
def test_inheritance():
    """
    Test that AbsoluteValueMetric inherits from MetricBase.
    """
    from swarmauri_base.metrics.MetricBase import MetricBase
    
    assert issubclass(AbsoluteValueMetric, MetricBase)