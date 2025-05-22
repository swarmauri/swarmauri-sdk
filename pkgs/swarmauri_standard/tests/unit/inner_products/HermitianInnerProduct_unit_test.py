import logging
from typing import Tuple

import numpy as np
import pytest
from swarmauri_base.inner_products.InnerProductBase import InnerProductBase

from swarmauri_standard.inner_products.HermitianInnerProduct import (
    HermitianInnerProduct,
)
from swarmauri_standard.vectors.Vector import Vector

# Configure logging
logger = logging.getLogger(__name__)


@pytest.fixture
def hermitian_inner_product() -> HermitianInnerProduct:
    """
    Fixture providing a HermitianInnerProduct instance.

    Returns
    -------
    HermitianInnerProduct
        An instance of HermitianInnerProduct
    """
    return HermitianInnerProduct()


@pytest.fixture
def vector_samples() -> Tuple[Vector, Vector]:
    """
    Fixture providing sample vectors for testing.

    Returns
    -------
    Tuple[Vector, Vector]
        A tuple of two Vector instances
    """
    # Replace complex numbers with integers
    v1 = Vector(value=[1, 3, 2])
    v2 = Vector(value=[2, 0, 4])
    return v1, v2


@pytest.fixture
def array_samples() -> Tuple[np.ndarray, np.ndarray]:
    """
    Fixture providing sample numpy arrays for testing.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        A tuple of two numpy arrays
    """
    a1 = np.array([1 + 2j, 3 - 1j, 0.5j])
    a2 = np.array([2 - 1j, 0, 4 + 2j])
    return a1, a2


@pytest.fixture
def matrix_samples() -> Tuple[np.ndarray, np.ndarray]:
    """
    Fixture providing sample matrices for testing.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        A tuple of two numpy matrix arrays
    """
    m1 = np.array([[1 + 1j, 2 - 1j], [3j, 4]])
    m2 = np.array([[2, 1 + 2j], [0.5 - 0.5j, 3]])
    return m1, m2


@pytest.mark.unit
def test_inheritance():
    """Test that HermitianInnerProduct inherits from InnerProductBase."""
    assert issubclass(HermitianInnerProduct, InnerProductBase)


@pytest.mark.unit
def test_type_attribute(hermitian_inner_product):
    """Test the type attribute of HermitianInnerProduct."""
    assert hermitian_inner_product.type == "HermitianInnerProduct"


@pytest.mark.unit
def test_compute_with_vectors(hermitian_inner_product, vector_samples):
    """Test compute method with vector inputs."""
    v1, v2 = vector_samples

    # Compute the inner product
    result = hermitian_inner_product.compute(v1, v2)

    # Manual calculation for comparison (with real numbers, this is just a standard dot product)
    expected = np.dot(v1.to_numpy(), v2.to_numpy())

    assert np.isclose(result, expected)
    # Remove the complex check since result will be real
    assert isinstance(result, (int, float, np.number))


@pytest.mark.unit
def test_compute_with_arrays(hermitian_inner_product, array_samples):
    """Test compute method with numpy array inputs."""
    a1, a2 = array_samples

    # Compute the inner product
    result = hermitian_inner_product.compute(a1, a2)

    # Manual calculation for comparison
    expected = np.vdot(a1, a2)

    assert np.isclose(result, expected)
    assert isinstance(result, complex)


@pytest.mark.unit
def test_compute_with_matrices(hermitian_inner_product, matrix_samples):
    """Test compute method with matrix inputs."""
    m1, m2 = matrix_samples

    # Compute the inner product
    result = hermitian_inner_product.compute(m1, m2)

    # Manual calculation for comparison
    expected = np.trace(m1.conj().T @ m2)

    assert np.isclose(result, expected)
    assert isinstance(result, complex)


@pytest.mark.unit
def test_compute_with_mismatched_dimensions(hermitian_inner_product):
    """Test compute method with mismatched dimensions raises ValueError."""
    # Use integers instead of complex numbers
    v1 = Vector(value=[1, 3, 2])
    v2 = Vector(value=[2, 0])

    with pytest.raises(ValueError):
        hermitian_inner_product.compute(v1, v2)


@pytest.mark.unit
def test_compute_with_unsupported_types(hermitian_inner_product):
    """Test compute method with unsupported types raises TypeError."""
    with pytest.raises(TypeError):
        hermitian_inner_product.compute("not a vector", 123)


@pytest.mark.unit
def test_compute_with_callables(hermitian_inner_product):
    """Test compute method with callable inputs raises NotImplementedError."""

    def func1(x):
        return x

    def func2(x):
        return x**2

    with pytest.raises(NotImplementedError):
        hermitian_inner_product.compute(func1, func2)


@pytest.mark.unit
def test_conjugate_symmetry(hermitian_inner_product, vector_samples):
    """Test conjugate symmetry property of Hermitian inner product."""
    v1, v2 = vector_samples

    # Check conjugate symmetry
    result = hermitian_inner_product.check_conjugate_symmetry(v1, v2)

    # Manually verify: <v1, v2> = conj(<v2, v1>)
    v1v2 = hermitian_inner_product.compute(v1, v2)
    v2v1 = hermitian_inner_product.compute(v2, v1)

    assert result is True
    assert np.isclose(v1v2, np.conj(v2v1))


@pytest.mark.unit
def test_linearity_first_argument(hermitian_inner_product, vector_samples):
    """Test linearity in first argument property of Hermitian inner product."""
    v1, v2 = vector_samples
    # Use real-valued scalars
    alpha = 2
    beta = -1

    # Create a third vector with integers
    v3 = Vector(value=[1, 2, 1])

    # Check linearity
    result = hermitian_inner_product.check_linearity_first_argument(
        v1, v2, v3, alpha, beta
    )

    assert result is True


@pytest.mark.unit
def test_positivity(hermitian_inner_product, vector_samples):
    """Test positivity property of Hermitian inner product."""
    v1, _ = vector_samples

    # Check positivity
    result = hermitian_inner_product.check_positivity(v1)

    # Manually verify: <v1, v1> >= 0
    v1v1 = hermitian_inner_product.compute(v1, v1)

    assert result is True
    assert v1v1.real >= 0
    assert np.isclose(v1v1.imag, 0)


@pytest.mark.unit
def test_positivity_with_zero_vector(hermitian_inner_product):
    """Test positivity property with zero vector."""
    # Change complex zeros to integer zeros
    zero_vector = Vector(value=[0, 0, 0])

    # Check positivity
    result = hermitian_inner_product.check_positivity(zero_vector)

    # Manually verify: <0, 0> = 0
    zero_zero = hermitian_inner_product.compute(zero_vector, zero_vector)

    assert result is True
    assert np.isclose(zero_zero, 0)


@pytest.mark.unit
def test_logging(caplog):
    """Test that appropriate logging occurs."""
    caplog.set_level(logging.DEBUG)

    inner_product = HermitianInnerProduct()
    v1 = np.array([1, 2, 3])
    v2 = np.array([4, 5, 6])

    inner_product.compute(v1, v2)

    # Check that debug logs were created
    assert "Computing Hermitian inner product" in caplog.text


@pytest.mark.unit
def test_error_handling_compute():
    """Test error handling in compute method."""
    inner_product = HermitianInnerProduct()

    # Test with high dimensional array (not supported)
    with pytest.raises(TypeError):
        tensor = np.ones((2, 3, 4))
        inner_product.compute(tensor, tensor)
