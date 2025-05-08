import pytest
import numpy as np
import logging
from typing import List, Tuple, Any

from swarmauri_standard.metrics.FrobeniusMetric import FrobeniusMetric

# Configure logger for tests
logger = logging.getLogger(__name__)

@pytest.fixture
def frobenius_metric() -> FrobeniusMetric:
    """
    Fixture to create a FrobeniusMetric instance for testing.
    
    Returns
    -------
    FrobeniusMetric
        An instance of FrobeniusMetric
    """
    return FrobeniusMetric()

@pytest.mark.unit
def test_type_attribute():
    """Test that the type attribute is correctly set."""
    metric = FrobeniusMetric()
    assert metric.type == "FrobeniusMetric"

@pytest.mark.unit
def test_validator_accepts_correct_type():
    """Test that the type validator accepts the correct type."""
    metric = FrobeniusMetric(type="FrobeniusMetric")
    assert metric.type == "FrobeniusMetric"

@pytest.mark.unit
def test_validator_rejects_incorrect_type():
    """Test that the type validator rejects incorrect types."""
    with pytest.raises(ValueError):
        FrobeniusMetric(type="WrongType")

@pytest.mark.unit
@pytest.mark.parametrize("x, y, expected", [
    # 1x1 matrices (scalars)
    ([[0]], [[0]], 0.0),
    ([[3]], [[4]], 1.0),
    
    # 2x2 matrices
    ([[1, 2], [3, 4]], [[1, 2], [3, 4]], 0.0),
    ([[1, 2], [3, 4]], [[5, 6], [7, 8]], 8.0),
    
    # 3x3 matrices
    (
        [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        0.0
    ),
    (
        [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        [[9, 8, 7], [6, 5, 4], [3, 2, 1]],
        12.0  # sqrt(288)
    ),
    
    # Vectors
    ([1, 2, 3], [1, 2, 3], 0.0),
    ([1, 2, 3], [4, 5, 6], 5.196152422706632),  # sqrt(27)
])
def test_distance(frobenius_metric: FrobeniusMetric, x: List[List[float]], y: List[List[float]], expected: float):
    """
    Test the distance method with various matrix inputs.
    
    Parameters
    ----------
    frobenius_metric : FrobeniusMetric
        The metric instance to test
    x : List[List[float]]
        First matrix
    y : List[List[float]]
        Second matrix
    expected : float
        Expected distance value
    """
    result = frobenius_metric.distance(x, y)
    assert np.isclose(result, expected)

@pytest.mark.unit
def test_distance_with_numpy_arrays(frobenius_metric: FrobeniusMetric):
    """Test the distance method with numpy array inputs."""
    x = np.array([[1, 2], [3, 4]])
    y = np.array([[5, 6], [7, 8]])
    result = frobenius_metric.distance(x, y)
    assert np.isclose(result, 8.0)

@pytest.mark.unit
def test_distance_with_incompatible_shapes(frobenius_metric: FrobeniusMetric):
    """Test that the distance method raises an error for incompatible shapes."""
    x = [[1, 2], [3, 4]]
    y = [[1, 2, 3], [4, 5, 6]]
    with pytest.raises(ValueError):
        frobenius_metric.distance(x, y)

@pytest.mark.unit
def test_distance_with_invalid_inputs(frobenius_metric: FrobeniusMetric):
    """Test that the distance method raises an error for invalid inputs."""
    x = [[1, 2], [3, "4"]]  # String can't be converted to float
    y = [[1, 2], [3, 4]]
    with pytest.raises(TypeError):
        frobenius_metric.distance(x, y)

@pytest.mark.unit
@pytest.mark.parametrize("x, y, expected", [
    # Identical matrices
    ([[1, 2], [3, 4]], [[1, 2], [3, 4]], True),
    
    # Almost identical (floating point precision)
    ([[1.0000001, 2], [3, 4]], [[1, 2], [3, 4]], True),
    
    # Different matrices
    ([[1, 2], [3, 4]], [[5, 6], [7, 8]], False),
])
def test_are_identical(frobenius_metric: FrobeniusMetric, x: List[List[float]], y: List[List[float]], expected: bool):
    """
    Test the are_identical method with various matrix inputs.
    
    Parameters
    ----------
    frobenius_metric : FrobeniusMetric
        The metric instance to test
    x : List[List[float]]
        First matrix
    y : List[List[float]]
        Second matrix
    expected : bool
        Expected result
    """
    result = frobenius_metric.are_identical(x, y)
    assert result == expected

@pytest.mark.unit
def test_validate_inputs_valid_data(frobenius_metric: FrobeniusMetric):
    """Test that validate_inputs correctly processes valid inputs."""
    x = [[1, 2], [3, 4]]
    y = [[5, 6], [7, 8]]
    x_array, y_array = frobenius_metric.validate_inputs(x, y)
    
    assert isinstance(x_array, np.ndarray)
    assert isinstance(y_array, np.ndarray)
    assert x_array.shape == (2, 2)
    assert y_array.shape == (2, 2)
    
@pytest.mark.unit
def test_validate_inputs_incompatible_shapes(frobenius_metric: FrobeniusMetric):
    """Test that validate_inputs raises an error for incompatible shapes."""
    x = [[1, 2], [3, 4]]
    y = [[1, 2, 3], [4, 5, 6]]
    with pytest.raises(ValueError):
        frobenius_metric.validate_inputs(x, y)

@pytest.mark.unit
def test_validate_inputs_invalid_dimensions(frobenius_metric: FrobeniusMetric):
    """Test that validate_inputs raises an error for invalid dimensions."""
    # Test with 0-dimensional data
    with pytest.raises(ValueError):
        frobenius_metric.validate_inputs(5, 10)

@pytest.mark.unit
def test_serialization():
    """Test serialization and deserialization of FrobeniusMetric."""
    original_metric = FrobeniusMetric()
    json_data = original_metric.model_dump_json()
    
    # Deserialize
    deserialized_metric = FrobeniusMetric.model_validate_json(json_data)
    
    # Check that they're equivalent
    assert deserialized_metric.type == original_metric.type
    assert isinstance(deserialized_metric, FrobeniusMetric)

@pytest.mark.unit
def test_edge_case_empty_arrays(frobenius_metric: FrobeniusMetric):
    """Test behavior with empty arrays."""
    x = np.array([[]])
    y = np.array([[]])
    
    # This should work without errors and return 0
    result = frobenius_metric.distance(x, y)
    assert np.isclose(result, 0.0)

@pytest.mark.unit
def test_edge_case_large_matrices(frobenius_metric: FrobeniusMetric):
    """Test behavior with large matrices."""
    # Create two 100x100 matrices
    x = np.ones((100, 100))
    y = np.ones((100, 100)) * 2
    
    # Expected distance: sqrt(100*100*1²) = 100
    result = frobenius_metric.distance(x, y)
    assert np.isclose(result, 100.0)