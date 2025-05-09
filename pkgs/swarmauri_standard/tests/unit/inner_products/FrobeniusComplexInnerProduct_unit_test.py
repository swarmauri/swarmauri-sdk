import pytest
import numpy as np
from swarmauri_standard.swarmauri_standard.inner_products.FrobeniusComplexInnerProduct import (
    FrobeniusComplexInnerProduct,
)


@pytest.fixture
def frobenius_complex_inner_product():
    """Fixture to provide an instance of FrobeniusComplexInnerProduct."""
    return FrobeniusComplexInnerProduct()


@pytest.mark.unit
def test_resource():
    """Test that the resource attribute is correctly set."""
    assert FrobeniusComplexInnerProduct.resource == "Inner_product"


@pytest.mark.unit
def test_type():
    """Test that the type attribute is correctly set."""
    assert FrobeniusComplexInnerProduct.type == "FrobeniusComplexInnerProduct"


@pytest.mark.unit
def test_compute(frobenius_complex_inner_product):
    """Test the compute method with valid complex matrices."""
    # Generate random complex matrices
    x = np.random.rand(3, 3) + 1j * np.random.rand(3, 3)
    y = np.random.rand(3, 3) + 1j * np.random.rand(3, 3)

    # Compute inner product
    result = frobenius_complex_inner_product.compute(x, y)

    # Assert result is a float
    assert isinstance(result, float)

    # Test invalid input
    with pytest.raises(ValueError):
        frobenius_complex_inner_product.compute("invalid", y)


@pytest.mark.unit
def test_check_conjugate_symmetry(frobenius_complex_inner_product):
    """Test the check_conjugate_symmetry method."""
    # Generate random complex matrices
    x = np.random.rand(3, 3) + 1j * np.random.rand(3, 3)
    y = np.random.rand(3, 3) + 1j * np.random.rand(3, 3)

    # Check symmetry
    assert frobenius_complex_inner_product.check_conjugate_symmetry(x, y)


@pytest.mark.unit
def test_check_linearity_first_argument(frobenius_complex_inner_product):
    """Test the check_linearity_first_argument method."""
    # Generate random complex matrices and scalars
    x = np.random.rand(3, 3) + 1j * np.random.rand(3, 3)
    y = np.random.rand(3, 3) + 1j * np.random.rand(3, 3)
    z = np.random.rand(3, 3) + 1j * np.random.rand(3, 3)
    a = np.random.rand()
    b = np.random.rand()

    # Check linearity
    assert frobenius_complex_inner_product.check_linearity_first_argument(x, y, z, a, b)


@pytest.mark.unit
def test_check_positivity(frobenius_complex_inner_product):
    """Test the check_positivity method."""
    # Test with non-zero matrix
    x = np.random.rand(3, 3) + 1j * np.random.rand(3, 3)
    assert frobenius_complex_inner_product.check_positivity(x)

    # Test with zero matrix
    x = np.zeros((3, 3), dtype=np.complex64)
    assert not frobenius_complex_inner_product.check_positivity(x)
