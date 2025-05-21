import logging
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from swarmauri_standard.norms.SobolevNorm import SobolevNorm

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def sobolev_norm():
    """
    Fixture that provides a basic SobolevNorm instance.

    Returns
    -------
    SobolevNorm
        A SobolevNorm instance with default parameters.
    """
    return SobolevNorm()


@pytest.fixture
def sobolev_norm_order2():
    """
    Fixture that provides a SobolevNorm instance with order 2.

    Returns
    -------
    SobolevNorm
        A SobolevNorm instance with order 2 and custom weights.
    """
    return SobolevNorm(order=2, weights={0: 1.0, 1: 2.0, 2: 3.0})


@pytest.fixture
def test_function():
    """
    Fixture that provides a test function with derivative method.

    Returns
    -------
    Callable
        A function with its derivative method.
    """

    def f(x):
        return x**2

    def df(x):
        return 2 * x

    def ddf(x):
        return 2

    # Add derivative method to f
    f.derivative = lambda: df
    df.derivative = lambda: ddf

    return f


@pytest.fixture
def vector_data():
    """
    Fixture that provides test vector data.

    Returns
    -------
    List[float]
        A list of float values representing a vector.
    """
    return [1.0, 2.0, 3.0, 4.0, 5.0]


@pytest.mark.unit
def test_initialization_default(sobolev_norm):
    """Test initialization with default parameters."""
    assert sobolev_norm.type == "SobolevNorm"
    assert sobolev_norm.order == 1
    assert sobolev_norm.weights == {0: 1.0, 1: 1.0}


@pytest.mark.unit
def test_initialization_custom(sobolev_norm_order2):
    """Test initialization with custom parameters."""
    assert sobolev_norm_order2.type == "SobolevNorm"
    assert sobolev_norm_order2.order == 2
    assert sobolev_norm_order2.weights == {0: 1.0, 1: 2.0, 2: 3.0}


@pytest.mark.unit
def test_initialization_fills_missing_weights():
    """Test that initialization fills missing weights."""
    norm = SobolevNorm(order=3, weights={0: 1.0, 2: 2.0})
    assert norm.weights == {0: 1.0, 1: 1.0, 2: 2.0, 3: 1.0}


@pytest.mark.unit
def test_compute_with_vector(sobolev_norm, vector_data):
    """Test compute method with vector data."""
    with patch.object(sobolev_norm, "_compute_l2_norm", return_value=7.416):
        result = sobolev_norm.compute(vector_data)
        assert result == pytest.approx(7.416)  # Only 0th derivative with weight 1.0
        sobolev_norm._compute_l2_norm.assert_called_once_with(vector_data)


@pytest.mark.unit
def test_compute_with_function(sobolev_norm, test_function):
    """Test compute method with callable function."""
    with patch.object(sobolev_norm, "_compute_for_callable", return_value=1.732):
        result = sobolev_norm.compute(test_function)
        assert result == pytest.approx(1.732)
        sobolev_norm._compute_for_callable.assert_called_once_with(test_function)


@pytest.mark.unit
def test_compute_with_unsupported_type(sobolev_norm):
    """Test compute method with unsupported input type."""
    with pytest.raises(TypeError):
        sobolev_norm.compute(None)


@pytest.mark.unit
def test_compute_for_callable(sobolev_norm, test_function):
    """Test _compute_for_callable method."""
    with patch.object(sobolev_norm, "_evaluate_function_norm") as mock_eval:
        # Set up the mock to return different values for function and derivative
        mock_eval.side_effect = [2.0, 1.0]

        result = sobolev_norm._compute_for_callable(test_function)

        # Should be sqrt(2.0^2 + 1.0^2) = sqrt(5)
        assert result == pytest.approx(np.sqrt(5))
        assert mock_eval.call_count == 2


@pytest.mark.unit
def test_compute_for_callable_weighted(sobolev_norm_order2, test_function):
    """Test _compute_for_callable method with custom weights."""
    with patch.object(sobolev_norm_order2, "_evaluate_function_norm") as mock_eval:
        # Set up the mock to return different values for function and derivatives
        mock_eval.side_effect = [2.0, 1.0, 0.5]

        result = sobolev_norm_order2._compute_for_callable(test_function)

        # Should be sqrt(1.0*2.0^2 + 2.0*1.0^2 + 3.0*0.5^2) = sqrt(4 + 2 + 0.75) = sqrt(6.75)
        assert result == pytest.approx(np.sqrt(6.75))
        assert mock_eval.call_count == 3


@pytest.mark.unit
def test_compute_for_callable_no_derivative(sobolev_norm):
    """Test _compute_for_callable method with function that has no derivative method."""

    def f(x):
        return x**2

    with pytest.raises(ValueError):
        sobolev_norm._compute_for_callable(f)


