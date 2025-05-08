import pytest
import numpy as np
import logging
from typing import Callable
from numpy.typing import NDArray

from swarmauri_standard.inner_products.WeightedL2 import WeightedL2

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Simple test grid and functions
@pytest.fixture
def grid():
    """
    Fixture providing a simple 1D grid for testing.
    
    Returns
    -------
    NDArray
        A numpy array representing a uniformly spaced grid from 0 to 1
    """
    return np.linspace(0, 1, 100)

@pytest.fixture
def constant_weight_function() -> Callable[[NDArray], NDArray]:
    """
    Fixture providing a constant weight function.
    
    Returns
    -------
    Callable[[NDArray], NDArray]
        A function that returns a constant weight of 1.0 for any input
    """
    def weight_func(x: NDArray) -> NDArray:
        return np.ones_like(x)
    return weight_func

@pytest.fixture
def variable_weight_function() -> Callable[[NDArray], NDArray]:
    """
    Fixture providing a variable weight function.
    
    Returns
    -------
    Callable[[NDArray], NDArray]
        A function that returns a position-dependent weight (x+1)
    """
    def weight_func(x: NDArray) -> NDArray:
        return x + 1.0
    return weight_func

@pytest.fixture
def invalid_weight_function() -> Callable[[NDArray], NDArray]:
    """
    Fixture providing an invalid weight function (has negative values).
    
    Returns
    -------
    Callable[[NDArray], NDArray]
        A function that returns some negative weights
    """
    def weight_func(x: NDArray) -> NDArray:
        return x - 0.5  # Will be negative for x < 0.5
    return weight_func

# Mock function class for testing
class MockFunction:
    """Mock function class with grid and values attributes for testing."""
    def __init__(self, grid, values):
        self.grid = grid
        self.values = values
        self.dx = grid[1] - grid[0] if len(grid) > 1 else 1.0

@pytest.mark.unit
def test_initialization(constant_weight_function):
    """Test proper initialization of WeightedL2 class."""
    inner_product = WeightedL2(constant_weight_function)
    
    assert inner_product.type == "WeightedL2"
    assert inner_product.weight_function == constant_weight_function
    assert inner_product.integration_method == "trapezoidal"
    assert inner_product.integration_domain is None

@pytest.mark.unit
def test_initialization_with_params(variable_weight_function):
    """Test initialization with custom parameters."""
    domain = {"x_min": 0, "x_max": 1}
    inner_product = WeightedL2(
        variable_weight_function,
        integration_domain=domain,
        integration_method="simpson"
    )
    
    assert inner_product.weight_function == variable_weight_function
    assert inner_product.integration_domain == domain
    assert inner_product.integration_method == "simpson"

@pytest.mark.unit
def test_initialization_with_invalid_weight():
    """Test initialization with non-callable weight function raises error."""
    with pytest.raises(ValueError):
        WeightedL2(weight_function=1.0)  # Not callable

@pytest.mark.unit
def test_compute_with_numpy_arrays(grid, constant_weight_function):
    """Test compute method with numpy arrays."""
    inner_product = WeightedL2(constant_weight_function)
    
    # Create two simple functions as numpy arrays
    f = np.sin(2 * np.pi * grid)
    g = np.sin(2 * np.pi * grid)
    
    # For sine functions with period 1, the L2 inner product should be 0.5
    result = inner_product.compute(f, g)
    assert np.isclose(result, 0.5, rtol=1e-3)
    
    # Orthogonal functions should have inner product close to 0
    h = np.cos(2 * np.pi * grid)
    result = inner_product.compute(f, h)
    assert np.isclose(result, 0.0, atol=1e-3)

@pytest.mark.unit
def test_compute_with_variable_weight(grid, variable_weight_function):
    """Test compute method with variable weight function."""
    inner_product = WeightedL2(variable_weight_function)
    
    # Create two simple functions
    f = np.ones_like(grid)
    g = np.ones_like(grid)
    
    # For constant functions f=g=1 with weight w(x)=x+1, 
    # the inner product should be ∫(x+1)dx from 0 to 1 = 1.5
    result = inner_product.compute(f, g)
    assert np.isclose(result, 1.5, rtol=1e-3)

@pytest.mark.unit
def test_compute_with_mock_functions(grid, constant_weight_function):
    """Test compute method with mock function objects."""
    inner_product = WeightedL2(constant_weight_function)
    
    # Create mock function objects
    f_values = np.sin(2 * np.pi * grid)
    g_values = np.sin(2 * np.pi * grid)
    
    f = MockFunction(grid, f_values)
    g = MockFunction(grid, g_values)
    
    # Compute inner product
    result = inner_product.compute(f, g)
    assert np.isclose(result, 0.5, rtol=1e-3)

