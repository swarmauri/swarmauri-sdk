import pytest
import numpy as np
from swarmauri_standard.swarmauri_standard.inner_products.TraceFormWeightedInnerProduct import (
    TraceFormWeightedInnerProduct,
)
import logging


@pytest.fixture
def weight_matrix():
    """Fixture providing a default weight matrix for testing"""
    return np.identity(2)


@pytest.mark.unit
def test_compute(weight_matrix):
    """Test the compute method of TraceFormWeightedInnerProduct"""
    # Create test vectors
    x = np.array([1, 2], dtype=np.float64)
    y = np.array([3, 4], dtype=np.float64)

    # Initialize the inner product instance
    inner_product = TraceFormWeightedInnerProduct(weight_matrix)

    # Compute the inner product
    result = inner_product.compute(x, y)

    # Expected result with identity matrix
    expected = np.trace(
        np.dot(x.reshape(2, 1).T, np.dot(weight_matrix, y.reshape(2, 1)))
    )

    # Assert the computed result matches expected
    assert np.isclose(result, expected)


@pytest.mark.unit
def test_conjugate_symmetry(weight_matrix):
    """Test conjugate symmetry property"""
    x = np.array([1, 2], dtype=np.complex128)
    y = np.array([3, 4], dtype=np.complex128)

    inner_product = TraceFormWeightedInnerProduct(weight_matrix)

    # Compute both inner products
    xy = inner_product.compute(x, y)
    yx = inner_product.compute(y, x)

    # Check conjugate symmetry
    assert np.isclose(xy, yx.conjugate())


@pytest.mark.unit
def test_linearity(weight_matrix):
    """Test linearity in the first argument"""
    x = np.array([1, 2], dtype=np.float64)
    y = np.array([3, 4], dtype=np.float64)
    z = np.array([5, 6], dtype=np.float64)
    a = 2.0
    b = 3.0

    inner_product = TraceFormWeightedInnerProduct(weight_matrix)

    # Compute <ax + by, z>
    ax = a * x
    by = b * y
    lhs = inner_product.compute(ax + by, z)

    # Compute a<x, z> + b<y, z>
    rhs = a * inner_product.compute(x, z) + b * inner_product.compute(y, z)

    assert np.isclose(lhs, rhs)


@pytest.mark.unit
def test_positivity(weight_matrix):
    """Test positivity of the inner product"""
    x = np.array([1, 1], dtype=np.float64)

    inner_product = TraceFormWeightedInnerProduct(weight_matrix)

    value = inner_product.compute(x, x)

    assert value > 0


@pytest.mark.unit
def test_incompatible_dimensions():
    """Test incompatible vector dimensions"""
    weight_matrix = np.array([[1, 2], [3, 4]])
    x = np.array([1, 2, 3], dtype=np.float64)
    y = np.array([4, 5, 6], dtype=np.float64)

    inner_product = TraceFormWeightedInnerProduct(weight_matrix)

    with pytest.raises(ValueError):
        inner_product.compute(x, y)


@pytest.mark.unit
def test_resource():
    """Test the resource property"""
    assert TraceFormWeightedInnerProduct.resource == "Inner_product"


@pytest.mark.unit
def test_type():
    """Test the type property"""
    assert TraceFormWeightedInnerProduct.type == "TraceFormWeightedInnerProduct"
