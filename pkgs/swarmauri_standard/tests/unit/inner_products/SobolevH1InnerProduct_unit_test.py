import logging
from typing import Tuple
from unittest.mock import MagicMock

import numpy as np
import pytest

from swarmauri_standard.inner_products.SobolevH1InnerProduct import (
    SobolevH1InnerProduct,
)
from swarmauri_standard.vectors.Vector import Vector

# Configure logging
logger = logging.getLogger(__name__)


# Test fixtures
@pytest.fixture
def sobolev_h1_inner_product():
    """Fixture that returns a default SobolevH1InnerProduct instance."""
    return SobolevH1InnerProduct()


@pytest.fixture
def custom_weighted_inner_product():
    """Fixture that returns a SobolevH1InnerProduct with custom weights."""
    return SobolevH1InnerProduct(alpha=2.0, beta=3.0)


@pytest.fixture
def vector_pair():
    """Fixture that returns a pair of vector objects with values and derivatives."""
    vector1 = Vector(value=[1.0, 2.0, 3.0, 4.0], derivatives=[0.5, 1.0, 1.5, 2.0])

    vector2 = Vector(value=[2.0, 3.0, 4.0, 5.0], derivatives=[1.0, 1.5, 2.0, 2.5])

    return vector1, vector2


@pytest.fixture
def function_pair():
    """Fixture that returns a pair of functions with values and derivatives."""

    def f(x: float) -> Tuple[float, float]:
        """First test function returning value and derivative."""
        return x**2, 2 * x

    def g(x: float) -> Tuple[float, float]:
        """Second test function returning value and derivative."""
        return x**3, 3 * x**2

    return f, g


@pytest.mark.unit
def test_initialization():
    """Test the initialization of SobolevH1InnerProduct with default and custom parameters."""
    # Default initialization
    inner_product = SobolevH1InnerProduct()
    assert inner_product.alpha == 1.0
    assert inner_product.beta == 1.0

    # Custom initialization
    inner_product = SobolevH1InnerProduct(alpha=2.5, beta=3.5)
    assert inner_product.alpha == 2.5
    assert inner_product.beta == 3.5


@pytest.mark.unit
def test_type_attribute():
    """Test that the type attribute is correctly set."""
    inner_product = SobolevH1InnerProduct()
    assert inner_product.type == "SobolevH1InnerProduct"


@pytest.mark.unit
def test_compute_for_arrays(sobolev_h1_inner_product):
    """Test computing the inner product for numpy arrays."""
    # Simple arrays where we can manually calculate the expected result
    a = np.array([1.0, 2.0, 3.0, 4.0])
    b = np.array([2.0, 3.0, 4.0, 5.0])

    # L2 part: (1*2 + 2*3 + 3*4 + 4*5)/4 = (2 + 6 + 12 + 20)/4 = 40/4 = 10
    # Derivatives using central differences:
    # a_derivative = [1, 1, 1, 1] (approximately)
    # b_derivative = [1, 1, 1, 1] (approximately)
    # Derivative part: (1*1 + 1*1 + 1*1 + 1*1)/4 = 4/4 = 1
    # Result = 1.0 * 10 + 1.0 * 1 = 11.0

    result = sobolev_h1_inner_product._compute_for_arrays(a, b)
    assert pytest.approx(result, abs=1e-5) == 11.0


@pytest.mark.unit
def test_compute_for_vectors(sobolev_h1_inner_product, vector_pair):
    """Test computing the inner product for vector objects."""
    vector1, vector2 = vector_pair

    result = sobolev_h1_inner_product._compute_for_vectors(vector1, vector2)
    assert pytest.approx(result, abs=1e-5) == 11.0


@pytest.mark.unit
def test_compute_for_functions(sobolev_h1_inner_product, function_pair):
    """Test computing the inner product for functions."""
    f, g = function_pair

    # We'll test with a specific domain and integration points to make verification easier
    domain = (0, 1)
    num_points = 5  # Using a small number for easy manual verification

    result = sobolev_h1_inner_product._compute_for_functions(
        f, g, domain=domain, num_points=num_points
    )
    # Using a larger tolerance due to the coarse integration
    assert pytest.approx(result, abs=0.1) == 2.66


@pytest.mark.unit
def test_compute_with_different_weights(custom_weighted_inner_product, vector_pair):
    """Test that the inner product correctly applies custom weights."""
    vector1, vector2 = vector_pair

    result = custom_weighted_inner_product._compute_for_vectors(vector1, vector2)
    assert pytest.approx(result, abs=1e-5) == 23.0


