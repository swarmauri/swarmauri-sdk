import pytest
import numpy as np
import logging
from typing import List, Union

from swarmauri_standard.metrics.EuclideanMetric import EuclideanMetric

# Configure logger for tests
logger = logging.getLogger(__name__)


@pytest.fixture
def euclidean_metric():
    """
    Fixture that returns an instance of EuclideanMetric.
    
    Returns
    -------
    EuclideanMetric
        An instance of the EuclideanMetric class
    """
    return EuclideanMetric()


@pytest.mark.unit
def test_euclidean_metric_type():
    """Test that the type attribute is correctly set."""
    metric = EuclideanMetric()
    assert metric.type == "EuclideanMetric"


@pytest.mark.unit
def test_euclidean_metric_resource():
    """Test that the resource attribute is correctly set."""
    assert EuclideanMetric.resource == "Metric"


@pytest.mark.unit
def test_serialization_deserialization():
    """Test that the metric can be properly serialized and deserialized."""
    metric = EuclideanMetric()
    serialized = metric.model_dump_json()
    deserialized = EuclideanMetric.model_validate_json(serialized)
    
    assert isinstance(deserialized, EuclideanMetric)
    assert deserialized.type == metric.type


@pytest.mark.unit
@pytest.mark.parametrize("x, y, expected", [
    ([0, 0], [3, 4], 5.0),                      # 3-4-5 triangle
    ([1, 2, 3], [4, 5, 6], np.sqrt(27)),        # 3D vector
    ([0, 0, 0, 0], [1, 1, 1, 1], 2.0),          # 4D vector
    ([-1, -1], [1, 1], 2.0 * np.sqrt(2)),       # Negative values
    ([0.5, 0.5], [0.5, 0.5], 0.0),              # Identical vectors
    (np.array([1, 2]), np.array([3, 4]), np.sqrt(8)),  # NumPy arrays
])
def test_distance_calculation(euclidean_metric, x, y, expected):
    """
    Test Euclidean distance calculation with various vector inputs.
    
    Parameters
    ----------
    euclidean_metric : EuclideanMetric
        The metric instance from the fixture
    x : Union[List[float], np.ndarray]
        First vector
    y : Union[List[float], np.ndarray]
        Second vector
    expected : float
        Expected distance value
    """
    distance = euclidean_metric.distance(x, y)
    assert np.isclose(distance, expected)


@pytest.mark.unit
def test_distance_symmetry(euclidean_metric):
    """Test that the distance is symmetric: d(x,y) = d(y,x)."""
    x = [1, 2, 3]
    y = [4, 5, 6]
    
    distance_xy = euclidean_metric.distance(x, y)
    distance_yx = euclidean_metric.distance(y, x)
    
    assert np.isclose(distance_xy, distance_yx)


@pytest.mark.unit
def test_distance_non_negativity(euclidean_metric):
    """Test that the distance is always non-negative: d(x,y) ≥ 0."""
    x = [-10, -20, -30]
    y = [-5, -15, -25]
    
    distance = euclidean_metric.distance(x, y)
    
    assert distance >= 0


@pytest.mark.unit
def test_distance_identity(euclidean_metric):
    """Test that distance between identical vectors is zero: d(x,x) = 0."""
    x = [1.5, 2.5, 3.5]
    
    distance = euclidean_metric.distance(x, x)
    
    assert np.isclose(distance, 0.0)


@pytest.mark.unit
def test_triangle_inequality(euclidean_metric):
    """Test that the triangle inequality holds: d(x,z) ≤ d(x,y) + d(y,z)."""
    x = [0, 0]
    y = [1, 1]
    z = [2, 0]
    
    distance_xz = euclidean_metric.distance(x, z)
    distance_xy = euclidean_metric.distance(x, y)
    distance_yz = euclidean_metric.distance(y, z)
    
    assert distance_xz <= distance_xy + distance_yz


@pytest.mark.unit
@pytest.mark.parametrize("x, y, expected", [
    ([1, 2, 3], [1, 2, 3], True),               # Identical vectors
    ([0.1, 0.2], [0.1, 0.2], True),             # Identical decimal vectors
    ([1, 2], [1.000000001, 2], True),           # Nearly identical (within epsilon)
    ([1, 2], [1.1, 2], False),                  # Different vectors
    (np.array([5, 5]), np.array([5, 5]), True), # Identical NumPy arrays
])
def test_are_identical(euclidean_metric, x, y, expected):
    """
    Test the are_identical method with various inputs.
    
    Parameters
    ----------
    euclidean_metric : EuclideanMetric
        The metric instance from the fixture
    x : Union[List[float], np.ndarray]
        First vector
    y : Union[List[float], np.ndarray]
        Second vector
    expected : bool
        Expected result of identity check
    """
    result = euclidean_metric.are_identical(x, y)
    assert result == expected


@pytest.mark.unit
def test_different_dimensions_error(euclidean_metric):
    """Test that an error is raised when vectors have different dimensions."""
    x = [1, 2, 3]
    y = [4, 5]
    
    with pytest.raises(ValueError) as excinfo:
        euclidean_metric.distance(x, y)
    
    assert "same dimensions" in str(excinfo.value)


@pytest.mark.unit
def test_invalid_input_type_error(euclidean_metric):
    """Test that an error is raised for invalid input types."""
    x = [1, 2, 3]
    y = ["a", "b", "c"]  # Non-numeric values
    
    with pytest.raises(TypeError) as excinfo:
        euclidean_metric.distance(x, y)
    
    assert "numeric arrays or lists" in str(excinfo.value)