@pytest.mark.unit
def test_evaluate_function_norm():
    """Test _evaluate_function_norm method."""
    norm = SobolevNorm()

    # Test with a simple function
    def f(x):
        return x

    # The L2 norm of f(x) = x on [0,1] is 1/sqrt(3)
    result = norm._evaluate_function_norm(f)
    assert result == pytest.approx(1 / np.sqrt(3), abs=0.01)


@pytest.mark.unit
def test_compute_l2_norm_with_norm_method():
    """Test _compute_l2_norm with object that has norm method."""
    norm = SobolevNorm()

    # Create a mock object with a norm method
    mock_obj = MagicMock()
    mock_obj.norm.return_value = 5.0

    result = norm._compute_l2_norm(mock_obj)
    assert result == 5.0
    mock_obj.norm.assert_called_once()


@pytest.mark.unit
def test_compute_l2_norm_with_sequence():
    """Test _compute_l2_norm with sequence."""
    norm = SobolevNorm()

    # Test with a simple sequence
    seq = [3.0, 4.0]

    # The L2 norm should be 5.0
    result = norm._compute_l2_norm(seq)
    assert result == pytest.approx(5.0)


@pytest.mark.unit
def test_compute_l2_norm_unsupported():
    """Test _compute_l2_norm with unsupported type."""
    norm = SobolevNorm()

    with pytest.raises(ValueError):
        norm._compute_l2_norm("string")


@pytest.mark.unit
def test_check_non_negativity(sobolev_norm):
    """Test check_non_negativity method."""
    with patch.object(sobolev_norm, "compute", return_value=5.0):
        assert sobolev_norm.check_non_negativity([1, 2, 3]) is True

    with patch.object(sobolev_norm, "compute", return_value=-1.0):
        assert sobolev_norm.check_non_negativity([1, 2, 3]) is False

    with patch.object(sobolev_norm, "compute", side_effect=ValueError("Test error")):
        assert sobolev_norm.check_non_negativity([1, 2, 3]) is False


@pytest.mark.unit
def test_check_definiteness(sobolev_norm):
    """Test check_definiteness method."""
    # Test with zero input
    with patch.object(sobolev_norm, "_is_zero", return_value=True):
        with patch.object(sobolev_norm, "compute", return_value=0.0):
            assert sobolev_norm.check_definiteness([0, 0, 0]) is True

    # Test with zero input but non-zero norm (should fail)
    with patch.object(sobolev_norm, "_is_zero", return_value=True):
        with patch.object(sobolev_norm, "compute", return_value=1.0):
            assert sobolev_norm.check_definiteness([0, 0, 0]) is False

    # Test with non-zero input and positive norm
    with patch.object(sobolev_norm, "_is_zero", return_value=False):
        with patch.object(sobolev_norm, "compute", return_value=5.0):
            assert sobolev_norm.check_definiteness([1, 2, 3]) is True

    # Test with non-zero input but zero norm (should fail)
    with patch.object(sobolev_norm, "_is_zero", return_value=False):
        with patch.object(sobolev_norm, "compute", return_value=0.0):
            assert sobolev_norm.check_definiteness([1, 2, 3]) is False

    # Test with error
    with patch.object(sobolev_norm, "_is_zero", side_effect=ValueError("Test error")):
        assert sobolev_norm.check_definiteness([1, 2, 3]) is False


@pytest.mark.unit
def test_check_triangle_inequality(sobolev_norm):
    """Test check_triangle_inequality method."""
    # Create test vectors
    x = [1, 2, 3]
    y = [4, 5, 6]

    # Mock the compute method to return controlled values
    with patch.object(sobolev_norm, "compute") as mock_compute:
        # Set up the mock to return different values for different inputs
        def compute_side_effect(input_val):
            if input_val == x:
                return 3.0
            elif input_val == y:
                return 4.0
            else:
                return 7.0  # For x + y

        mock_compute.side_effect = compute_side_effect

        # The triangle inequality holds: 7.0 <= 3.0 + 4.0
        assert sobolev_norm.check_triangle_inequality(x, y) is True

    # Test with the triangle inequality not holding
    with patch.object(sobolev_norm, "compute") as mock_compute:

        def compute_side_effect(input_val):
            if input_val == x:
                return 3.0
            elif input_val == y:
                return 4.0
            else:
                return 8.0  # For x + y (exceeds 3.0 + 4.0)

        mock_compute.side_effect = compute_side_effect

        # The triangle inequality doesn't hold: 8.0 > 3.0 + 4.0
        assert sobolev_norm.check_triangle_inequality(x, y) is False

    # Test with error
    with patch.object(sobolev_norm, "compute", side_effect=ValueError("Test error")):
        assert sobolev_norm.check_triangle_inequality(x, y) is False


