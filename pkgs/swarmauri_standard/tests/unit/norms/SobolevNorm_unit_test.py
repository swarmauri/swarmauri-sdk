import pytest
import numpy as np
import logging
from unittest.mock import MagicMock
from swarmauri_standard.norms.SobolevNorm import SobolevNorm

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
def default_norm():
    """
    Fixture providing a default SobolevNorm instance.
    
    Returns
    -------
    SobolevNorm
        A default SobolevNorm instance with weights=[1.0, 1.0] and max_order=1
    """
    return SobolevNorm()

@pytest.fixture
def custom_norm():
    """
    Fixture providing a customized SobolevNorm instance.
    
    Returns
    -------
    SobolevNorm
        A SobolevNorm instance with weights=[0.5, 1.0, 2.0] and max_order=2
    """
    return SobolevNorm(weights=[0.5, 1.0, 2.0], max_order=2)

@pytest.mark.unit
def test_initialization():
    """Test the initialization of SobolevNorm with different parameters."""
    # Test default initialization
    norm = SobolevNorm()
    assert norm.weights == [1.0, 1.0]
    assert norm.max_order == 1
    
    # Test custom initialization
    norm = SobolevNorm(weights=[0.5, 1.0, 2.0], max_order=2)
    assert norm.weights == [0.5, 1.0, 2.0]
    assert norm.max_order == 2
    
    # Test weight adjustment when too short
    norm = SobolevNorm(weights=[0.5], max_order=2)
    assert len(norm.weights) == 3
    assert norm.weights[0] == 0.5
    
    # Test weight adjustment when too long
    norm = SobolevNorm(weights=[0.5, 1.0, 1.5, 2.0], max_order=1)
    assert len(norm.weights) == 2
    assert norm.weights == [0.5, 1.0]

@pytest.mark.unit
def test_type_and_resource():
    """Test the type and resource attributes of SobolevNorm."""
    norm = SobolevNorm()
    assert norm.type == "SobolevNorm"
    assert norm.resource == "Norm"

@pytest.mark.unit
def test_name(default_norm, custom_norm):
    """Test the name method returns the expected string identifier."""
    assert default_norm.name() == "SobolevNorm(max_order=1, weights=[1.0, 1.0])"
    assert custom_norm.name() == "SobolevNorm(max_order=2, weights=[0.5, 1.0, 2.0])"

@pytest.mark.unit
def test_default_derivative_fn(default_norm):
    """Test the default derivative function implementation."""
    # Test zero-order derivative (identity)
    x = np.array([1.0, 2.0, 3.0, 4.0])
    assert np.array_equal(default_norm._default_derivative_fn(x, 0), x)
    
    # Test first-order derivative (finite difference)
    expected_first_derivative = np.array([1.0, 1.0, 1.0, 0.0])
    np.testing.assert_array_equal(default_norm._default_derivative_fn(x, 1), expected_first_derivative)
    
    # Test second-order derivative
    expected_second_derivative = np.array([0.0, 0.0, -1.0, 0.0])
    np.testing.assert_array_equal(default_norm._default_derivative_fn(x, 2), expected_second_derivative)
    
    # Test empty array
    empty = np.array([])
    assert np.array_equal(default_norm._default_derivative_fn(empty, 0), empty)
    assert np.array_equal(default_norm._default_derivative_fn(empty, 1), empty)

@pytest.mark.unit
def test_compute_with_different_inputs(default_norm):
    """Test compute method with different types of inputs."""
    # Test with numpy array
    x_array = np.array([1.0, 2.0, 3.0, 4.0])
    norm_value = default_norm.compute(x_array)
    assert isinstance(norm_value, float)
    assert norm_value > 0
    
    # Test with list
    x_list = [1.0, 2.0, 3.0, 4.0]
    assert default_norm.compute(x_list) == norm_value
    
    # Test with tuple
    x_tuple = (1.0, 2.0, 3.0, 4.0)
    assert default_norm.compute(x_tuple) == norm_value
    
    # Test with empty array
    assert default_norm.compute(np.array([])) == 0.0
    
    # Test with invalid input type
    with pytest.raises(TypeError):
        default_norm.compute("not a vector")

@pytest.mark.unit
def test_compute_with_custom_weights(custom_norm):
    """Test compute method with custom weights for different derivative orders."""
    x = np.array([1.0, 2.0, 3.0, 4.0])
    
    # Calculate expected norm value manually
    # For this array:
    # - 0th derivative (original): [1.0, 2.0, 3.0, 4.0]
    # - 1st derivative: [1.0, 1.0, 1.0, 0.0]
    # - 2nd derivative: [0.0, 0.0, -1.0, 0.0]
    
    zeroth_order_contribution = 0.5 * (1**2 + 2**2 + 3**2 + 4**2)  # weight=0.5
    first_order_contribution = 1.0 * (1**2 + 1**2 + 1**2 + 0**2)   # weight=1.0
    second_order_contribution = 2.0 * (0**2 + 0**2 + (-1)**2 + 0**2)  # weight=2.0
    
    expected_norm_squared = zeroth_order_contribution + first_order_contribution + second_order_contribution
    expected_norm = np.sqrt(expected_norm_squared)
    
    assert np.isclose(custom_norm.compute(x), expected_norm)

