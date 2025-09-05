import logging
from unittest.mock import MagicMock, Mock

import numpy as np
import pytest
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.vectors.IVector import IVector

from swarmauri_standard.norms.GeneralLpNorm import GeneralLpNorm

# Configure logging
logger = logging.getLogger(__name__)


# Mock classes for testing
class MockVector(IVector):
    def __init__(self, data):
        self.data = np.array(data)

    def to_array(self):
        return self.data

    def __len__(self):
        return len(self.data)


# Fixtures
@pytest.fixture
def simple_vector():
    return [3, 4]


@pytest.fixture
def mock_vector():
    return MockVector([3, 4])


@pytest.fixture
def mock_matrix():
    """Fixture providing a mock matrix for testing."""
    mock = MagicMock(spec=IMatrix)
    mock.to_array = Mock(return_value=np.array([[1, 2], [3, 4]]))
    return mock


@pytest.fixture
def norm_p2():
    return GeneralLpNorm(p=2)


@pytest.fixture
def norm_p3():
    return GeneralLpNorm(p=3)


# Test cases
@pytest.mark.unit
def test_initialization():
    """Test that GeneralLpNorm initializes correctly."""
    norm = GeneralLpNorm(p=2)
    assert norm.p == 2
    assert norm.type == "GeneralLpNorm"


@pytest.mark.unit
def test_invalid_p_values():
    """Test that invalid p values raise ValueError."""
    with pytest.raises(ValueError):
        GeneralLpNorm(p=1)  # p must be > 1

    with pytest.raises(ValueError):
        GeneralLpNorm(p=0)  # p must be > 1

    with pytest.raises(ValueError):
        GeneralLpNorm(p=-2)  # p must be > 1


@pytest.mark.unit
@pytest.mark.parametrize(
    "p,vector,expected",
    [
        (2, [3, 4], 5.0),  # Euclidean norm of [3, 4] is 5
        (3, [3, 4], (3**3 + 4**3) ** (1 / 3)),
        (2, [1, 2, 3], (1**2 + 2**2 + 3**2) ** (1 / 2)),
    ],
)
def test_compute_with_list(p, vector, expected):
    """Test compute method with list input."""
    norm = GeneralLpNorm(p=p)
    result = norm.compute(vector)
    assert np.isclose(result, expected)


@pytest.mark.unit
def test_compute_with_mock_vector(norm_p2, mock_vector):
    """Test compute method with IVector implementation."""
    result = norm_p2.compute(mock_vector)
    expected = 5.0  # Euclidean norm of [3, 4]
    assert np.isclose(result, expected)


@pytest.mark.unit
def test_compute_with_mock_matrix(norm_p2, mock_matrix):
    """Test compute method with IMatrix implementation."""
    result = norm_p2.compute(mock_matrix)
    # Norm of flattened matrix [1, 2, 3, 4]
    expected = (1**2 + 2**2 + 3**2 + 4**2) ** (1 / 2)
    assert np.isclose(result, expected)


@pytest.mark.unit
def test_compute_with_string():
    """Test compute method with string input."""
    norm = GeneralLpNorm(p=2)
    result = norm.compute("AB")
    # ASCII: 'A' = 65, 'B' = 66
    expected = (65**2 + 66**2) ** (1 / 2)
    assert np.isclose(result, expected)


@pytest.mark.unit
def test_compute_with_callable():
    """Test compute method with callable input."""
    norm = GeneralLpNorm(p=2)

    def func(x):
        return x**2

    result = norm.compute(func)
    # This is an approximation since we're sampling the function
    assert result > 0


@pytest.mark.unit
def test_non_negativity(norm_p2, simple_vector):
    """Test non-negativity property of the norm."""
    assert norm_p2.check_non_negativity(simple_vector)


@pytest.mark.unit
def test_definiteness(norm_p2):
    """Test definiteness property of the norm."""
    # Zero vector should have zero norm
    assert norm_p2.check_definiteness([0, 0, 0])

    # Non-zero vector should have non-zero norm
    assert norm_p2.check_definiteness([1, 2, 3])


@pytest.mark.unit
def test_triangle_inequality(norm_p2):
    """Test triangle inequality property of the norm."""
    x = [1, 2, 3]
    y = [4, 5, 6]
    assert norm_p2.check_triangle_inequality(x, y)


@pytest.mark.unit
def test_absolute_homogeneity(norm_p2, simple_vector):
    """Test absolute homogeneity property of the norm."""
    assert norm_p2.check_absolute_homogeneity(simple_vector, 2.5)
    assert norm_p2.check_absolute_homogeneity(simple_vector, -3.7)


@pytest.mark.unit
def test_different_p_values():
    """Test that different p values give different results."""
    vector = [3, 4]
    norm_p2 = GeneralLpNorm(p=2)
    norm_p3 = GeneralLpNorm(p=3)

    result_p2 = norm_p2.compute(vector)
    result_p3 = norm_p3.compute(vector)

    assert not np.isclose(result_p2, result_p3)
    assert np.isclose(result_p2, 5.0)
    assert np.isclose(result_p3, (3**3 + 4**3) ** (1 / 3))


@pytest.mark.unit
def test_error_handling_incompatible_shapes():
    """Test error handling when shapes are incompatible."""
    norm = GeneralLpNorm(p=2)
    x = [1, 2]
    y = [1, 2, 3]

    assert norm.check_triangle_inequality(x, y) is False


@pytest.mark.unit
def test_serialization():
    """Test that GeneralLpNorm can be serialized and deserialized."""
    norm = GeneralLpNorm(p=2.5)
    json_str = norm.model_dump_json()
    deserialized = GeneralLpNorm.model_validate_json(json_str)

    assert deserialized.p == norm.p
    assert deserialized.type == norm.type


@pytest.mark.unit
def test_large_vectors():
    """Test with large vectors to ensure computational stability."""
    norm = GeneralLpNorm(p=2)
    large_vector = list(range(1000))
    result = norm.compute(large_vector)
    assert result > 0
    assert np.isfinite(result)


@pytest.mark.unit
def test_very_large_p():
    """Test with a very large p value."""
    large_p = 100
    norm = GeneralLpNorm(p=large_p)
    vector = [3, 4]
    result = norm.compute(vector)
    # As p approaches infinity, the Lp norm approaches max(|x_i|)
    assert np.isclose(result, 4.0, atol=0.1)
