import pytest
import numpy as np
import logging
from typing import Any, List, Tuple
from swarmauri_standard.inner_products.RKHSReproducing import RKHSReproducing

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define fixtures for common test data
@pytest.fixture
def default_rkhs():
    """
    Fixture providing a default RKHSReproducing instance with the default RBF kernel.
    
    Returns
    -------
    RKHSReproducing
        An instance of the RKHSReproducing class with default settings
    """
    return RKHSReproducing()

@pytest.fixture
def custom_kernel_rkhs():
    """
    Fixture providing a RKHSReproducing instance with a custom polynomial kernel.
    
    Returns
    -------
    RKHSReproducing
        An instance of the RKHSReproducing class with a polynomial kernel
    """
    def polynomial_kernel(x: Any, y: Any, degree: int = 2) -> float:
        """Simple polynomial kernel k(x,y) = (x·y + 1)^degree"""
        x_array = np.asarray(x, dtype=np.float64)
        y_array = np.asarray(y, dtype=np.float64)
        return float(np.power(np.dot(x_array, y_array) + 1, degree))
    
    return RKHSReproducing(kernel_func=polynomial_kernel)

@pytest.fixture
def vector_pairs() -> List[Tuple[np.ndarray, np.ndarray]]:
    """
    Fixture providing various vector pairs for testing.
    
    Returns
    -------
    List[Tuple[np.ndarray, np.ndarray]]
        List of vector pairs for testing inner product computation
    """
    return [
        (np.array([1.0, 0.0]), np.array([1.0, 0.0])),
        (np.array([1.0, 0.0]), np.array([0.0, 1.0])),
        (np.array([1.0, 2.0, 3.0]), np.array([4.0, 5.0, 6.0])),
        (np.array([0.0, 0.0, 0.0]), np.array([0.0, 0.0, 0.0])),
    ]

@pytest.fixture
def data_points_list() -> List[List[np.ndarray]]:
    """
    Fixture providing lists of data points for testing positive definiteness.
    
    Returns
    -------
    List[List[np.ndarray]]
        List of data point sets for positive definiteness testing
    """
    return [
        [np.array([1.0, 0.0]), np.array([0.0, 1.0]), np.array([1.0, 1.0])],
        [np.array([i, i**2]) for i in range(5)],
        [np.random.rand(3) for _ in range(10)],
    ]


@pytest.mark.unit
def test_rkhs_type_attribute():
    """Test that the type attribute is correctly set."""
    rkhs = RKHSReproducing()
    assert rkhs.type == "RKHSReproducing"


@pytest.mark.unit
def test_rkhs_resource_attribute():
    """Test that the resource attribute is correctly set."""
    rkhs = RKHSReproducing()
    assert rkhs.resource == "inner_product"


@pytest.mark.unit
def test_default_initialization(default_rkhs):
    """Test that the default initialization creates a valid instance."""
    assert default_rkhs is not None
    assert hasattr(default_rkhs, 'kernel_func')
    assert callable(default_rkhs.kernel_func)


@pytest.mark.unit
def test_custom_kernel_initialization():
    """Test initialization with a custom kernel function."""
    def linear_kernel(x, y):
        return np.dot(np.array(x), np.array(y))
    
    rkhs = RKHSReproducing(kernel_func=linear_kernel)
    assert rkhs.kernel_func == linear_kernel
    
    # Test the kernel works as expected
    result = rkhs.compute(np.array([1, 2]), np.array([3, 4]))
    assert result == 11.0  # 1*3 + 2*4 = 11


@pytest.mark.unit
@pytest.mark.parametrize("vec1, vec2, expected", [
    (np.array([1.0, 0.0]), np.array([1.0, 0.0]), 1.0),  # Same vector
    (np.array([1.0, 0.0]), np.array([0.0, 1.0]), np.exp(-2.0)),  # Orthogonal vectors
    (np.array([0.0, 0.0]), np.array([0.0, 0.0]), 1.0),  # Zero vectors
])
def test_default_rbf_kernel_compute(default_rkhs, vec1, vec2, expected):
    """Test computation with the default RBF kernel."""
    result = default_rkhs.compute(vec1, vec2)
    assert np.isclose(result, expected)


@pytest.mark.unit
def test_custom_kernel_compute(custom_kernel_rkhs):
    """Test computation with a custom kernel."""
    vec1 = np.array([1.0, 2.0])
    vec2 = np.array([3.0, 4.0])
    
    # For polynomial kernel (x·y + 1)^2 with x=[1,2], y=[3,4]
    # (1*3 + 2*4 + 1)^2 = (3 + 8 + 1)^2 = 12^2 = 144
    expected = 144.0
    
    result = custom_kernel_rkhs.compute(vec1, vec2)
    assert np.isclose(result, expected)