@pytest.mark.unit
def test_distance(default_norm):
    """Test the distance method for computing Sobolev distance between vectors."""
    x = np.array([1.0, 2.0, 3.0, 4.0])
    y = np.array([2.0, 3.0, 4.0, 5.0])
    
    # Distance should be the norm of the difference
    expected_distance = default_norm.compute(x - y)
    actual_distance = default_norm.distance(x, y)
    
    assert np.isclose(actual_distance, expected_distance)
    
    # Test with incompatible dimensions
    with pytest.raises(ValueError):
        default_norm.distance(x, np.array([1.0, 2.0]))
    
    # Test with invalid input types
    with pytest.raises(TypeError):
        default_norm.distance(x, "not a vector")
    with pytest.raises(TypeError):
        default_norm.distance("not a vector", y)

@pytest.mark.unit
def test_normalize(default_norm):
    """Test the normalize method for creating unit norm vectors."""
    x = np.array([2.0, 0.0, 0.0, 0.0])  # Simple vector for predictable derivatives
    
    normalized = default_norm.normalize(x)
    
    # Check that the normalized vector has unit norm
    assert np.isclose(default_norm.compute(normalized), 1.0)
    
    # Check that direction is preserved (proportional to original)
    assert np.allclose(normalized / x[0], np.array([1/default_norm.compute(x), 0.0, 0.0, 0.0]))
    
    # Test with zero vector
    with pytest.raises(ValueError):
        default_norm.normalize(np.zeros(4))
    
    # Test with list input (should return list)
    x_list = [2.0, 0.0, 0.0, 0.0]
    normalized_list = default_norm.normalize(x_list)
    assert isinstance(normalized_list, list)
    assert np.isclose(default_norm.compute(normalized_list), 1.0)
    
    # Test with tuple input (should return tuple)
    x_tuple = (2.0, 0.0, 0.0, 0.0)
    normalized_tuple = default_norm.normalize(x_tuple)
    assert isinstance(normalized_tuple, tuple)
    assert np.isclose(default_norm.compute(normalized_tuple), 1.0)

@pytest.mark.unit
def test_is_normalized(default_norm):
    """Test the is_normalized method for checking unit norm vectors."""
    # Create a normalized vector
    x = np.array([2.0, 0.0, 0.0, 0.0])
    normalized = default_norm.normalize(x)
    
    # Test with normalized vector
    assert default_norm.is_normalized(normalized)
    
    # Test with non-normalized vector
    assert not default_norm.is_normalized(x)
    
    # Test with almost normalized vector (within tolerance)
    almost_normalized = normalized * 1.000000001
    assert default_norm.is_normalized(almost_normalized)
    
    # Test with almost normalized vector (outside tolerance)
    almost_normalized = normalized * 1.1
    assert not default_norm.is_normalized(almost_normalized)
    
    # Test with custom tolerance
    slightly_off = normalized * 1.05
    assert not default_norm.is_normalized(slightly_off, tolerance=0.01)
    assert default_norm.is_normalized(slightly_off, tolerance=0.1)

@pytest.mark.unit
def test_set_weights(default_norm):
    """Test the set_weights method for updating weights."""
    new_weights = [0.5, 1.5]
    default_norm.set_weights(new_weights)
    assert default_norm.weights == new_weights
    
    # Test with incompatible weights length
    with pytest.raises(ValueError):
        default_norm.set_weights([0.5, 1.0, 1.5])  # Too many weights for max_order=1

@pytest.mark.unit
def test_set_derivative_function(default_norm):
    """Test setting a custom derivative function."""
    # Create a mock derivative function
    mock_derivative_fn = MagicMock(return_value=np.array([1.0, 1.0]))
    
    # Set the custom function
    default_norm.set_derivative_function(mock_derivative_fn)
    
    # Verify the function was set
    assert default_norm.derivative_fn == mock_derivative_fn
    
    # Test that the custom function is used
    x = np.array([1.0, 2.0])
    default_norm.compute(x)
    
    # Verify the mock was called with expected arguments
    mock_derivative_fn.assert_any_call(x, 0)
    mock_derivative_fn.assert_any_call(x, 1)

@pytest.mark.unit
def test_serialization(default_norm, custom_norm):
    """Test serialization and deserialization of SobolevNorm instances."""