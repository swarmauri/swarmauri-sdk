import logging

import numpy as np
import pytest
from swarmauri_base.norms.NormBase import NormBase
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.vectors.IVector import IVector

from swarmauri_standard.norms.LInfNorm import LInfNorm

# Configure logging
logger = logging.getLogger(__name__)


# Mock classes for testing
class MockVector(IVector):
    def __init__(self, data):
        self.data = data

    @property
    def dimension(self) -> int:
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]

    def __len__(self):
        return len(self.data)


class MockMatrix(IMatrix):
    def __init__(self, data):
        self.data = np.array(data)

    def to_array(self):
        return self.data

    # Add required methods
    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __add__(self, other):
        return MockMatrix(self.data + getattr(other, "data", other))

    def __array__(self):
        return self.data

    def __eq__(self, other):
        return np.array_equal(self.data, getattr(other, "data", other))

    def __iter__(self):
        return iter([self.data[i] for i in range(len(self.data))])

    def __matmul__(self, other):
        return MockMatrix(self.data @ getattr(other, "data", other))

    def __mul__(self, other):
        return MockMatrix(self.data * getattr(other, "data", other))

    def __neg__(self):
        return MockMatrix(-self.data)

    def __sub__(self, other):
        return MockMatrix(self.data - getattr(other, "data", other))

    def __truediv__(self, other):
        return MockMatrix(self.data / getattr(other, "data", other))

    def column(self, idx):
        return self.data[:, idx]

    def row(self, idx):
        return self.data[idx, :]

    def reshape(self, shape):
        return MockMatrix(self.data.reshape(shape))

    def tolist(self):
        return self.data.tolist()

    def transpose(self):
        return MockMatrix(self.data.T)

    @property
    def shape(self):
        return self.data.shape

    @property
    def dtype(self):
        return self.data.dtype


@pytest.fixture
def linf_norm():
    """Fixture to create a LInfNorm instance."""
    return LInfNorm()


@pytest.fixture
def test_vector():
    """Fixture to create a test vector."""
    return MockVector([-3, 1, 4, -5, 2])


@pytest.fixture
def test_matrix():
    """Fixture to create a test matrix."""
    return MockMatrix([[-3, 1], [4, -5], [2, 0]])


@pytest.fixture
def test_sequence():
    """Fixture to create a test sequence."""
    return [-3, 1, 4, -5, 2]


@pytest.fixture
def test_function():
    """Fixture to create a test function."""
    return lambda x: x**2 - 2 * x + 3


@pytest.mark.unit
def test_inheritance():
    """Test that LInfNorm inherits from NormBase."""
    assert issubclass(LInfNorm, NormBase)


@pytest.mark.unit
def test_instantiation():
    """Test that LInfNorm can be instantiated."""
    norm = LInfNorm()
    assert isinstance(norm, LInfNorm)
    assert norm.type == "LInfNorm"
    assert norm.resource == "Norm"
    assert norm.domain_bounds == (-1, 1)


@pytest.mark.unit
def test_custom_domain_bounds():
    """Test that LInfNorm can be instantiated with custom domain bounds."""
    norm = LInfNorm(domain_bounds=(-10, 10))
    assert norm.domain_bounds == (-10, 10)


@pytest.mark.unit
def test_invalid_domain_bounds():
    """Test that LInfNorm raises an error for invalid domain bounds."""
    with pytest.raises(ValueError):
        LInfNorm(domain_bounds=(1, -1))  # min > max

    with pytest.raises(ValueError):
        LInfNorm(domain_bounds=(1, 1))  # min == max


@pytest.mark.unit
def test_compute_vector(linf_norm, test_vector):
    """Test computing L-infinity norm for a vector."""
    result = linf_norm.compute(test_vector)
    assert result == 5.0  # Max absolute value is 5


@pytest.mark.unit
def test_compute_matrix(linf_norm, test_matrix):
    """Test computing L-infinity norm for a matrix."""
    result = linf_norm.compute(test_matrix)
    assert result == 5.0  # Max absolute value is 5


@pytest.mark.unit
def test_compute_sequence(linf_norm, test_sequence):
    """Test computing L-infinity norm for a sequence."""
    result = linf_norm.compute(test_sequence)
    assert result == 5.0  # Max absolute value is 5


@pytest.mark.unit
def test_compute_string(linf_norm):
    """Test computing L-infinity norm for a string."""
    result = linf_norm.compute("abc")
    assert result == 99  # ASCII value of 'c' is the largest


@pytest.mark.unit
def test_compute_function(linf_norm, test_function):
    """Test computing L-infinity norm for a function."""
    # Function x^2 - 2x + 3 on domain [-1, 1]
    # Maximum absolute value should be at x = -1: (-1)^2 - 2*(-1) + 3 = 1 + 2 + 3 = 6
    result = linf_norm.compute(test_function)
    assert abs(result - 6.0) < 0.1  # Allow for numerical approximation