@pytest.mark.unit
def test_set_kernel():
    """Test setting a new kernel function."""
    rkhs = RKHSReproducing()
    
    # Original kernel is RBF
    vec1 = np.array([1.0, 0.0])
    vec2 = np.array([0.0, 1.0])
    original_result = rkhs.compute(vec1, vec2)
    assert np.isclose(original_result, np.exp(-2.0))
    
    # Set new kernel (linear)
    def linear_kernel(x, y):
        return float(np.dot(np.array(x), np.array(y)))
    
    rkhs.set_kernel(linear_kernel)
    
    # Test with new kernel
    new_result = rkhs.compute(vec1, vec2)
    assert np.isclose(new_result, 0.0)  # Dot product of orthogonal vectors is 0


@pytest.mark.unit
@pytest.mark.parametrize("vec1, vec2, compatible", [
    (np.array([1.0, 2.0]), np.array([3.0, 4.0]), True),  # Compatible numpy arrays
    ([1.0, 2.0], [3.0, 4.0], True),  # Compatible lists
    (1.0, 2.0, True),  # Compatible scalars
    (np.array([1.0, 2.0]), np.array([3.0, 4.0, 5.0]), False),  # Different dimensions
    (np.array([1.0, 2.0]), "not_a_vector", False),  # Incompatible types
])
def test_is_compatible(default_rkhs, vec1, vec2, compatible):
    """Test compatibility checking for different types of inputs."""
    assert default_rkhs.is_compatible(vec1, vec2) == compatible


@pytest.mark.unit
def test_compute_with_incompatible_vectors(default_rkhs):
    """Test that compute raises ValueError for incompatible vectors."""
    vec1 = np.array([1.0, 2.0])
    vec2 = "not_a_vector"
    
    with pytest.raises(ValueError):
        default_rkhs.compute(vec1, vec2)


@pytest.mark.unit
@pytest.mark.parametrize("data_points_idx", [0, 1, 2])
def test_is_positive_definite(default_rkhs, data_points_list, data_points_idx):
    """Test positive definiteness checking for the RBF kernel."""
    data_points = data_points_list[data_points_idx]
    
    # RBF kernel is always positive definite
    assert default_rkhs.is_positive_definite(data_points)


@pytest.mark.unit
def test_is_positive_definite_empty_data(default_rkhs):
    """Test positive definiteness checking with empty data."""
    # Empty data should return True by convention
    assert default_rkhs.is_positive_definite([])


@pytest.mark.unit
def test_non_positive_definite_kernel():
    """Test a kernel that is not positive definite."""
    def non_pd_kernel(x, y):
        """A kernel that is not positive definite."""
        x_array = np.asarray(x)
        y_array = np.asarray(y)
        # This is not a valid kernel (does not satisfy Mercer's condition)
        if np.array_equal(x_array, y_array):
            return -1.0  # Negative on diagonal, violating PD property
        return 0.0
    
    rkhs = RKHSReproducing(kernel_func=non_pd_kernel)
    data_points = [np.array([1.0, 0.0]), np.array([0.0, 1.0])]
    
    assert not rkhs.is_positive_definite(data_points)


@pytest.mark.unit
def test_serialization():
    """Test serialization and deserialization."""
    rkhs = RKHSReproducing()
    serialized = rkhs.model_dump_json()
    deserialized = RKHSReproducing.model_validate_json(serialized)
    
    assert deserialized.type == rkhs.type
    assert deserialized.resource == rkhs.resource


@pytest.mark.unit
def test_kernel_with_error_handling():
    """Test error handling in kernel computation."""
    def problematic_kernel(x, y):
        """A kernel that raises an exception for certain inputs."""
        if isinstance(x, str) or isinstance(y, str):
            raise ValueError("Cannot process string inputs")
        return float(np.dot(np.array(x), np.array(y)))
    
    rkhs = RKHSReproducing(kernel_func=problematic_kernel)
    
    # Should work with valid inputs
    assert np.isclose(rkhs.compute([1, 2], [3, 4]), 11.0)
    
    # Should raise ValueError with invalid inputs
    with pytest.raises(ValueError):
        rkhs.compute([1, 2], "invalid")


@pytest.mark.unit
def test_default_rbf_kernel_directly():
    """Test the default RBF kernel function directly."""
    rkhs = RKHSReproducing()
    
    # Test with various inputs
    assert np.isclose(rkhs._default_rbf_kernel([0, 0], [0, 0]), 1.0)
    assert np.isclose(rkhs._default_rbf_kernel([1, 0], [0