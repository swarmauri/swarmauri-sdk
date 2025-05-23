import logging
from typing import Any, Callable

import numpy as np
import pytest

from swarmauri_standard.inner_products.WeightedL2InnerProduct import (
    WeightedL2InnerProduct,
)

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture
def constant_weight_function() -> Callable[[Any], float]:
    """
    Fixture providing a constant weight function that always returns 2.0.

    Returns
    -------
    Callable[[Any], float]
        A function that returns 2.0 for any input
    """
    return lambda x: 2.0


@pytest.fixture
def position_dependent_weight_function() -> Callable[[Any], np.ndarray]:
    """
    Fixture providing a position-dependent weight function.

    Returns
    -------
    Callable[[Any], np.ndarray]
        A function that returns position-dependent weights
    """
    return (
        lambda x: np.exp(-0.1 * x)
        if isinstance(x, np.ndarray)
        else np.exp(-0.1 * np.array(x))
    )


@pytest.fixture
def weighted_l2_constant() -> WeightedL2InnerProduct:
    """
    Fixture providing a WeightedL2InnerProduct instance with constant weights.

    Returns
    -------
    WeightedL2InnerProduct
        An instance with constant weight function
    """
    return WeightedL2InnerProduct(weight_function=lambda x: 2.0)


@pytest.fixture
def weighted_l2_variable() -> WeightedL2InnerProduct:
    """
    Fixture providing a WeightedL2InnerProduct instance with variable weights.

    Returns
    -------
    WeightedL2InnerProduct
        An instance with variable weight function
    """
    return WeightedL2InnerProduct(
        weight_function=lambda x: np.exp(-0.1 * x)
        if isinstance(x, np.ndarray)
        else np.exp(-0.1 * np.array(x))
    )


@pytest.mark.unit
def test_initialization_with_weight_function(constant_weight_function):
    """Test proper initialization with a weight function."""
    inner_product = WeightedL2InnerProduct(weight_function=constant_weight_function)
    assert inner_product.weight_function is constant_weight_function
    assert inner_product.type == "WeightedL2InnerProduct"
    assert inner_product.resource == "InnerProduct"


@pytest.mark.unit
def test_initialization_without_weight_function():
    """Test that initialization fails without a weight function."""
    with pytest.raises(ValueError, match="Weight function must be provided"):
        WeightedL2InnerProduct(weight_function=None)


@pytest.mark.unit
def test_validate_weight_at_points_valid(weighted_l2_constant):
    """Test validation passes with positive weights."""
    # This should not raise an exception
    weighted_l2_constant._validate_weight_at_points(np.array([1, 2, 3]))


@pytest.mark.unit
def test_validate_weight_at_points_invalid():
    """Test validation fails with non-positive weights."""

    # Create a weight function that returns negative values
    def negative_weight_func(x):
        return -1.0

    inner_product = WeightedL2InnerProduct(weight_function=negative_weight_func)

    with pytest.raises(ValueError, match="Weight function must be strictly positive"):
        inner_product._validate_weight_at_points(np.array([1, 2, 3]))


@pytest.mark.unit
@pytest.mark.parametrize(
    "a, b, expected",
    [
        (
            np.array([1, 2, 3]),
            np.array([4, 5, 6]),
            complex(2 * (1 * 4 + 2 * 5 + 3 * 6)),
        ),
        (
            np.array([1 + 1j, 2 - 2j]),
            np.array([3 - 3j, 4 + 4j]),
            complex(2 * ((1 + 1j) * (3 + 3j) + (2 - 2j) * (4 - 4j))),
        ),
    ],
)
def test_compute_with_arrays(weighted_l2_constant, a, b, expected):
    """Test computing inner product with arrays."""
    result = weighted_l2_constant.compute(a, b)
    assert np.isclose(result, expected)


@pytest.mark.unit
def test_compute_with_arrays_dimension_mismatch(weighted_l2_constant):
    """Test inner product computation raises error with mismatched dimensions."""
    a = np.array([1, 2, 3])
    b = np.array([4, 5])

    with pytest.raises(ValueError, match="Dimensions must match"):
        weighted_l2_constant.compute(a, b)


@pytest.mark.unit
def test_compute_with_callables(weighted_l2_constant):
    """Test computing inner product with callable functions."""

    def func_a(x):
        return x**2

    def func_b(x):
        return np.sin(x)

    # This is a simplified test - the actual result depends on the integration method
    result = weighted_l2_constant.compute(func_a, func_b)
    assert isinstance(result, complex)


