import pytest
import numpy as np
from swarmauri_standard.swarmauri_standard.inner_products.FrobeniusRealInnerProduct import FrobeniusRealInnerProduct

@pytest.fixture
def frobenius_real_inner_product():
    """Fixture to provide an instance of FrobeniusRealInnerProduct."""
    return FrobeniusRealInnerProduct()

@pytest.mark.unit
def test_compute(frobenius_real_inner_product):
    """Test the compute method of FrobeniusRealInnerProduct."""
    x = np.array([[1, 2], [3, 4]])
    y = np.array([[5, 6], [7, 8]])
    expected_result = np.trace(x.T @ y)
    assert frobenius_real_inner_product.compute(x, y) == expected_result

@pytest.mark.unit
def test_compute_invalid_shapes(frobenius_real_inner_product):
    """Test compute with matrices of different shapes."""
    x = np.array([[1, 2], [3, 4]])
    y = np.array([[5, 6]])
    with pytest.raises(ValueError):
        frobenius_real_inner_product.compute(x, y)

@pytest.mark.unit
def test_check_conjugate_symmetry(frobenius_real_inner_product):
    """Test conjugate symmetry check."""
    x = np.array([[1, 2], [3, 4]])
    y = np.array([[5, 6], [7, 8]])
    assert frobenius_real_inner_product.check_conjugate_symmetry(x, y)

@pytest.mark.unit
def test_check_linearity_first_argument(frobenius_real_inner_product):
    """Test linearity in first argument."""
    x = np.array([[1, 2], [3, 4]])
    y = np.array([[5, 6], [7, 8]])
    z = np.array([[9, 10], [11, 12]])
    a = 2.0
    b = 3.0
    left_side = frobenius_real_inner_product.compute(a * x + b * y, z)
    right_side = a * frobenius_real_inner_product.compute(x, z) + b * frobenius_real_inner_product.compute(y, z)
    assert frobenius_real_inner_product.check_linearity_first_argument(x, y, z, a, b)

@pytest.mark.unit
def test_check_positivity(frobenius_real_inner_product):
    """Test positivity check."""
    x = np.array([[1, 2], [3, 4]])
    assert frobenius_real_inner_product.check_positivity(x)

@pytest.mark.unit
def test_check_positivity_zero_matrix(frobenius_real_inner_product):
    """Test positivity with zero matrix."""
    x = np.array([[0, 0], [0, 0]])
    assert not frobenius_real_inner_product.check_positivity(x)