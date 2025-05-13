import pytest
from swarmauri_standard.inner_products.RKHSInnerProduct import RKHSInnerProduct
import numpy as np
import logging

logger = logging.getLogger(__name__)


@pytest.fixture
def rkhs_inner_product():
    """Fixture providing a basic RKHSInnerProduct instance with a default kernel."""

    # Using a simple linear kernel as the default
    def linear_kernel(a, b):
        return np.dot(a, b)

    return RKHSInnerProduct(kernel=linear_kernel)


@pytest.mark.unit
def test_type():
    """Tests that the type attribute is correctly set."""
    instance = RKHSInnerProduct()
    assert instance.type == "RKHSInnerProduct"


@pytest.mark.unit
def test_compute_with_vectors(rkhs_inner_product):
    """Tests computing the inner product with vector inputs."""
    a = np.array([1, 2, 3])
    b = np.array([4, 5, 6])
    result = rkhs_inner_product.compute(a, b)
    assert result > 0  # Kernel should be positive-definite


@pytest.mark.unit
def test_compute_with_callables(rkhs_inner_product):
    """Tests computing the inner product with callable inputs."""

    def a():
        return np.array([1, 2, 3])

    def b():
        return np.array([4, 5, 6])

    result = rkhs_inner_product.compute(a, b)
    assert result > 0  # Kernel should be positive-definite


@pytest.mark.unit
def test_check_positive_definite(rkhs_inner_product):
    """Tests the positive-definite check functionality."""
    a = np.array([1, 2, 3])
    rkhs_inner_product.check_positive_definite(a)

    # Test with a non-positive-definite kernel
    def non_pd_kernel(a, b):
        return -1.0

    rkhs_pd = RKHSInnerProduct(kernel=non_pd_kernel)
    with pytest.raises(ValueError):
        rkhs_pd.check_positive_definite(a)


@pytest.mark.unit
def test_set_kernel():
    """Tests the set_kernel method functionality."""

    def custom_kernel(a, b):
        return np.dot(a, b)

    rkhs = RKHSInnerProduct()  # Initialize without kernel
    rkhs.set_kernel(custom_kernel)

    assert rkhs.kernel is not None
    assert rkhs.kernel == custom_kernel