@pytest.mark.unit
def test_compute_with_incompatible_arrays(sobolev_h1_inner_product):
    """Test that computing with incompatible arrays raises ValueError."""
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([2.0, 3.0, 4.0, 5.0])

    with pytest.raises(ValueError):
        sobolev_h1_inner_product._compute_for_arrays(a, b)


@pytest.mark.unit
def test_compute_with_unsupported_types(sobolev_h1_inner_product):
    """Test that computing with unsupported types raises TypeError."""
    a = "not a valid input"
    b = 42

    with pytest.raises(TypeError):
        sobolev_h1_inner_product.compute(a, b)


@pytest.mark.unit
def test_check_conjugate_symmetry(sobolev_h1_inner_product, vector_pair):
    """Test the conjugate symmetry property check."""
    vector1, vector2 = vector_pair

    # For real-valued functions, conjugate symmetry means <a,b> = <b,a>
    assert sobolev_h1_inner_product.check_conjugate_symmetry(vector1, vector2)


@pytest.mark.unit
def test_check_linearity_first_argument(sobolev_h1_inner_product):
    """Test the linearity in first argument property check."""
    # Using arrays for simplicity
    a1 = np.array([1.0, 2.0, 3.0, 4.0])
    a2 = np.array([2.0, 3.0, 4.0, 5.0])
    b = np.array([3.0, 4.0, 5.0, 6.0])

    alpha = 2.0
    beta = 3.0

    assert sobolev_h1_inner_product.check_linearity_first_argument(
        a1, a2, b, alpha, beta
    )


@pytest.mark.unit
def test_check_positivity(sobolev_h1_inner_product):
    """Test the positivity property check."""
    # Non-zero array should have positive inner product with itself
    a = np.array([1.0, 2.0, 3.0, 4.0])
    assert sobolev_h1_inner_product.check_positivity(a)

    # Zero array should have zero inner product with itself
    zero_array = np.zeros(4)
    assert sobolev_h1_inner_product.compute(zero_array, zero_array) == 0
    assert sobolev_h1_inner_product.check_positivity(zero_array)


@pytest.mark.unit
def test_string_representation():
    """Test the string representation of the inner product."""
    inner_product = SobolevH1InnerProduct(alpha=2.5, beta=3.5)
    assert str(inner_product) == "SobolevH1InnerProduct(alpha=2.5, beta=3.5)"


@pytest.mark.unit
@pytest.mark.parametrize(
    "alpha,beta",
    [
        (1.0, 1.0),
        (2.0, 3.0),
        (0.5, 1.5),
        (0.0, 1.0),  # L2 part has no contribution
        (1.0, 0.0),  # Derivative part has no contribution
    ],
)
def test_parameterized_weights(alpha, beta, vector_pair):
    """Test the inner product with various weight combinations."""
    vector1, vector2 = vector_pair
    inner_product = SobolevH1InnerProduct(alpha=alpha, beta=beta)

    expected = alpha * 10.0 + beta * 1.0
    result = inner_product._compute_for_vectors(vector1, vector2)
    assert pytest.approx(result, abs=1e-5) == expected


@pytest.mark.unit
def test_compute_dispatch(sobolev_h1_inner_product, vector_pair, function_pair):
    """Test that compute correctly dispatches to the appropriate implementation."""
    vector1, vector2 = vector_pair
    f, g = function_pair

    # Mock the implementation methods to check they're called
    sobolev_h1_inner_product._compute_for_vectors = MagicMock(return_value=42.0)
    sobolev_h1_inner_product._compute_for_arrays = MagicMock(return_value=43.0)
    sobolev_h1_inner_product._compute_for_functions = MagicMock(return_value=44.0)

    # Test dispatch for vectors
    result = sobolev_h1_inner_product.compute(vector1, vector2)
    sobolev_h1_inner_product._compute_for_vectors.assert_called_once_with(
        vector1, vector2
    )
    assert result == 42.0

    # Test dispatch for arrays
    a = np.array([1.0, 2.0])
    b = np.array([3.0, 4.0])
    result = sobolev_h1_inner_product.compute(a, b)
    sobolev_h1_inner_product._compute_for_arrays.assert_called_once_with(a, b)
    assert result == 43.0

    # Test dispatch for functions
    # Note: In the real implementation, we would need to adapt this test since
    # the compute method would need to determine if the callables return derivatives
    # For the test, we assume it correctly identifies our functions
    result = sobolev_h1_inner_product.compute(f, g)
    sobolev_h1_inner_product._compute_for_functions.assert_called_once_with(f, g)
    assert result == 44.0
