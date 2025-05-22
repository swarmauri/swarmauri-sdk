import logging
from unittest.mock import MagicMock, Mock

import numpy as np
import pytest
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.vectors.IVector import IVector

from swarmauri_standard.norms.L1ManhattanNorm import L1ManhattanNorm

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Fixtures for common test objects
@pytest.fixture
def l1_norm():
    """
    Fixture that provides an L1ManhattanNorm instance.

    Returns
    -------
    L1ManhattanNorm
        An instance of the L1ManhattanNorm class.
    """
    return L1ManhattanNorm()


@pytest.fixture
def mock_vector():
    """
    Fixture that provides a mock IVector.

    Returns
    -------
    MagicMock
        A mock object that simulates an IVector.
    """
    mock = MagicMock(spec=IVector)
    mock.values = [1.0, -2.0, 3.0, -4.0]
    return mock


@pytest.fixture
def mock_matrix():
    """
    Fixture providing a mock IMatrix for testing.
    """
    mock = MagicMock(spec=IMatrix)
    mock.values = [[1, 2], [3, 4]]
    mock.to_array = Mock(return_value=np.array([[1, 2], [3, 4]]))
    return mock


# Test cases
@pytest.mark.unit
def test_instantiation():
    """Test that L1ManhattanNorm can be instantiated correctly."""
    norm = L1ManhattanNorm()
    assert norm.type == "L1ManhattanNorm"
    assert norm.resource == "Norm"


@pytest.mark.unit
def test_serialization(l1_norm):
    """Test serialization and deserialization of L1ManhattanNorm."""
    json_data = l1_norm.model_dump_json()
    deserialized = L1ManhattanNorm.model_validate_json(json_data)

    assert deserialized.type == l1_norm.type
    assert deserialized.resource == l1_norm.resource


@pytest.mark.unit
@pytest.mark.parametrize(
    "input_data,expected_norm",
    [
        ([1, 2, 3, 4], 10.0),
        ([1.0, -2.0, 3.0, -4.0], 10.0),
        ([-5, -10, -15], 30.0),
        ([0, 0, 0], 0.0),
        (np.array([1, -2, 3, -4]), 10.0),
    ],
)
def test_compute_with_sequences(l1_norm, input_data, expected_norm):
    """Test computing L1 norm with various sequence types."""
    result = l1_norm.compute(input_data)
    assert result == expected_norm
    assert isinstance(result, float)


@pytest.mark.unit
def test_compute_with_vector(l1_norm, mock_vector):
    """Test computing L1 norm with an IVector object."""
    result = l1_norm.compute(mock_vector)
    assert result == 10.0
    assert isinstance(result, float)


@pytest.mark.unit
def test_compute_with_matrix(l1_norm, mock_matrix):
    """Test computing L1 norm with an IMatrix object."""
    result = l1_norm.compute(mock_matrix)
    assert result == 10.0
    assert isinstance(result, float)


@pytest.mark.unit
def test_compute_with_unsupported_type(l1_norm):
    """Test that computing L1 norm with unsupported types raises TypeError."""
    with pytest.raises(TypeError):
        l1_norm.compute("not a valid input")


@pytest.mark.unit
def test_compute_with_invalid_sequence(l1_norm):
    """Test that computing L1 norm with non-numeric sequence raises TypeError."""
    with pytest.raises(TypeError):
        l1_norm.compute(["a", "b", "c"])


@pytest.mark.unit
@pytest.mark.parametrize(
    "input_data",
    [
        [1, 2, 3, 4],
        [1.0, -2.0, 3.0, -4.0],
        [-5, -10, -15],
        [0, 0, 0],
        np.array([1, -2, 3, -4]),
    ],
)
def test_non_negativity(l1_norm, input_data):
    """Test that L1 norm satisfies the non-negativity property."""
    assert l1_norm.check_non_negativity(input_data) is True


@pytest.mark.unit
@pytest.mark.parametrize(
    "input_data,expected_result",
    [
        ([0, 0, 0], True),  # Zero vector
        ([1, 0, 0], True),  # Non-zero vector
        ([1, -2, 3], True),  # Mixed vector
    ],
)
def test_definiteness(l1_norm, input_data, expected_result):
    """Test that L1 norm satisfies the definiteness property."""
    assert l1_norm.check_definiteness(input_data) is expected_result


@pytest.mark.unit
@pytest.mark.parametrize(
    "x,y",
    [
        ([1, 2, 3], [4, 5, 6]),
        ([1.0, -2.0, 3.0], [-1.0, 2.0, -3.0]),
        ([0, 0, 0], [0, 0, 0]),
        (np.array([1, 2, 3]), np.array([4, 5, 6])),
    ],
)
def test_triangle_inequality(l1_norm, x, y):
    """Test that L1 norm satisfies the triangle inequality."""
    assert l1_norm.check_triangle_inequality(x, y) is True


