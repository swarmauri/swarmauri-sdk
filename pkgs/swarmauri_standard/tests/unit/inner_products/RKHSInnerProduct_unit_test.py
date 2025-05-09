"""Unit tests for the RKHSInnerProduct class in the swarmauri_standard package."""

import pytest
import numpy as np
from swarmauri_standard.swarmauri_standard.inner_products.RKHSInnerProduct import (
    RKHSInnerProduct,
)
from base.swarmauri_standard.kernels import LinearKernel
from base.swarmauri_core.inner_products.IInnerProduct import IVector


@pytest.fixture
def rkhsinnerproduct() -> RKHSInnerProduct:
    """Fixture to create an RKHSInnerProduct instance with a linear kernel."""
    return RKHSInnerProduct(kernel=LinearKernel())


@pytest.fixture
def kernel_vector() -> IVector:
    """Fixture to create a sample vector for testing."""
    return np.random.randn(5)


@pytest.mark.unit
def test_compute(rkhsinnerproduct: RKHSInnerProduct, kernel_vector: IVector):
    """Test the compute method of the RKHSInnerProduct class."""
    x = kernel_vector
    y = kernel_vector
    result = rkhsinnerproduct.compute(x, y)
    assert result == pytest.approx(np.dot(x, y))


@pytest.mark.unit
def test_conjugate_symmetry(rkhsinnerproduct: RKHSInnerProduct, kernel_vector: IVector):
    """Test the conjugate symmetry property of the RKHSInnerProduct."""
    x = kernel_vector
    y = kernel_vector
    k_xy = rkhsinnerproduct.compute(x, y)
    k_yx = rkhsinnerproduct.compute(y, x)
    assert k_xy == k_yx


@pytest.mark.unit
def test_linearity(rkhsinnerproduct: RKHSInnerProduct, kernel_vector: IVector):
    """Test the linearity property in the first argument."""
    x = kernel_vector
    y = kernel_vector
    z = kernel_vector
    a = 2.0
    b = 3.0

    lhs = rkhsinnerproduct.compute((a * x) + (b * y), z)
    rhs = a * rkhsinnerproduct.compute(x, z) + b * rkhsinnerproduct.compute(y, z)

    assert lhs == pytest.approx(rhs)


@pytest.mark.unit
def test_positivity(rkhsinnerproduct: RKHSInnerProduct, kernel_vector: IVector):
    """Test the positivity property of the RKHSInnerProduct."""
    x = kernel_vector
    value = rkhsinnerproduct.compute(x, x)
    assert value > 0