@pytest.mark.unit
def test_compute_with_complex_functions(grid, constant_weight_function):
    """Test compute method with complex-valued functions."""
    inner_product = WeightedL2(constant_weight_function)
    
    # Create complex functions
    f = np.exp(2j * np.pi * grid)
    g = np.exp(2j * np.pi * grid)
    
    # For e^(2πix) functions, the L2 inner product should be 1.0
    result = inner_product.compute(f, g)
    assert np.isclose(result, 1.0, rtol=1e-3)
    
    # Different complex frequencies should be orthogonal
    h = np.exp(4j * np.pi * grid)
    result = inner_product.compute(f, h)
    assert np.isclose(result, 0.0, atol=1e-3)

@pytest.mark.unit
def test_is_compatible_with_arrays():
    """Test is_compatible method with numpy arrays."""
    inner_product = WeightedL2(lambda x: np.ones_like(x))
    
    # Compatible arrays (same shape)
    vec1 = np.ones(10)
    vec2 = np.ones(10)
    assert inner_product.is_compatible(vec1, vec2) is True
    
    # Incompatible arrays (different shapes)
    vec3 = np.ones(20)
    assert inner_product.is_compatible(vec1, vec3) is False
    
    # Incompatible types
    assert inner_product.is_compatible(vec1, "not an array") is False

@pytest.mark.unit
def test_is_compatible_with_mock_functions(grid):
    """Test is_compatible method with mock function objects."""
    inner_product = WeightedL2(lambda x: np.ones_like(x))
    
    # Create mock function objects with same grid
    f = MockFunction(grid, np.ones_like(grid))
    g = MockFunction(grid, np.zeros_like(grid))
    assert inner_product.is_compatible(f, g) is True
    
    # Different grids
    h = MockFunction(np.linspace(0, 2, 100), np.ones(100))
    assert inner_product.is_compatible(f, h) is False
    
    # Different value shapes
    i = MockFunction(grid, np.ones((len(grid), 2)))
    assert inner_product.is_compatible(f, i) is False

@pytest.mark.unit
def test_validate_weight_function(grid, constant_weight_function, variable_weight_function, invalid_weight_function):
    """Test validate_weight_function method."""
    inner_product1 = WeightedL2(constant_weight_function)
    inner_product2 = WeightedL2(variable_weight_function)
    inner_product3 = WeightedL2(invalid_weight_function)
    
    # Constant weight (all ones) should be valid
    assert inner_product1.validate_weight_function(grid) is True
    
    # Variable weight (x+1) should be valid (all positive)
    assert inner_product2.validate_weight_function(grid) is True
    
    # Invalid weight (x-0.5) should be invalid (some negative)
    assert inner_product3.validate_weight_function(grid) is False

@pytest.mark.unit
def test_compute_with_invalid_weight(grid, invalid_weight_function):
    """Test compute method raises error with invalid weight function."""
    inner_product = WeightedL2(invalid_weight_function)
    
    f = np.ones_like(grid)
    g = np.ones_like(grid)
    
    # Should raise ValueError because weight function has negative values
    with pytest.raises(ValueError):
        inner_product.compute(f, g)

@pytest.mark.unit
def test_compute_with_incompatible_vectors(grid, constant_weight_function):
    """Test compute method raises error with incompatible vectors."""
    inner_product = WeightedL2(constant_weight_function)
    
    f = np.ones(100)
    g = np.ones(50)  # Different size
    
    # Should raise ValueError because vectors are incompatible
    with pytest.raises(ValueError):
        inner_product.compute(f, g)

@pytest.mark.unit
def test_compute_with_unsupported_integration_method(grid, constant_weight_function):
    """Test compute method raises error with unsupported integration method."""
    inner_product = WeightedL2(
        constant_weight_function,
        integration_method="unsupported_method"
    )
    
    f = MockFunction(grid, np.ones_like(grid))
    g = MockFunction(grid, np.ones_like(grid))
    
    # Should raise ValueError because integration method is unsupported
    with pytest.raises(ValueError):
        inner_product.compute(f, g)

@pytest.mark.unit
def test_compute_with_unsupported_vector_types(constant_weight_function):
    """Test compute method raises error with unsupported vector types."""
    inner_product = WeightedL2(constant_weight_function)
    
    # Using unsupported types (strings)
    f = "not a valid vector"
    g = "not a valid vector"
    
    # Should raise TypeError because vector types are unsupported
    with pytest.raises(TypeError):
        inner_product.compute(f, g)