@pytest.mark.unit
def test_triangle_inequality_incompatible_inputs(l1_norm):
    """Test that triangle inequality check raises TypeError for incompatible inputs."""
    with pytest.raises(TypeError):
        l1_norm.check_triangle_inequality([1, 2, 3], [4, 5])


@pytest.mark.unit
@pytest.mark.parametrize(
    "input_data,scalar",
    [
        ([1, 2, 3], 2.0),
        ([1.0, -2.0, 3.0], -3.0),
        ([0, 0, 0], 5.0),
        (np.array([1, 2, 3]), 2.5),
    ],
)
def test_absolute_homogeneity(l1_norm, input_data, scalar):
    """Test that L1 norm satisfies the absolute homogeneity property."""
    assert l1_norm.check_absolute_homogeneity(input_data, scalar) is True


@pytest.mark.unit
def test_absolute_homogeneity_unsupported_type(l1_norm):
    """Test that absolute homogeneity check raises TypeError for unsupported types."""
    with pytest.raises(TypeError):
        l1_norm.check_absolute_homogeneity("not a valid input", 2.0)


@pytest.mark.unit
@pytest.mark.parametrize(
    "input_data,expected_result",
    [
        ([0, 0, 0], True),
        ([1, 0, 0], False),
        ([0.0, 0.0, 0.0], True),
        (np.zeros(3), True),
        (np.ones(3), False),
    ],
)
def test_is_zero(l1_norm, input_data, expected_result):
    """Test the internal _is_zero method."""
    assert l1_norm._is_zero(input_data) == expected_result


@pytest.mark.unit
def test_is_zero_unsupported_type(l1_norm):
    """Test that _is_zero raises TypeError for unsupported types."""
    with pytest.raises(TypeError):
        l1_norm._is_zero("not a valid input")


@pytest.mark.unit
@pytest.mark.parametrize(
    "x,y,expected_result",
    [
        ([1, 2, 3], [4, 5, 6], True),
        ([1, 2, 3], [4, 5], False),
        (np.array([1, 2, 3]), np.array([4, 5, 6]), True),
        (np.array([1, 2, 3]), np.array([4, 5]), False),
    ],
)
def test_are_compatible(l1_norm, x, y, expected_result):
    """Test the internal _are_compatible method."""
    assert l1_norm._are_compatible(x, y) is expected_result


@pytest.mark.unit
def test_add(l1_norm):
    """Test the internal _add method."""
    x = [1, 2, 3]
    y = [4, 5, 6]
    result = l1_norm._add(x, y)
    assert result == [5.0, 7.0, 9.0]


@pytest.mark.unit
def test_add_numpy(l1_norm):
    """Test the internal _add method with numpy arrays."""
    x = np.array([1, 2, 3])
    y = np.array([4, 5, 6])
    result = l1_norm._add(x, y)
    np.testing.assert_array_equal(result, np.array([5, 7, 9]))


@pytest.mark.unit
def test_add_unsupported_type(l1_norm):
    """Test that _add raises TypeError for unsupported types."""
    with pytest.raises(TypeError):
        l1_norm._add("not a valid input", "another invalid input")


@pytest.mark.unit
def test_scale(l1_norm):
    """Test the internal _scale method."""
    x = [1, 2, 3]
    scalar = 2.0
    result = l1_norm._scale(x, scalar)
    assert result == [2.0, 4.0, 6.0]


@pytest.mark.unit
def test_scale_numpy(l1_norm):
    """Test the internal _scale method with numpy arrays."""
    x = np.array([1, 2, 3])
    scalar = 2.0
    result = l1_norm._scale(x, scalar)
    np.testing.assert_array_equal(result, np.array([2, 4, 6]))


@pytest.mark.unit
def test_scale_unsupported_type(l1_norm):
    """Test that _scale raises TypeError for unsupported types."""
    with pytest.raises(TypeError):
        l1_norm._scale("not a valid input", 2.0)


@pytest.mark.unit
def test_vector_operations(l1_norm, mock_vector):
    """Test vector operations with IVector objects."""
    # Test non-negativity
    assert l1_norm.check_non_negativity(mock_vector) is True

    # Test definiteness
    mock_vector.values = [0.0, 0.0, 0.0, 0.0]
    assert l1_norm.check_definiteness(mock_vector) is True

    mock_vector.values = [1.0, -2.0, 3.0, -4.0]
    assert l1_norm.check_definiteness(mock_vector) is True


@pytest.mark.unit
def test_matrix_operations(l1_norm, mock_matrix):
    """Test matrix operations with IMatrix objects."""
    # Test non-negativity
    assert l1_norm.check_non_negativity(mock_matrix) is True

    # Test definiteness
    mock_matrix.values = [[0.0, 0.0], [0.0, 0.0]]
    assert l1_norm.check_definiteness(mock_matrix) is True

    mock_matrix.values = [[1.0, -2.0], [3.0, -4.0]]
    assert l1_norm.check_definiteness(mock_matrix) is True
