import logging

import numpy as np
import pytest

from swarmauri_standard.inner_products.RKHSInnerProduct import RKHSInnerProduct

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Define common kernel functions for testing
def linear_kernel(x, y):
    """Simple linear kernel: K(x, y) = x.T @ y"""
    return np.dot(x, y)


def polynomial_kernel(x, y, degree=2):
    """Polynomial kernel: K(x, y) = (x.T @ y + 1)^degree"""
    return (np.dot(x, y) + 1) ** degree


def rbf_kernel(x, y, gamma=1.0):
    """RBF kernel: K(x, y) = exp(-gamma * ||x - y||^2)"""
    return np.exp(-gamma * np.sum((x - y) ** 2))


@pytest.fixture
def linear_rkhs():
    """Fixture for a linear kernel RKHS inner product."""
    return RKHSInnerProduct(kernel_function=linear_kernel)


@pytest.fixture
def polynomial_rkhs():
    """Fixture for a polynomial kernel RKHS inner product."""
    return RKHSInnerProduct(
        kernel_function=lambda x, y: polynomial_kernel(x, y, degree=2)
    )


@pytest.fixture
def rbf_rkhs():
    """Fixture for an RBF kernel RKHS inner product."""
    return RKHSInnerProduct(kernel_function=lambda x, y: rbf_kernel(x, y, gamma=0.5))


@pytest.fixture
def vector_samples():
    """Fixture providing sample vectors for testing."""
    return [
        np.array([1.0, 0.0, 0.0]),
        np.array([0.0, 1.0, 0.0]),
        np.array([0.0, 0.0, 1.0]),
        np.array([1.0, 1.0, 0.0]),
        np.array([0.0, 1.0, 1.0]),
        np.array([1.0, 0.0, 1.0]),
        np.array([1.0, 1.0, 1.0]),
    ]


@pytest.mark.unit
def test_rkhs_type():
    """Test that the type attribute is correctly set."""
    rkhs = RKHSInnerProduct(kernel_function=linear_kernel)
    assert rkhs.type == "RKHSInnerProduct"


@pytest.mark.unit
def test_rkhs_resource():
    """Test that the resource attribute is correctly set."""
    rkhs = RKHSInnerProduct(kernel_function=linear_kernel)
    assert rkhs.resource == "InnerProduct"


@pytest.mark.unit
def test_rkhs_initialization():
    """Test that the RKHS inner product can be properly initialized."""
    rkhs = RKHSInnerProduct(kernel_function=linear_kernel)
    assert rkhs.kernel_function == linear_kernel
    assert callable(rkhs.kernel_function)


@pytest.mark.unit
@pytest.mark.parametrize(
    "kernel_func",
    [
        linear_kernel,
        lambda x, y: polynomial_kernel(x, y, degree=2),
        lambda x, y: rbf_kernel(x, y, gamma=0.5),
    ],
)
def test_rkhs_different_kernels(kernel_func):
    """Test that different kernel functions can be used."""
    rkhs = RKHSInnerProduct(kernel_function=kernel_func)
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([4.0, 5.0, 6.0])

    # Compute inner product using RKHS
    result = rkhs.compute(a, b)

    # Compute expected result directly
    expected = kernel_func(a, b)

    assert np.isclose(result, expected)


@pytest.mark.unit
def test_rkhs_compute(linear_rkhs):
    """Test the compute method for the linear kernel."""
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([4.0, 5.0, 6.0])

    # Expected result for linear kernel: dot product
    expected = np.dot(a, b)
    result = linear_rkhs.compute(a, b)

    assert np.isclose(result, expected)


@pytest.mark.unit
def test_rkhs_compute_error():
    """Test that compute method raises TypeError for incompatible inputs."""

    def bad_kernel(x, y):
        if not isinstance(x, np.ndarray) or not isinstance(y, np.ndarray):
            raise ValueError("Inputs must be numpy arrays")
        return np.dot(x, y)

    rkhs = RKHSInnerProduct(kernel_function=bad_kernel)

    with pytest.raises(TypeError):
        rkhs.compute("not an array", np.array([1, 2, 3]))


@pytest.mark.unit
def test_rkhs_conjugate_symmetry(
    linear_rkhs, polynomial_rkhs, rbf_rkhs, vector_samples
):
    """Test that the RKHS inner product satisfies conjugate symmetry."""
    for rkhs in [linear_rkhs, polynomial_rkhs, rbf_rkhs]:
        for a in vector_samples:
            for b in vector_samples:
                assert rkhs.check_conjugate_symmetry(a, b)


@pytest.mark.unit
def test_rkhs_linearity_first_argument(linear_rkhs):
    """Test linearity in the first argument for linear kernel."""
    a1 = np.array([1.0, 2.0, 3.0])
    a2 = np.array([4.0, 5.0, 6.0])
    b = np.array([7.0, 8.0, 9.0])
    alpha = 2.5
    beta = -1.5

    # Linear kernel should satisfy linearity
    assert linear_rkhs.check_linearity_first_argument(a1, a2, b, alpha, beta)


@pytest.mark.unit
def test_rkhs_positivity(linear_rkhs, polynomial_rkhs, rbf_rkhs, vector_samples):
    """Test that the RKHS inner product satisfies positivity."""
    for rkhs in [linear_rkhs, polynomial_rkhs, rbf_rkhs]:
        for a in vector_samples:
            assert rkhs.check_positivity(a)

    # Special case: zero vector
    zero_vector = np.zeros(3)
    for rkhs in [linear_rkhs, polynomial_rkhs, rbf_rkhs]:
        assert rkhs.check_positivity(zero_vector)


@pytest.mark.unit
def test_rkhs_positive_definite(linear_rkhs, polynomial_rkhs, rbf_rkhs, vector_samples):
    """Test that the kernel functions are positive definite."""
    for rkhs in [linear_rkhs, polynomial_rkhs, rbf_rkhs]:
        assert rkhs.is_positive_definite(vector_samples)


@pytest.mark.unit
def test_rkhs_with_random_vectors():
    """Test RKHS inner product with random vectors."""
    np.random.seed(42)  # For reproducibility

    # Generate random vectors
    vectors = [np.random.randn(5) for _ in range(10)]

    # Test with different kernels
    kernels = [
        linear_kernel,
        lambda x, y: polynomial_kernel(x, y, degree=3),
        lambda x, y: rbf_kernel(x, y, gamma=0.1),
    ]

    for kernel in kernels:
        rkhs = RKHSInnerProduct(kernel_function=kernel)

        # Check basic properties
        for a in vectors:
            for b in vectors:
                # Inner product should be symmetric for real-valued kernels
                assert np.isclose(rkhs.compute(a, b), rkhs.compute(b, a))

                # Self inner product should be non-negative
                if np.array_equal(a, b):
                    assert rkhs.compute(a, b) >= 0

        # Check positive definiteness
        assert rkhs.is_positive_definite(vectors)


@pytest.mark.unit
def test_rkhs_with_custom_kernel():
    """Test RKHS inner product with a custom kernel function."""

    # Define a custom kernel function
    def custom_kernel(x, y):
        """Custom kernel: K(x, y) = sin(x.T @ y)"""
        return np.sin(np.dot(x, y))

    rkhs = RKHSInnerProduct(kernel_function=custom_kernel)

    a = np.array([1.0, 2.0, 3.0])
    b = np.array([4.0, 5.0, 6.0])

    # Compute inner product using RKHS
    result = rkhs.compute(a, b)

    # Compute expected result directly
    expected = custom_kernel(a, b)

    assert np.isclose(result, expected)