@pytest.mark.unit
def test_check_triangle_inequality_different_types(sobolev_norm):
    """Test check_triangle_inequality with different input types."""
    x = [1, 2, 3]
    y = "string"

    with pytest.raises(TypeError):
        sobolev_norm.check_triangle_inequality(x, y)


@pytest.mark.unit
def test_check_absolute_homogeneity(sobolev_norm):
    """Test check_absolute_homogeneity method."""
    # Create test vector
    x = [1, 2, 3]
    scalar = 2.0

    # Mock the compute method to return controlled values
    with patch.object(sobolev_norm, "compute") as mock_compute:
        # Set up the mock to return different values for different inputs
        def compute_side_effect(input_val):
            if input_val == x:
                return 3.0
            else:
                return 6.0  # For 2.0 * x

        mock_compute.side_effect = compute_side_effect

        # The absolute homogeneity holds: 6.0 == 2.0 * 3.0
        assert sobolev_norm.check_absolute_homogeneity(x, scalar) is True

    # Test with absolute homogeneity not holding
    with patch.object(sobolev_norm, "compute") as mock_compute:

        def compute_side_effect(input_val):
            if input_val == x:
                return 3.0
            else:
                return 7.0  # For 2.0 * x (not equal to 2.0 * 3.0)

        mock_compute.side_effect = compute_side_effect

        # The absolute homogeneity doesn't hold: 7.0 != 2.0 * 3.0
        assert sobolev_norm.check_absolute_homogeneity(x, scalar) is False

    # Test with error
    with patch.object(sobolev_norm, "compute", side_effect=ValueError("Test error")):
        assert sobolev_norm.check_absolute_homogeneity(x, scalar) is False


@pytest.mark.unit
def test_is_zero():
    """Test _is_zero method."""
    norm = SobolevNorm()

    # Test with callable
    def zero_func(x):
        return 0

    assert norm._is_zero(zero_func) is True

    def non_zero_func(x):
        return x

    assert norm._is_zero(non_zero_func) is False

    # Test with object that has is_zero method
    mock_obj = MagicMock()
    mock_obj.is_zero.return_value = True
    assert norm._is_zero(mock_obj) is True

    # Test with sequence
    assert norm._is_zero([0, 0, 0]) is True
    assert norm._is_zero([0, 0.1, 0]) is False

    # Test with object that has __abs__ method
    mock_obj = MagicMock()
    mock_obj.__abs__.return_value = 0
    assert norm._is_zero(mock_obj) is True


@pytest.mark.unit
def test_serialization(sobolev_norm, sobolev_norm_order2):
    """Test serialization and deserialization."""
    # Test serialization and deserialization of default norm
    json_str = sobolev_norm.model_dump_json()
    deserialized = SobolevNorm.model_validate_json(json_str)

    assert deserialized.type == sobolev_norm.type
    assert deserialized.order == sobolev_norm.order
    assert deserialized.weights == sobolev_norm.weights

    # Test serialization and deserialization of custom norm
    json_str = sobolev_norm_order2.model_dump_json()
    deserialized = SobolevNorm.model_validate_json(json_str)

    assert deserialized.type == sobolev_norm_order2.type
    assert deserialized.order == sobolev_norm_order2.order
    assert deserialized.weights == sobolev_norm_order2.weights


@pytest.mark.unit
@pytest.mark.parametrize(
    "order,weights,expected_weights",
    [
        (1, {0: 1.0, 1: 2.0}, {0: 1.0, 1: 2.0}),
        (2, {0: 1.0}, {0: 1.0, 1: 1.0, 2: 1.0}),
        (3, {1: 2.0, 3: 4.0}, {0: 1.0, 1: 2.0, 2: 1.0, 3: 4.0}),
    ],
)
def test_initialization_with_different_parameters(order, weights, expected_weights):
    """Test initialization with different parameters."""
    norm = SobolevNorm(order=order, weights=weights)
    assert norm.order == order
    assert norm.weights == expected_weights


@pytest.mark.unit
def test_integration_with_real_function():
    """Test integration with a real function and its derivatives."""
    norm = SobolevNorm(order=2, weights={0: 1.0, 1: 2.0, 2: 3.0})

    # Define a test function and its derivatives
    def f(x):
        return x**2

    def df(x):
        return 2 * x

    def ddf(x):
        return 2

    # Add derivative methods
    f.derivative = lambda: df
    df.derivative = lambda: ddf

    # Using the implementation
    result = norm.compute(f)
    expected = np.sqrt(1 / 5 + 2 * 4 / 3 + 3 * 4)

    # Check with a reasonable tolerance
    assert result == pytest.approx(expected, abs=0.1)
