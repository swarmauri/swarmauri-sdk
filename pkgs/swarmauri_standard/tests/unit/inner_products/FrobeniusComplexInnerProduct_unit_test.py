import pytest
import numpy as np
import logging

from swarmauri_standard.swarmauri_standard.inner_products.FrobeniusComplexInnerProduct import (
    FrobeniusComplexInnerProduct,
)


@pytest.fixture
def inner_product():
    """Fixture to provide an instance of FrobeniusComplexInnerProduct"""
    return FrobeniusComplexInnerProduct()


@pytest.mark.unit
def test_compute(inner_product):
    """Test computation of Frobenius inner product with complex matrices"""
    # Test with 2x2 complex matrices
    a = np.array([[1 + 2j, 3 + 4j], [5 + 6j, 7 + 8j]])
    b = np.array([[9 + 10j, 11 + 12j], [13 + 14j, 15 + 16j]])

    # Expected result from manual calculation
    expected = 70 + 90j

    result = inner_product.compute(a, b)
    assert np.isclose(result, expected)


@pytest.mark.unit
def test_conjugate_symmetry(inner_product):
    """Test conjugate symmetry property"""
    a = np.array([[1 + 2j], [3 + 4j]])
    b = np.array([[5 + 6j], [7 + 8j]])

    inner_product_ab = inner_product.compute(a, b)
    inner_product_ba = inner_product.compute(b, a)

    # Check conjugate symmetry
    assert np.isclose(inner_product_ab, np.conj(inner_product_ba))


@pytest.mark.unit
def test_linearity_first_argument(inner_product):
    """Test linearity in the first argument"""
    a = np.array([[1, 2], [3, 4]])
    b = np.array([[5, 6], [7, 8]])
    c = np.array([[9, 10], [11, 12]])

    # Test additivity: <a + c, b> = <a, b> + <c, b>
    add_result = inner_product.compute(a + c, b)
    expected_add = inner_product.compute(a, b) + inner_product.compute(c, b)
    assert np.isclose(add_result, expected_add)

    # Test homogeneity: <2.0*a, b> = 2.0*<a, b>
    k = 2.0
    homo_result = inner_product.compute(k * a, b)
    expected_homo = k * inner_product.compute(a, b)
    assert np.isclose(homo_result, expected_homo)


@pytest.mark.unit
def test_positivity(inner_product):
    """Test positive definiteness"""
    a = np.array([[1, 2], [3, 4]])
    result = inner_product.check_positivity(a)
    assert result > 0

    # Test with zero matrix
    zero_matrix = np.zeros((2, 2))
    zero_result = inner_product.check_positivity(zero_matrix)
    assert zero_result == 0


@pytest.mark.unit
def test_type():
    """Test type identifier"""
    assert FrobeniusComplexInnerProduct.type == "FrobeniusComplexInnerProduct"


@pytest.mark.unit
def test_compute_complex_matrices():
    """Test compute method with different complex matrices"""
    a = np.array([[1 + 1j, 2 + 2j], [3 + 3j, 4 + 4j]])
    b = np.array([[5 + 5j, 6 + 6j], [7 + 7j, 8 + 8j]])

    inner_product = FrobeniusComplexInnerProduct()
    result = inner_product.compute(a, b)

    # Expected result from manual calculation
    expected = 70 + 70j
    assert np.isclose(result, expected)


@pytest.mark.unit
def test_compute_random_matrices():
    """Test compute method with random complex matrices"""
    np.random.seed(42)
    a = np.random.rand(3, 3) + 1j * np.random.rand(3, 3)
    b = np.random.rand(3, 3) + 1j * np.random.rand(3, 3)

    inner_product = FrobeniusComplexInnerProduct()
    result = inner_product.compute(a, b)

    # Verify the result is a complex number
    assert isinstance(result, (float, complex))
    assert not np.isnan(result)
