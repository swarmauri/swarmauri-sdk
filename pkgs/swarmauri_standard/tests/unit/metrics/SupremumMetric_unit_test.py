import pytest
import numpy as np
import logging
from typing import List, Union, Tuple, Any

from swarmauri_standard.metrics.SupremumMetric import SupremumMetric

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def supremum_metric() -> SupremumMetric:
    """
    Fixture that provides a SupremumMetric instance for testing.
    
    Returns
    -------
    SupremumMetric
        An instance of the SupremumMetric class
    """
    return SupremumMetric()


@pytest.mark.unit
def test_resource():
    """
    Test that the resource attribute is correctly set.
    """
    assert SupremumMetric.resource == "Metric"


@pytest.mark.unit
def test_type():
    """
    Test that the type attribute is correctly set.
    """
    assert SupremumMetric.type == "SupremumMetric"


@pytest.mark.unit
def test_serialization(supremum_metric):
    """
    Test serialization and deserialization of SupremumMetric.
    
    Parameters
    ----------
    supremum_metric : SupremumMetric
        The metric instance from the fixture
    """
    # Serialize to JSON
    serialized = supremum_metric.model_dump_json()
    
    # Deserialize from JSON
    deserialized = SupremumMetric.model_validate_json(serialized)
    
    # Check that the deserialized object has the same attributes
    assert deserialized.type == supremum_metric.type
    assert deserialized.resource == supremum_metric.resource


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y, expected", [
        ([0, 0, 0], [0, 0, 0], 0.0),
        ([1, 2, 3], [1, 2, 3], 0.0),
        ([1, 2, 3], [4, 5, 6], 3.0),
        ([1, 2, 3], [1, 5, 3], 3.0),
        ([-1, -2, -3], [1, 2, 3], 6.0),
        ([0.1, 0.2, 0.3], [0.2, 0.3, 0.4], 0.1),
        ([[1, 2], [3, 4]], [[5, 6], [7, 8]], 4.0),
    ]
)
def test_distance(supremum_metric: SupremumMetric, x: Union[List[float], np.ndarray], 
                  y: Union[List[float], np.ndarray], expected: float):
    """
    Test the distance method with various input vectors.
    
    Parameters
    ----------
    supremum_metric : SupremumMetric
        The metric instance from the fixture
    x : Union[List[float], np.ndarray]
        First input vector
    y : Union[List[float], np.ndarray]
        Second input vector
    expected : float
        Expected distance value
    """
    result = supremum_metric.distance(x, y)
    assert np.isclose(result, expected)


@pytest.mark.unit
def test_distance_with_numpy_arrays(supremum_metric: SupremumMetric):
    """
    Test the distance method with numpy arrays.
    
    Parameters
    ----------
    supremum_metric : SupremumMetric
        The metric instance from the fixture
    """
    x = np.array([1.0, 2.0, 3.0])
    y = np.array([4.0, 6.0, 5.0])
    expected = 4.0  # Max absolute difference is at index 1: |2-6| = 4
    
    result = supremum_metric.distance(x, y)
    assert np.isclose(result, expected)


@pytest.mark.unit
def test_distance_with_different_dimensions(supremum_metric: SupremumMetric):
    """
    Test that the distance method raises ValueError when vectors have different dimensions.
    
    Parameters
    ----------
    supremum_metric : SupremumMetric
        The metric instance from the fixture
    """
    x = [1, 2, 3]
    y = [1, 2]
    
    with pytest.raises(ValueError) as excinfo:
        supremum_metric.distance(x, y)
    
    assert "Input vectors must have the same dimensions" in str(excinfo.value)


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y, expected", [
        ([0, 0, 0], [0, 0, 0], True),
        ([1, 2, 3], [1, 2, 3], True),
        ([1, 2, 3], [1, 2, 3.000000001], True),  # Testing epsilon tolerance
        ([1, 2, 3], [1, 2, 3.1], False),
        ([1, 2, 3], [4, 5, 6], False),
    ]
)
def test_are_identical(supremum_metric: SupremumMetric, x: Union[List[float], np.ndarray], 
                       y: Union[List[float], np.ndarray], expected: bool):
    """
    Test the are_identical method with various input vectors.
    
    Parameters
    ----------
    supremum_metric : SupremumMetric
        The metric instance from the fixture
    x : Union[List[float], np.ndarray]
        First input vector
    y : Union[List[float], np.ndarray]
        Second input vector
    expected : bool
        Expected result (True if vectors are identical, False otherwise)
    """
    result = supremum_metric.are_identical(x, y)
    assert result == expected


@pytest.mark.unit
def test_are_identical_with_invalid_inputs(supremum_metric: SupremumMetric):
    """
    Test the are_identical method with invalid inputs.
    
    Parameters
    ----------
    supremum_metric : SupremumMetric
        The metric instance from the fixture
    """
    x = [1, 2, 3]
    y = [1, 2]  # Different dimension
    
    # Should return False rather than raising exception
    result = supremum_metric.are_identical(x, y)
    assert result == False


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y, expected", [
        ([1, 2, 3], [4, 5, 6], True),
        ([[1, 2], [3, 4]], [[5, 6], [7, 8]], True),
        ([1, 2, 3], [1, 2], False),  # Different dimensions
        ([1, 2, 3], "invalid", False),  # Invalid type
        (None, [1, 2, 3], False),  # None value
    ]
)
def test_validate_inputs(supremum_metric: SupremumMetric, x: Any, y: Any, expected: bool):
    """
    Test the validate_inputs method with various inputs.
    
    Parameters
    ----------
    supremum_metric : SupremumMetric
        The metric instance from the fixture
    x : Any
        First input to validate
    y : Any
        Second input to validate
    expected : bool
        Expected validation result
    """
    result = supremum_metric.validate_inputs(x, y)
    assert result == expected


@pytest.mark.unit
def test_edge_case_zero_distance(supremum_metric: SupremumMetric):
    """
    Test edge case where distance is exactly zero.
    
    Parameters
    ----------
    supremum_metric : SupremumMetric
        The metric instance from the fixture
    """
    x = [0, 0, 0]
    y = [0, 0, 0]
    
    assert supremum_metric.distance(x, y) == 0.0
    assert supremum_metric.are_identical(x, y) == True


@pytest.mark.unit
def test_edge_case_large_values(supremum_metric: SupremumMetric):
    """
    Test edge case with very large values.
    
    Parameters
    ----------
    supremum_metric : SupremumMetric
        The metric instance from the fixture
    """
    x = [1e10, 2e10, 3e10]
    y = [1e10, 5e10, 3e10]
    
    expected = 3e10  # |2e10 - 5e10| = 3e10
    result = supremum_metric.distance(x, y)
    
    assert np.isclose(result, expected)


@pytest.mark.unit
def test_edge_case_negative_values(supremum_metric: SupremumMetric):
    """
    Test edge case with negative values.
    
    Parameters
    ----------
    supremum_metric : SupremumMetric
        The metric instance from the fixture
    """
    x = [-1, -2, -3]
    y = [-4, -5, -6]
    
    expected = 3.0  # Max of |(-1)-(-4)|, |(-2)-(-5)|, |(-3)-(-6)| = 3
    result = supremum_metric.distance(x, y)
    
    assert np.isclose(result, expected)