@pytest.mark.unit
def test_compute_empty_sequence(linf_norm):
    """Test that computing L-infinity norm for an empty sequence raises an error."""
    with pytest.raises(ValueError):
        linf_norm.compute([])


@pytest.mark.unit
def test_compute_unsupported_type(linf_norm):
    """Test that computing L-infinity norm for an unsupported type raises an error."""
    with pytest.raises(TypeError):
        linf_norm.compute(42)  # Single integer is not supported


@pytest.mark.unit
def test_non_negativity(
    linf_norm, test_vector, test_matrix, test_sequence, test_function
):
    """Test the non-negativity property of the L-infinity norm."""
    assert linf_norm.check_non_negativity(test_vector)
    assert linf_norm.check_non_negativity(test_matrix)
    assert linf_norm.check_non_negativity(test_sequence)
    assert linf_norm.check_non_negativity("abc")
    assert linf_norm.check_non_negativity(test_function)


@pytest.mark.unit
def test_definiteness(linf_norm):
    """Test the definiteness property of the L-infinity norm."""
    # Zero vector, matrix, sequence, and function
    zero_vector = MockVector([0, 0, 0])
    zero_matrix = MockMatrix([[0, 0], [0, 0]])
    zero_sequence = [0, 0, 0]

    def zero_function(x):
        return 0

    assert linf_norm.check_definiteness(zero_vector)
    assert linf_norm.check_definiteness(zero_matrix)
    assert linf_norm.check_definiteness(zero_sequence)
    assert linf_norm.check_definiteness(zero_function)

    # Non-zero vector, matrix, sequence, and function
    non_zero_vector = MockVector([0, 1, 0])
    non_zero_matrix = MockMatrix([[0, 1], [0, 0]])
    non_zero_sequence = [0, 1, 0]

    def non_zero_function(x):
        return x

    assert linf_norm.check_definiteness(non_zero_vector)
    assert linf_norm.check_definiteness(non_zero_matrix)
    assert linf_norm.check_definiteness(non_zero_sequence)
    assert linf_norm.check_definiteness(non_zero_function)


@pytest.mark.unit
def test_triangle_inequality(linf_norm):
    """Test the triangle inequality property of the L-infinity norm."""
    # Test vectors
    vector_a = MockVector([1, -2, 3])
    vector_b = MockVector([2, 1, -1])
    assert linf_norm.check_triangle_inequality(vector_a, vector_b)

    # Test matrices
    matrix_a = MockMatrix([[1, -2], [3, 0]])
    matrix_b = MockMatrix([[2, 1], [-1, 2]])
    assert linf_norm.check_triangle_inequality(matrix_a, matrix_b)

    # Test sequences
    sequence_a = [1, -2, 3]
    sequence_b = [2, 1, -1]
    assert linf_norm.check_triangle_inequality(sequence_a, sequence_b)

    # Test strings
    string_a = "abc"
    string_b = "defr"
    with pytest.raises(ValueError):  # Different length strings should raise error
        linf_norm.check_triangle_inequality(string_a, string_b)

    # Test functions
    def function_a(x):
        return x**2

    def function_b(x):
        return 2 * x

    assert linf_norm.check_triangle_inequality(function_a, function_b)


@pytest.mark.unit
def test_absolute_homogeneity(linf_norm):
    """Test the absolute homogeneity property of the L-infinity norm."""
    # Test vector
    vector = MockVector([1, -2, 3])
    assert linf_norm.check_absolute_homogeneity(vector, 2.0)
    assert linf_norm.check_absolute_homogeneity(vector, -0.5)

    # Test matrix
    matrix = MockMatrix([[1, -2], [3, 0]])
    assert linf_norm.check_absolute_homogeneity(matrix, 2.0)
    assert linf_norm.check_absolute_homogeneity(matrix, -0.5)

    # Test sequence
    sequence = [1, -2, 3]
    assert linf_norm.check_absolute_homogeneity(sequence, 2.0)
    assert linf_norm.check_absolute_homogeneity(sequence, -0.5)

    # Test function
    def function(x):
        return x**2

    assert linf_norm.check_absolute_homogeneity(function, 2.0)
    assert linf_norm.check_absolute_homogeneity(function, -0.5)


@pytest.mark.unit
def test_serialization():
    """Test serialization and deserialization of LInfNorm."""
    original_norm = LInfNorm(domain_bounds=(-5, 5))
    serialized = original_norm.model_dump_json()
    deserialized = LInfNorm.model_validate_json(serialized)

    assert deserialized.type == original_norm.type
    assert deserialized.resource == original_norm.resource
    assert deserialized.domain_bounds == original_norm.domain_bounds


@pytest.mark.unit
@pytest.mark.parametrize(
    "input_data,expected_result",
    [
        ([-3, 1, 4, -5, 2], 5.0),
        ([0, 0, 0], 0.0),
        ([10], 10.0),
        ([-7, -2, -9], 9.0),
    ],
)
def test_compute_parametrized(linf_norm, input_data, expected_result):
    """Parameterized test for computing L-infinity norm with various inputs."""
    assert linf_norm.compute(input_data) == expected_result
