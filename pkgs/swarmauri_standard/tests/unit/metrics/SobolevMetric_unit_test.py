import pytest
import numpy as np
import logging
from unittest.mock import MagicMock, patch
from swarmauri_standard.metrics.SobolevMetric import SobolevMetric

# Configure logger for testing
logger = logging.getLogger(__name__)

@pytest.fixture
def sobolev_metric():
    """
    Fixture that provides a default SobolevMetric instance.
    
    Returns
    -------
    SobolevMetric
        A default SobolevMetric instance with weights {0: 1.0, 1: 0.5} and norm_type=2
    """
    return SobolevMetric()

@pytest.fixture
def custom_sobolev_metric():
    """
    Fixture that provides a custom SobolevMetric instance.
    
    Returns
    -------
    SobolevMetric
        A custom SobolevMetric instance with weights {0: 1.0, 1: 1.0, 2: 0.25} and norm_type=1
    """
    return SobolevMetric(weights={0: 1.0, 1: 1.0, 2: 0.25}, norm_type=1)

@pytest.mark.unit
def test_sobolev_metric_initialization():
    """Test that SobolevMetric initializes with correct default values."""
    metric = SobolevMetric()
    assert metric.type == "SobolevMetric"
    assert metric.weights == {0: 1.0, 1: 0.5}
    assert metric.norm_type == 2

@pytest.mark.unit
def test_sobolev_metric_custom_initialization():
    """Test that SobolevMetric initializes with custom values."""
    weights = {0: 2.0, 1: 1.0, 2: 0.5}
    norm_type = 1
    metric = SobolevMetric(weights=weights, norm_type=norm_type)
    assert metric.weights == weights
    assert metric.norm_type == norm_type

@pytest.mark.unit
def test_validate_weights_valid():
    """Test that valid weights are accepted."""
    # Valid weights should include at least the zero-order term
    valid_weights = {0: 1.0, 1: 0.5, 2: 0.25}
    metric = SobolevMetric(weights=valid_weights)
    assert metric.weights == valid_weights

@pytest.mark.unit
def test_validate_weights_missing_zero_order():
    """Test that weights without zero-order term raise ValueError."""
    # Weights must include the zero-order term
    invalid_weights = {1: 0.5, 2: 0.25}
    with pytest.raises(ValueError, match="Weights must include at least the zero-order term"):
        SobolevMetric(weights=invalid_weights)

@pytest.mark.unit
def test_validate_weights_negative():
    """Test that negative weights raise ValueError."""
    # Weights must be non-negative
    invalid_weights = {0: 1.0, 1: -0.5}
    with pytest.raises(ValueError, match="Weight for order 1 must be non-negative"):
        SobolevMetric(weights=invalid_weights)

@pytest.mark.unit
def test_norm_type_validation():
    """Test that norm_type is validated to be >= 1."""
    with pytest.raises(ValueError):
        SobolevMetric(norm_type=0)

@pytest.mark.unit
def test_distance_identical_arrays(sobolev_metric):
    """Test distance calculation for identical arrays."""
    x = np.array([1, 2, 3, 4, 5])
    y = np.array([1, 2, 3, 4, 5])
    distance = sobolev_metric.distance(x, y)
    assert distance == 0.0

@pytest.mark.unit
def test_distance_different_arrays(sobolev_metric):
    """Test distance calculation for different arrays."""
    x = np.array([1, 2, 3, 4, 5])
    y = np.array([2, 3, 4, 5, 6])
    distance = sobolev_metric.distance(x, y)
    # Expected: sqrt((1^2 + 1^2 + 1^2 + 1^2 + 1^2) + 0.5*0)
    # The derivative difference is 0 because the constant difference has no effect on derivative
    assert distance == pytest.approx(np.sqrt(5))

@pytest.mark.unit
def test_distance_with_derivatives(custom_sobolev_metric):
    """Test distance calculation including derivatives with custom weights."""
    # Arrays with different slopes
    x = np.array([1, 2, 3, 4, 5])
    y = np.array([1, 3, 5, 7, 9])  # y has a steeper slope than x
    
    distance = custom_sobolev_metric.distance(x, y)
    
    # Expected:
    # Function difference: |1-1| + |2-3| + |3-5| + |4-7| + |5-9| = 0 + 1 + 2 + 3 + 4 = 10
    # First derivative difference: |1-2| + |1-2| + |1-2| + |1-2| = 4
    # Second derivative: Both are constant derivatives, so difference is 0
    expected = 10 + 1.0*4 + 0.25*0
    assert distance == pytest.approx(expected)

