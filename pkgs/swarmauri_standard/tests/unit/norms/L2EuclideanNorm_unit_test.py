import pytest
import logging
from swarmauri_standard.norms.L2EuclideanNorm import L2EuclideanNorm

logger = logging.getLogger(__name__)

@pytest.mark.unit
class TestL2EuclideanNorm:
    """Unit tests for the L2EuclideanNorm class."""
    
    def test_compute_vector(self, vector_input):
        """Test L2 norm computation for vector inputs."""
        norm = L2EuclideanNorm()
        result = norm.compute(vector_input)
        expected = sum(x**2 for x in vector_input.to_list())**0.5
        assert result == pytest.approx(expected)
        
    def test_compute_matrix(self, matrix_input):
        """Test L2 norm computation for matrix inputs."""
        norm = L2EuclideanNorm()
        elements = matrix_input.to_list()
        flat_elements = [num for row in elements for num in row]
        expected = sum(x**2 for x in flat_elements) ** 0.5
        result = norm.compute(matrix_input)
        assert result == pytest.approx(expected)
        
    def test_compute_sequence(self, sequence_input):
        """Test L2 norm computation for sequence inputs."""
        norm = L2EuclideanNorm()
        result = norm.compute(sequence_input)
        expected = sum(x**2 for x in sequence_input)**0.5
        assert result == pytest.approx(expected)
        
    def test_compute_string(self, string_input):
        """Test L2 norm computation for string inputs."""
        norm = L2EuclideanNorm()
        ord_values = [ord(c) for c in string_input]
        expected = sum(x**2 for x in ord_values) ** 0.5
        result = norm.compute(string_input)
        assert result == pytest.approx(expected)
        
    def test_compute_callable(self, callable_input):
        """Test L2 norm computation for callable inputs."""
        norm = L2EuclideanNorm()
        result = norm.compute(callable_input)
        # Assuming callable returns a vector-like object
        elements = callable_input().to_list()
        expected = sum(x**2 for x in elements) ** 0.5
        assert result == pytest.approx(expected)
        
    def test_zero_vector(self):
        """Test L2 norm computation for a zero vector."""
        norm = L2EuclideanNorm()
        zero_vector = [0, 0, 0]
        result = norm.compute(zero_vector)
        assert result == 0.0
        
    def test_empty_string(self):
        """Test L2 norm computation for an empty string."""
        norm = L2EuclideanNorm()
        result = norm.compute("")
        assert result == 0.0
        
    def test_callable_empty(self, callable_empty_input):
        """Test L2 norm computation for a callable that returns an empty vector."""
        norm = L2EuclideanNorm()
        result = norm.compute(callable_empty_input)
        assert result == 0.0

@pytest.fixture
def vector_input():
    """Fixture providing test vectors."""
    from swarmauri_core.vectors import Vector
    vectors = [
        Vector([3, 4]),  # Expected norm: 5.0
        Vector([-1, 2, 3]),  # Expected norm: sqrt(1+4+9)=sqrt(14)
        Vector([0, 0, 0]),  # Expected norm: 0.0
    ]
    return vectors

@pytest.fixture
def matrix_input():
    """Fixture providing test matrices."""
    from swarmauri_core.matrices import Matrix
    matrices = [
        Matrix([[1, 2], [3, 4]]),  # Expected norm: sqrt(1+4+9+16)=sqrt(30)
        Matrix([[0, 0], [0, 0]]),  # Expected norm: 0.0
    ]
    return matrices

@pytest.fixture
def sequence_input():
    """Fixture providing test sequences."""
    sequences = [
        [3, 4],  # Expected norm: 5.0
        (-1, 2, 3),  # Expected norm: sqrt(1+4+9)=sqrt(14)
        [],  # Expected norm: 0.0
    ]
    return sequences

@pytest.fixture
def string_input():
    """Fixture providing test strings."""
    strings = [
        "test",  # ASCII values: 116, 101, 115, 116
        "",  # Empty string
    ]
    return strings

@pytest.fixture
def callable_input():
    """Fixture providing test callables."""
    def vector_callable():
        from swarmauri_core.vectors import Vector
        return Vector([1, 2, 3])
        
    def matrix_callable():
        from swarmauri_core.matrices import Matrix
        return Matrix([[4, 5], [6, 7]])
        
    def sequence_callable():
        return [8, 9, 10]
        
    callables = [vector_callable, matrix_callable, sequence_callable]
    return callables

@pytest.fixture
def callable_empty_input():
    """Fixture providing callables that return empty vectors."""
    def empty_vector_callable():
        from swarmauri_core.vectors import Vector
        return Vector([])
        
    def empty_matrix_callable():
        from swarmauri_core.matrices import Matrix
        return Matrix([])
        
    def empty_sequence_callable():
        return []
        
    callables = [empty_vector_callable, empty_matrix_callable, empty_sequence_callable]
    return callables