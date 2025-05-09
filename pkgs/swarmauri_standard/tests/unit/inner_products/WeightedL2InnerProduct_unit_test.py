import pytest
import logging
from swarmauri_standard.swarmauri_standard.inner_products.WeightedL2InnerProduct import WeightedL2InnerProduct

@pytest.fixture
def weighted_l2_inner_product():
    """Fixture providing a default WeightedL2InnerProduct instance"""
    weight_function = lambda x: 1.0  # Default weight function
    domain = (0, 1)  # Default domain
    return WeightedL2InnerProduct(weight_function, domain)

@pytest.mark.unit
def test_type():
    """Test the type attribute of WeightedL2InnerProduct"""
    assert WeightedL2InnerProduct.type == "WeightedL2InnerProduct"

@pytest.mark.unit
def test_resource():
    """Test the resource attribute of WeightedL2InnerProduct"""
    assert WeightedL2InnerProduct.resource == "Inner_product"

@pytest.mark.unit
def test_weight_function_validation(weight_function):
    """Test validation of weight function"""
    # Test with valid weight function (should not raise error)
    valid_weight = lambda x: 1.0  # Positive function
    WeightedL2InnerProduct(valid_weight, (0, 1))

    # Test with invalid weight function (should raise ValueError)
    invalid_weight = lambda x: -1.0  # Negative function
    with pytest.raises(ValueError):
        WeightedL2InnerProduct(invalid_weight, (0, 1))

@pytest.mark.unit
def test_compute(weighted_l2_inner_product):
    """Test the compute method"""
    # Test with callable functions
    a = lambda x: x
    b = lambda x: x**2
    result = weighted_l2_inner_product.compute(a, b)
    assert result is not None
    assert isinstance(result, float)

    # Test with constants
    a = 2
    b = 3
    result = weighted_l2_inner_product.compute(a, b)
    assert result is not None
    assert isinstance(result, float)

@pytest.mark.unit
def test_conjugate_symmetry(weighted_l2_inner_product):
    """Test conjugate symmetry property"""
    a = lambda x: x
    b = lambda x: x**2

    inner_product_ab = weighted_l2_inner_product.compute(a, b)
    inner_product_ba = weighted_l2_inner_product.compute(b, a)

    # For real-valued functions, symmetry should hold
    assert inner_product_ab == pytest.approx(inner_product_ba)

@pytest.mark.unit
def test_positivity(weighted_l2_inner_product):
    """Test positivity property"""
    a = lambda x: 1  # Positive function
    result = weighted_l2_inner_product.compute(a, a)
    assert result > 0

@pytest.mark.unit
def test_linearity(weighted_l2_inner_product):
    """Test linearity property"""
    a = lambda x: x
    b = lambda x: x**2
    c = 2.0

    # Test additivity: <a + b, c> = <a, c> + <b, c>
    additivity = weighted_l2_inner_product.compute(
        lambda x: a(x) + b(x), lambda x: c
    )
    expected_additivity = (
        weighted_l2_inner_product.compute(a, lambda x: c) +
        weighted_l2_inner_product.compute(b, lambda x: c)
    )
    assert additivity == pytest.approx(expected_additivity)

    # Test homogeneity: <k*a, b> = k*<a, b>
    k = 2.0
    homogeneity = weighted_l2_inner_product.compute(
        lambda x: k * a(x), b
    )
    expected_homogeneity = k * weighted_l2_inner_product.compute(a, b)
    assert homogeneity == pytest.approx(expected_homogeneity)

@pytest.mark.unit
def test_logging(caplog):
    """Test logging functionality"""
    caplog.set_level(logging.DEBUG)
    
    a = lambda x: x
    b = lambda x: x**2
    
    weighted_l2_inner_product = WeightedL2InnerProduct(lambda x: 1, (0, 1))
    weighted_l2_inner_product.compute(a, b)
    
    # Verify that debug message was logged
    assert "Computing weighted L2 inner product" in caplog.text
    assert "Inner product result" in caplog.text