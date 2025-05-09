import pytest
import numpy as np
import logging
from swarmauri_standard.swarmauri_standard.inner_products.WeightedL2InnerProduct import (
    WeightedL2InnerProduct,
)


@pytest.mark.unit
def test_WeightedL2InnerProduct_resource():
    """Test that the resource property returns the correct value."""
    assert WeightedL2InnerProduct.resource == "Inner_product"


@pytest.mark.unit
def test_WeightedL2InnerProduct_type():
    """Test that the type property returns the correct value."""
    assert WeightedL2InnerProduct.type == "WeightedL2InnerProduct"


@pytest.fixture
def weighted_inner_product():
    """Fixture to provide a default WeightedL2InnerProduct instance."""
    # Using a simple weight array for testing
    weight = np.array([1.0, 1.0, 1.0])
    return WeightedL2InnerProduct(weight)


@pytest.mark.unit
def test_compute(weighted_inner_product):
    """Test the compute method with sample vectors."""
    a = np.array([1, 2, 3])
    b = np.array([4, 5, 6])

    # Compute weighted inner product
    result = weighted_inner_product.compute(a, b)

    # Expected result without weights (for verification)
    expected_unweighted = np.vdot(a, b)

    # Since weights are all 1.0 in this case, result should match expected_unweighted
    assert np.isclose(result, expected_unweighted)


@pytest.mark.unit
def test_compute_with_callable_weight():
    """Test compute method with a callable weight."""

    # Define a callable weight that returns an array
    def weight_callable(x):
        return np.array([0.5, 1.0, 2.0])

    weighted = WeightedL2InnerProduct(weight_callable)

    a = np.array([1, 2, 3])
    b = np.array([4, 5, 6])

    result = weighted.compute(a, b)

    # Compute expected result manually
    weights = weight_callable(a)
    weighted_a = a * np.sqrt(weights)
    weighted_b = b * np.sqrt(weights)
    expected_result = np.vdot(weighted_a.ravel(), weighted_b.ravel())

    assert np.isclose(result, expected_result)


@pytest.mark.unit
def test_check_conjugate_symmetry(weighted_inner_product):
    """Test the conjugate symmetry property."""
    a = np.array([1, 2])
    b = np.array([3, 4])

    inner_product_ab = weighted_inner_product.compute(a, b)
    inner_product_ba = weighted_inner_product.compute(b, a)

    # Check if inner_product_ab is the conjugate of inner_product_ba
    assert np.isclose(inner_product_ab, np.conj(inner_product_ba))


@pytest.mark.unit
def test_check_linearity_first_argument(weighted_inner_product):
    """Test linearity in the first argument."""
    a = np.array([1, 2])
    b = np.array([3, 4])
    c = np.array([5, 6])

    # Test additivity
    inner_product_add = weighted_inner_product.compute(a + c, b)
    inner_product_sum = weighted_inner_product.compute(
        a, b
    ) + weighted_inner_product.compute(c, b)

    # Test homogeneity
    scalar = 2.0
    inner_product_scale = weighted_inner_product.compute(scalar * a, b)
    inner_product_scaled = scalar * weighted_inner_product.compute(a, b)

    assert np.isclose(inner_product_add, inner_product_sum)
    assert np.isclose(inner_product_scale, inner_product_scaled)


@pytest.mark.unit
def test_check_positivity(weighted_inner_product):
    """Test positive definiteness."""
    a = np.array([1, 2, 3])

    inner_product = weighted_inner_product.compute(a, a)

    assert inner_product > 0


@pytest.mark.unit
def test_invalid_weights():
    """Test that invalid weights raise a ValueError."""
    # Test with non-positive weights
    weight = np.array([1.0, -1.0, 1.0])

    with pytest.raises(ValueError):
        WeightedL2InnerProduct(weight)

    # Test with zero weights
    weight = np.array([1.0, 0.0, 1.0])

    with pytest.raises(ValueError):
        WeightedL2InnerProduct(weight)
