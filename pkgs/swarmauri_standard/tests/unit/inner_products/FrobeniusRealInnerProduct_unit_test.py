import pytest
import numpy as np
import logging
from swarmauri_standard.swarmauri_standard.inner_products.FrobeniusRealInnerProduct import (
    FrobeniusRealInnerProduct,
)


@pytest.fixture
def frobenius_inner_product():
    """Fixture to provide a FrobeniusRealInnerProduct instance for testing."""
    return FrobeniusRealInnerProduct()


@pytest.mark.unit
def test_type_attribute(frobenius_inner_product):
    """Test the type attribute of the FrobeniusRealInnerProduct class."""
    assert frobenius_inner_product.type == "FrobeniusRealInnerProduct"


@pytest.mark.unit
def test_compute_with_valid_matrices(frobenius_inner_product):
    """Test compute method with valid real matrices."""
    a = np.array([[1, 2], [3, 4]])
    b = np.array([[5, 6], [7, 8]])
    result = frobenius_inner_product.compute(a, b)
    expected_result = np.sum(a * b)
    assert np.isclose(result, expected_result)


@pytest.mark.unit
def test_compute_with_invalid_shapes(frobenius_inner_product):
    """Test compute method with matrices of different shapes."""
    a = np.array([[1, 2], [3, 4]])
    b = np.array([[5, 6]])
    with pytest.raises(ValueError):
        frobenius_inner_product.compute(a, b)


@pytest.mark.unit
def test_compute_with_complex_matrices(frobenius_inner_product):
    """Test compute method with complex matrices."""
    a = np.array([[1, 2], [3, 4]], dtype=np.complex64)
    b = np.array([[5, 6], [7, 8]], dtype=np.complex64)
    with pytest.raises(ValueError):
        frobenius_inner_product.compute(a, b)


@pytest.mark.unit
def test_check_conjugate_symmetry(frobenius_inner_product):
    """Test conjugate symmetry property."""
    a = np.random.rand(3, 3)
    b = np.random.rand(3, 3)
    result_ab = frobenius_inner_product.compute(a, b)
    result_ba = frobenius_inner_product.compute(b, a)
    assert np.isclose(result_ab, result_ba)


@pytest.mark.unit
def test_check_linearity_first_argument(frobenius_inner_product):
    """Test linearity in the first argument."""
    a = np.random.rand(2, 2)
    b = np.random.rand(2, 2)
    c = np.random.rand(2, 2)

    # Test addition
    result_add = frobenius_inner_product.compute(a + c, b)
    expected_add = frobenius_inner_product.compute(
        a, b
    ) + frobenius_inner_product.compute(c, b)

    # Test scalar multiplication
    scalar = 2.0
    result_mult = frobenius_inner_product.compute(scalar * a, b)
    expected_mult = scalar * frobenius_inner_product.compute(a, b)

    assert np.isclose(result_add, expected_add) and np.isclose(
        result_mult, expected_mult
    )


@pytest.mark.unit
def test_check_linearity_second_argument(frobenius_inner_product):
    """Test linearity in the second argument."""
    a = np.random.rand(2, 2)
    b = np.random.rand(2, 2)
    c = np.random.rand(2, 2)

    # Test addition
    result_add = frobenius_inner_product.compute(a, b + c)
    expected_add = frobenius_inner_product.compute(
        a, b
    ) + frobenius_inner_product.compute(a, c)

    # Test scalar multiplication
    scalar = 2.0
    result_mult = frobenius_inner_product.compute(a, scalar * b)
    expected_mult = scalar * frobenius_inner_product.compute(a, b)

    assert np.isclose(result_add, expected_add) and np.isclose(
        result_mult, expected_mult
    )


@pytest.mark.unit
def test_check_positivity(frobenius_inner_product):
    """Test positive definiteness."""
    a = np.random.rand(2, 2)
    result = frobenius_inner_product.check_positivity(a)
    assert result


@pytest.mark.unit
def test_check_positivity_zero_matrix(frobenius_inner_product):
    """Test positive definiteness with zero matrix."""
    a = np.zeros((2, 2))
    result = frobenius_inner_product.check_positivity(a)
    assert not result


@pytest.mark.unit
def test_logging_in_compute(frobenius_inner_product, caplog):
    """Test if logging occurs during compute method execution."""
    a = np.array([[1, 2], [3, 4]])
    b = np.array([[5, 6], [7, 8]])
    with caplog.at_level(logging.DEBUG):
        frobenius_inner_product.compute(a, b)
    assert "Computed Frobenius inner product:" in caplog.text


@pytest.mark.unit
@pytest.mark.parametrize("matrix_dim", [(2, 2), (3, 3), (4, 4)])
def test_compute_with_different_dimensions(frobenius_inner_product, matrix_dim):
    """Test compute method with matrices of different dimensions."""
    a = np.random.rand(*matrix_dim)
    b = np.random.rand(*matrix_dim)
    result = frobenius_inner_product.compute(a, b)
    expected_result = np.sum(a * b)
    assert np.isclose(result, expected_result)