@pytest.mark.unit
def test_distance_with_callable():
    """Test distance calculation with callable functions."""
    metric = SobolevMetric(weights={0: 1.0}, norm_type=1)  # Only using function values
    
    def f(x): return x**2
    def g(x): return x**2 + 1
    
    with patch('numpy.linspace', return_value=np.array([0, 0.5, 1])):
        distance = metric.distance(f, g)
        # Expected: |0-1| + |0.25-1.25| + |1-2| = 1 + 1 + 1 = 3
        assert distance == pytest.approx(3.0)

@pytest.mark.unit
def test_are_identical_true(sobolev_metric):
    """Test are_identical returns True for identical functions."""
    x = np.array([1, 2, 3, 4, 5])
    y = np.array([1, 2, 3, 4, 5])
    assert sobolev_metric.are_identical(x, y) is True

@pytest.mark.unit
def test_are_identical_false(sobolev_metric):
    """Test are_identical returns False for different functions."""
    x = np.array([1, 2, 3, 4, 5])
    y = np.array([2, 3, 4, 5, 6])
    assert sobolev_metric.are_identical(x, y) is False

@pytest.mark.unit
def test_are_identical_exception_handling(sobolev_metric):
    """Test are_identical handles exceptions gracefully."""
    x = np.array([1, 2, 3])
    y = "not an array"  # This will cause an exception in distance calculation
    assert sobolev_metric.are_identical(x, y) is False

@pytest.mark.unit
def test_compute_finite_difference(sobolev_metric):
    """Test computation of finite differences."""
    # Linear function: f(x) = 2x + 1
    values = np.array([1, 3, 5, 7, 9])
    
    # First derivative should be constant (2)
    first_deriv = sobolev_metric._compute_finite_difference(values, 1)
    assert np.allclose(first_deriv, np.array([2, 2, 2, 2, 2]))
    
    # Second derivative should be zero
    second_deriv = sobolev_metric._compute_finite_difference(values, 2)
    assert np.allclose(second_deriv, np.array([0, 0, 0, 0, 0]))

@pytest.mark.unit
def test_compute_norm_l1(sobolev_metric):
    """Test computation of L1 norm."""
    sobolev_metric.norm_type = 1
    values = np.array([1, -2, 3, -4])
    assert sobolev_metric._compute_norm(values) == 10.0

@pytest.mark.unit
def test_compute_norm_l2(sobolev_metric):
    """Test computation of L2 norm."""
    values = np.array([1, -2, 3, -4])
    assert sobolev_metric._compute_norm(values) == pytest.approx(np.sqrt(30))

@pytest.mark.unit
def test_compute_norm_custom(sobolev_metric):
    """Test computation of custom norm."""
    sobolev_metric.norm_type = 3
    values = np.array([1, -2, 3, -4])
    expected = np.power(1**3 + 2**3 + 3**3 + 4**3, 1/3)
    assert sobolev_metric._compute_norm(values) == pytest.approx(expected)

@pytest.mark.unit
def test_get_derivative_callable_with_method():
    """Test getting derivative from a callable with derivative method."""
    metric = SobolevMetric()
    
    class TestFunction:
        def __call__(self, x):
            return x**2
            
        def derivative(self, order):
            if order == 1:
                return lambda x: 2*x
            elif order == 2:
                return lambda x: 2
            else:
                return lambda x: 0
    
    func = TestFunction()
    assert metric._get_derivative(func, 0) == func
    assert callable(metric._get_derivative(func, 1))
    assert callable(metric._get_derivative(func, 2))

@pytest.mark.unit
def test_get_derivative_with_attribute():
    """Test getting derivative from an object with derivative attributes."""
    metric = SobolevMetric()
    
    class TestFunction:
        def __init__(self):
            self.derivative_1 = lambda x: 2*x
            self.derivative_2 = lambda x: 2
    
    func = TestFunction()
    assert metric._get_derivative(func, 0) == func
    assert metric._get_derivative(func, 1) == func.derivative_1
    assert metric._get_derivative(func, 2) == func.derivative_2

@pytest.mark.unit
def test_get_derivative_from_dict():
    """Test getting derivative from a dictionary."""
    metric = SobolevMetric()
    
    func = {
        0: lambda x: x**2,
        1: lambda x: 2*x,
        2: lambda x: 2
    }
    
    assert metric._get_derivative(func, 0) == func[0]
    assert metric._get_derivative(func, 1) == func[1]
    assert metric._get_derivative(func, 2) == func[2]

@pytest.mark.unit
def test_get_derivative_invalid_input():
    """Test getting derivative from invalid input raises ValueError."""
    metric = SobolevMetric()
    
    with pytest.raises(ValueError, match="Cannot compute derivative of order 1 for the given input type"):
        metric._get_derivative("not a valid input", 1)

@pytest.mark.unit
def test_compute_difference_arrays():
    """Test computing difference between arrays."""
    metric = SobolevMetric()
    x = np.array([1, 2, 3])
    y =