import pytest
import logging
from swarmauri_standard.swarmauri_standard.inner_products.EuclideanInnerProduct import EuclideanInnerProduct

logger = logging.getLogger(__name__)

@pytest.mark.unit
def test_compute():
    """Test the compute method of the EuclideanInnerProduct class."""
    # Setup
    euclidean_inner_product = EuclideanInnerProduct()
    x = [1, 2, 3]
    y = [4, 5, 6]
    
    # Expected result
    expected_result = 1*4 + 2*5 + 3*6
    
    # Execution
    result = euclidean_inner_product.compute(x, y)
    
    # Assertion
    assert result == expected_result
    logger.debug("Test compute method passed")

@pytest.mark.unit
def test_compute_different_dimensions():
    """Test compute method with vectors of different dimensions."""
    euclidean_inner_product = EuclideanInnerProduct()
    x = [1, 2]
    y = [3, 4, 5]
    
    with pytest.raises(ValueError):
        euclidean_inner_product.compute(x, y)
    logger.debug("Test compute with different dimensions passed")

@pytest.mark.unit
def test_check_conjugate_symmetry():
    """Test the conjugate symmetry check method."""
    euclidean_inner_product = EuclideanInnerProduct()
    x = [1, 2]
    y = [3, 4]
    
    # Compute inner product both ways
    inner_xy = euclidean_inner_product.compute(x, y)
    inner_yx = euclidean_inner_product.compute(y, x)
    
    # Check symmetry
    assert inner_xy == inner_yx
    logger.debug("Test conjugate symmetry passed")

@pytest.mark.unit
def test_check_linearity_first_argument():
    """Test linearity in the first argument."""
    euclidean_inner_product = EuclideanInnerProduct()
    x = [1, 2]
    y = [3, 4]
    z = [5, 6]
    a = 2.0
    b = 3.0
    
    # Compute LHS: <a*x + b*y, z>
    ax_plus_by = [a*x[0] + b*y[0], a*x[1] + b*y[1]]
    lhs = euclidean_inner_product.compute(ax_plus_by, z)
    
    # Compute RHS: a*<x, z> + b*<y, z>
    inner_xz = euclidean_inner_product.compute(x, z)
    inner_yz = euclidean_inner_product.compute(y, z)
    rhs = a * inner_xz + b * inner_yz
    
    assert lhs == rhs
    logger.debug("Test linearity in first argument passed")

@pytest.mark.unit
def test_check_positivity():
    """Test the positivity property."""
    euclidean_inner_product = EuclideanInnerProduct()
    x = [1, 2]
    
    # Compute inner product with itself
    inner_xx = euclidean_inner_product.compute(x, x)
    
    assert inner_xx > 0
    logger.debug("Test positivity passed")

@pytest.mark.unit
def test_check_positivity_zero_vector():
    """Test positivity with a zero vector."""
    euclidean_inner_product = EuclideanInnerProduct()
    x = [0, 0]
    
    inner_xx = euclidean_inner_product.compute(x, x)
    assert inner_xx == 0
    logger.debug("Test positivity with zero vector passed")