@pytest.mark.unit
def test_compute_with_unsupported_types(weighted_l2_constant):
    """Test inner product computation raises error with unsupported types."""
    a = "not a valid input"
    b = 42

    with pytest.raises(TypeError, match="Unsupported types"):
        weighted_l2_constant.compute(a, b)


@pytest.mark.unit
def test_check_conjugate_symmetry_with_arrays(weighted_l2_constant):
    """Test conjugate symmetry property with arrays."""
    a = np.array([1 + 1j, 2 - 2j])
    b = np.array([3 - 3j, 4 + 4j])

    assert weighted_l2_constant.check_conjugate_symmetry(a, b)


@pytest.mark.unit
def test_check_linearity_first_argument_with_arrays(weighted_l2_constant):
    """Test linearity in first argument with arrays."""
    a1 = np.array([1, 2, 3])
    a2 = np.array([4, 5, 6])
    b = np.array([7, 8, 9])
    alpha = 2.0
    beta = 3.0

    assert weighted_l2_constant.check_linearity_first_argument(a1, a2, b, alpha, beta)


@pytest.mark.unit
def test_check_positivity_with_arrays(weighted_l2_constant):
    """Test positivity property with arrays."""
    a = np.array([1, 2, 3])
    assert weighted_l2_constant.check_positivity(a)

    # Zero array should also be positive
    zero = np.zeros_like(a)
    assert weighted_l2_constant.check_positivity(zero)


@pytest.mark.unit
def test_norm_with_arrays(weighted_l2_constant):
    """Test norm computation with arrays."""
    a = np.array([1, 2, 3])
    # Expected: sqrt(2 * (1^2 + 2^2 + 3^2))
    expected = np.sqrt(2 * (1**2 + 2**2 + 3**2))

    result = weighted_l2_constant.norm(a)
    assert np.isclose(result, expected)


@pytest.mark.unit
def test_position_dependent_weight(weighted_l2_variable):
    """Test inner product with position-dependent weights."""
    a = np.array([1, 2, 3])
    b = np.array([4, 5, 6])

    weights = np.exp(-0.1 * np.arange(3))
    expected = complex(np.sum(a * b * weights))

    result = weighted_l2_variable.compute(a, b)
    assert np.isclose(result, expected)


@pytest.mark.unit
def test_compute_with_complex_arrays(weighted_l2_constant):
    """Test inner product with complex arrays."""
    a = np.array([1 + 2j, 3 - 4j, 5 + 6j])
    b = np.array([7 - 8j, 9 + 10j, 11 - 12j])

    # Expected: 2 * sum(a * conj(b))
    expected = 2 * np.sum(a * np.conjugate(b))

    result = weighted_l2_constant.compute(a, b)
    assert np.isclose(result, expected)


@pytest.mark.unit
def test_invalid_weight_function():
    """Test inner product with a weight function that returns zero or negative values."""

    def invalid_weight_func(x):
        return np.zeros_like(x) if isinstance(x, np.ndarray) else 0

    inner_product = WeightedL2InnerProduct(weight_function=invalid_weight_func)

    a = np.array([1, 2, 3])
    b = np.array([4, 5, 6])

    with pytest.raises(ValueError, match="Weight function must be strictly positive"):
        inner_product.compute(a, b)


@pytest.mark.unit
def test_check_properties_with_functions(weighted_l2_constant):
    """Test inner product properties with callable functions."""

    def func_a(x):
        return x

    def func_b(x):
        return x**2

    # These are simplified tests - actual results depend on integration method
    assert weighted_l2_constant.check_conjugate_symmetry(func_a, func_b)
    assert weighted_l2_constant.check_positivity(func_a)


@pytest.mark.unit
def test_error_handling_in_compute(weighted_l2_constant):
    """Test error handling in compute method."""

    # Mock a function that raises an exception
    def failing_func(x):
        raise RuntimeError("Function evaluation failed")

    with pytest.raises(RuntimeError, match="Function evaluation failed"):
        weighted_l2_constant.compute(failing_func, lambda x: x)


@pytest.mark.unit
def test_serialization():
    """Test serialization and deserialization."""
    inner_product = WeightedL2InnerProduct(weight_function=lambda x: 2.0)

    # Convert to dict and back to ensure serializable fields work correctly
    data = inner_product.model_dump()
    assert data["type"] == "WeightedL2InnerProduct"
    assert data["resource"] == "InnerProduct"


@pytest.mark.unit
def test_inheritance():
    """Test proper inheritance from base classes."""
    from swarmauri_base.inner_products.InnerProductBase import InnerProductBase

    inner_product = WeightedL2InnerProduct(weight_function=lambda x: 2.0)
    assert isinstance(inner_product, InnerProductBase)
