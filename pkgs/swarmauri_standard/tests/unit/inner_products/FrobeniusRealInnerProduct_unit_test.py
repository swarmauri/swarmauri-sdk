import pytest
import numpy as np
import logging

from swarmauri_standard.inner_products.FrobeniusRealInnerProduct import FrobeniusRealInnerProduct

@pytest.fixture
def frobenius_inner_product():
    """Fixture to provide a FrobeniusRealInnerProduct instance for testing."""
    return FrobeniusRealInnerProduct()

@pytest.mark.unit
def test_compute_with_zero_matrices(frobenius_inner_product):
    """
    Test compute method with zero matrices.

    Verifies that the inner product of two zero matrices is zero.
    """
    a = np.zeros((2, 2))
    b = np.zeros((2, 2))
    result = frobenius_inner_product.compute(a, b)
    assert result == 0.0

@pytest.mark.unit
def test_compute_with_identity_matrices(frobenius_inner_product):
    """
    Test compute method with identity matrices.

    Verifies that the inner product of identity matrices of different sizes
    results in the sum of 1s on the diagonal.
    """
    # 2x2 identity matrix
    a = np.eye(2)
    b = np.eye(2)
    result = frobenius_inner_product.compute(a, b)
    assert result == 2.0

    # 3x3 identity matrix
    a = np.eye(3)
    b = np.eye(3)
    result = frobenius_inner_product.compute(a, b)
    assert result == 3.0

@pytest.mark.unit
def test_compute_with_random_matrices(frobenius_inner_product):
    """
    Test compute method with random matrices.

    Verifies that the inner product computation works correctly for random
    matrices and that the result is a float.
    """
    np.random.seed(42)
    a = np.random.rand(3, 3)
    b = np.random.rand(3, 3)
    result = frobenius_inner_product.compute(a, b)
    assert isinstance(result, float)

@pytest.mark.unit
def test_compute_with_different_shapes(frobenius_inner_product):
    """
    Test compute method with matrices of different shapes.

    Verifies that the method raises a ValueError when input matrices
    have different shapes.
    """
    a = np.zeros((2, 3))
    b = np.zeros((3, 2))
    with pytest.raises(ValueError):
        frobenius_inner_product.compute(a, b)

@pytest.mark.unit
def test_check_conjugate_symmetry(frobenius_inner_product):
    """
    Test the conjugate symmetry property.

    Verifies that the inner product of a and b is equal to the inner product
    of b and a, which should always hold for real matrices.
    """
    np.random.seed(42)
    a = np.random.rand(3, 3)
    b = np.random.rand(3, 3)
    
    inner_ab = frobenius_inner_product.compute(a, b)
    inner_ba = frobenius_inner_product.compute(b, a)
    
    assert np.isclose(inner_ab, inner_ba)

@pytest.mark.unit
def test_compute_with_non_numeric_input(frobenius_inner_product):
    """
    Test compute method with non-numeric input.

    Verifies that the method raises a ValueError when inputs are not numeric.
    """
    a = "non_numeric_input"
    b = np.zeros((2, 2))
    
    with pytest.raises(ValueError):
        frobenius_inner_product.compute(a, b)

@pytest.mark.unit
def test_logging(frobenius_inner_product, caplog):
    """
    Test that logging messages are generated during computation.

    Verifies that debug level logs are emitted when compute is called.
    """
    caplog.set_level(logging.DEBUG)
    
    a = np.zeros((2, 2))
    b = np.zeros((2, 2))
    frobenius_inner_product.compute(a, b)
    
    assert "Starting computation of Frobenius inner product" in caplog.text
    assert "Frobenius inner product result: 0.0" in caplog.text