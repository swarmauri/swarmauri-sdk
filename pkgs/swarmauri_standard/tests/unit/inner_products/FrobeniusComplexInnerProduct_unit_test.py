import logging
from typing import TypeVar

import numpy as np
import pytest

from swarmauri_standard.inner_products.FrobeniusComplexInnerProduct import (
    FrobeniusComplexInnerProduct,
)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

Matrix = TypeVar("Matrix", bound=np.ndarray)


@pytest.fixture
def inner_product():
    """
    Fixture that provides a FrobeniusComplexInnerProduct instance for testing.

    Returns
    -------
    FrobeniusComplexInnerProduct
        An instance of the FrobeniusComplexInnerProduct class
    """
    return FrobeniusComplexInnerProduct()


@pytest.fixture
def complex_matrices():
    """
    Fixture that provides sample complex matrices for testing.

    Returns
    -------
    tuple
        A tuple containing various complex matrices for testing
    """
    # Create some test matrices
    a = np.array([[1 + 2j, 3 - 1j], [0 + 1j, 2 + 2j]])
    b = np.array([[2 - 1j, 1 + 1j], [3 - 2j, 0 + 0j]])
    zero = np.zeros((2, 2), dtype=complex)
    identity = np.eye(2, dtype=complex)

    return a, b, zero, identity


@pytest.mark.unit
def test_initialization():
    """Test the initialization of the FrobeniusComplexInnerProduct class."""
    inner_product = FrobeniusComplexInnerProduct()
    assert inner_product.type == "FrobeniusComplexInnerProduct"
    assert inner_product.resource == "InnerProduct"


@pytest.mark.unit
def test_compute_basic(inner_product, complex_matrices):
    """Test basic computation of inner product."""
    a, b, zero, identity = complex_matrices

    # Test inner product computation
    result = inner_product.compute(a, b)

    # Manual calculation for verification
    # For complex matrices A and B, <A,B> = Tr(A* B) = sum(conj(a_ij) * b_ij)
    expected = np.sum(np.conjugate(a) * b)

    assert np.isclose(result, expected)
    assert isinstance(result, complex)


@pytest.mark.unit
def test_compute_with_zero_matrix(inner_product, complex_matrices):
    """Test inner product computation with zero matrix."""
    a, b, zero, identity = complex_matrices

    # Inner product with zero should be zero
    result_a_zero = inner_product.compute(a, zero)
    result_zero_b = inner_product.compute(zero, b)

    assert np.isclose(result_a_zero, 0)
    assert np.isclose(result_zero_b, 0)


@pytest.mark.unit
def test_compute_with_identity_matrix(inner_product, complex_matrices):
    """Test inner product computation with identity matrix."""
    a, b, zero, identity = complex_matrices

    # Inner product with identity
    result = inner_product.compute(a, identity)

    # For identity matrix, <A,I> = Tr(A*)
    expected = np.trace(np.conjugate(a))

    assert np.isclose(result, expected)


@pytest.mark.unit
def test_compute_dimension_mismatch(inner_product):
    """Test inner product computation with mismatched dimensions."""
    a = np.array([[1 + 2j, 3 - 1j], [0 + 1j, 2 + 2j]])
    b = np.array([[2 - 1j, 1 + 1j, 3j], [3 - 2j, 0 + 0j, 1j]])

    with pytest.raises(ValueError):
        inner_product.compute(a, b)


@pytest.mark.unit
def test_conjugate_symmetry(inner_product, complex_matrices):
    """Test if the inner product satisfies conjugate symmetry property."""
    a, b, _, _ = complex_matrices

    # Check if <a,b> = conj(<b,a>)
    ab_inner = inner_product.compute(a, b)
    ba_inner = inner_product.compute(b, a)

    assert np.isclose(ab_inner, np.conjugate(ba_inner))
    assert inner_product.check_conjugate_symmetry(a, b)


@pytest.mark.unit
def test_linearity_first_argument(inner_product, complex_matrices):
    """Test if the inner product satisfies linearity in the first argument."""
    a, b, _, identity = complex_matrices

    alpha = 2.5
    beta = -1.3

    # Check if <alpha*a + beta*identity, b> = alpha*<a,b> + beta*<identity,b>
    assert inner_product.check_linearity_first_argument(a, identity, b, alpha, beta)

    # Manual verification
    left_side = inner_product.compute(alpha * a + beta * identity, b)
    right_side = alpha * inner_product.compute(a, b) + beta * inner_product.compute(
        identity, b
    )

    assert np.isclose(left_side, right_side)


@pytest.mark.unit
def test_positivity(inner_product, complex_matrices):
    """Test if the inner product satisfies positivity property."""
    a, _, zero, _ = complex_matrices

    # Check if <a,a> >= 0
    aa_inner = inner_product.compute(a, a)
    assert aa_inner.real >= 0
    assert np.isclose(aa_inner.imag, 0)

    # Check if <zero,zero> = 0
    zero_inner = inner_product.compute(zero, zero)
    assert np.isclose(zero_inner, 0)

    # Verify the check_positivity method
    assert inner_product.check_positivity(a)
    assert inner_product.check_positivity(zero)


@pytest.mark.unit
def test_norm(inner_product, complex_matrices):
    """Test the norm computation."""
    a, _, zero, _ = complex_matrices

    # Compute norm using the inner product
    norm_a = inner_product.norm(a)

    # Verify against numpy's Frobenius norm
    expected_norm = np.linalg.norm(a, "fro")

    assert np.isclose(norm_a, expected_norm)
    assert inner_product.norm(zero) == 0


@pytest.mark.unit
def test_norm_property(inner_product):
    """Test if the norm satisfies the properties of a norm."""
    # Property 1: ||A|| >= 0, and ||A|| = 0 iff A = 0
    zero_matrix = np.zeros((2, 2), dtype=complex)
    assert inner_product.norm(zero_matrix) == 0

    # Non-zero matrix should have positive norm
    a = np.array([[1 + 2j, 3 - 1j], [0 + 1j, 2 + 2j]])
    assert inner_product.norm(a) > 0

    # Property 2: ||cA|| = |c| * ||A|| for any scalar c
    c = 2.5 - 1.3j
    norm_ca = inner_product.norm(c * a)
    expected = abs(c) * inner_product.norm(a)
    assert np.isclose(norm_ca, expected)


@pytest.mark.unit
def test_serialization():
    """Test serialization and deserialization of the inner product."""
    inner_product = FrobeniusComplexInnerProduct()

    # Serialize to JSON
    json_data = inner_product.model_dump_json()

    # Deserialize from JSON
    deserialized = FrobeniusComplexInnerProduct.model_validate_json(json_data)

    # Check if the type is preserved
    assert deserialized.type == "FrobeniusComplexInnerProduct"
    assert deserialized.resource == "InnerProduct"


@pytest.mark.unit
@pytest.mark.parametrize(
    "a,b,expected",
    [
        # Simple 2x2 matrices
        (
            np.array([[1 + 0j, 0 + 0j], [0 + 0j, 1 + 0j]]),
            np.array([[1 + 0j, 0 + 0j], [0 + 0j, 1 + 0j]]),
            2 + 0j,
        ),
        # Complex matrices
        (
            np.array([[1 + 1j, 2 + 2j], [3 + 3j, 4 + 4j]]),
            np.array([[5 + 5j, 6 + 6j], [7 + 7j, 8 + 8j]]),
            140 + 0j,
        ),
        # Zero matrix
        (
            np.zeros((2, 2), dtype=complex),
            np.array([[1 + 1j, 2 + 2j], [3 + 3j, 4 + 4j]]),
            0 + 0j,
        ),
    ],
)
def test_compute_parameterized(inner_product, a, b, expected):
    """Parameterized test for inner product computation with various matrices."""
    result = inner_product.compute(a, b)
    assert np.isclose(result, expected)


@pytest.mark.unit
def test_error_handling(inner_product):
    """Test error handling in the inner product computation."""
    # Test with non-array inputs that can be converted
    result = inner_product.compute(
        [[1 + 0j, 0 + 0j], [0 + 0j, 1 + 0j]], [[1 + 0j, 0 + 0j], [0 + 0j, 1 + 0j]]
    )
    assert np.isclose(result, 2 + 0j)

    # Test with incompatible types
    with pytest.raises(Exception):
        inner_product.compute("not a matrix", np.eye(2, dtype=complex))

    # Test with incompatible shapes for norm
    with pytest.raises(Exception):
        inner_product.compute(
            np.array([1 + 0j, 2 + 0j]), np.array([[1 + 0j, 0 + 0j], [0 + 0j, 1 + 0j]])
        )
