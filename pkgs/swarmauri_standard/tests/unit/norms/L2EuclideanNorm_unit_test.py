import logging
import math
from unittest.mock import MagicMock

import pytest
from swarmauri_core.matrices.IMatrix import IMatrix

from swarmauri_standard.norms.L2EuclideanNorm import L2EuclideanNorm
from swarmauri_standard.vectors.Vector import Vector

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def l2_norm() -> L2EuclideanNorm:
    """
    Fixture that provides an L2EuclideanNorm instance.

    Returns
    -------
    L2EuclideanNorm
        An instance of the L2EuclideanNorm class.
    """
    return L2EuclideanNorm()


@pytest.fixture
def real_vector() -> Vector:
    """
    Fixture that provides a real Vector instance.

    Returns
    -------
    Vector
        A concrete Vector instance with values [3, 4].
    """
    return Vector(value=[3, 4])


@pytest.fixture
def mock_matrix() -> IMatrix:
    """
    Fixture that provides a mock IMatrix instance.

    Returns
    -------
    IMatrix
        A mock matrix that behaves like an IMatrix.
    """
    matrix = MagicMock(spec=IMatrix)
    matrix.__iter__.return_value = iter([[1, 2], [3, 4]])
    matrix.__getitem__.side_effect = lambda i: [[1, 2], [3, 4]][i]
    matrix.shape = (2, 2)
    return matrix


@pytest.mark.unit
def test_l2_norm_attributes(l2_norm):
    """Test the basic attributes of the L2EuclideanNorm class."""
    assert l2_norm.type == "L2EuclideanNorm"
    assert l2_norm.resource == "Norm"


@pytest.mark.unit
def test_compute_with_list(l2_norm):
    """Test L2EuclideanNorm.compute with a list input."""
    # Test with a simple list [3, 4], which should have L2 norm = 5
    result = l2_norm.compute([3, 4])
    assert result == 5.0

    # Test with zero vector
    result = l2_norm.compute([0, 0, 0])
    assert result == 0.0

    # Test with another vector
    result = l2_norm.compute([1, 2, 3])
    assert math.isclose(result, math.sqrt(14), rel_tol=1e-10)


@pytest.mark.unit
def test_compute_with_vector(l2_norm, real_vector):
    """Test L2EuclideanNorm.compute with an IVector input."""
    result = l2_norm.compute(real_vector)
    assert result == 5.0


@pytest.mark.unit
def test_compute_with_matrix(l2_norm, mock_matrix):
    """Test L2EuclideanNorm.compute with an IMatrix input."""
    result = l2_norm.compute(mock_matrix)
    # For matrix [[1, 2], [3, 4]], the L2 norm should be sqrt(1^2 + 2^2 + 3^2 + 4^2) = sqrt(30)
    assert math.isclose(result, math.sqrt(30), rel_tol=1e-10)


@pytest.mark.unit
def test_compute_with_string(l2_norm):
    """Test L2EuclideanNorm.compute with a string input."""
    # For string "abc", the L2 norm is sqrt(97^2 + 98^2 + 99^2) where 97, 98, 99 are ASCII values
    result = l2_norm.compute("abc")
    expected = math.sqrt(sum(ord(c) ** 2 for c in "abc"))
    assert math.isclose(result, expected, rel_tol=1e-10)

    # Test with empty string
    result = l2_norm.compute("")
    assert result == 0.0


@pytest.mark.unit
def test_compute_with_invalid_input(l2_norm):
    """Test L2EuclideanNorm.compute with invalid inputs."""
    # Test with a function (should raise TypeError)
    with pytest.raises(TypeError):
        l2_norm.compute(lambda x: x)

    # Test with an integer (should raise TypeError)
    with pytest.raises(TypeError):
        l2_norm.compute(42)


@pytest.mark.unit
def test_compute_with_invalid_sequence(l2_norm):
    """Test L2EuclideanNorm.compute with a sequence containing non-numeric elements."""
    with pytest.raises(ValueError):
        l2_norm.compute(["a", "b", "c"])


@pytest.mark.unit
@pytest.mark.parametrize(
    "input_val",
    [
        [3, 4],
        (1, 2, 3),
        "hello",
    ],
)
def test_check_non_negativity(l2_norm, input_val):
    """Test L2EuclideanNorm.check_non_negativity with various inputs."""
    assert l2_norm.check_non_negativity(input_val) is True


@pytest.mark.unit
@pytest.mark.parametrize(
    "input_val, expected",
    [
        ([0, 0, 0], True),  # Zero vector should return True
        ([1, 0, 0], True),  # Non-zero vector should return True
        ("", True),  # Empty string should return True
        ("a", True),  # Non-empty string should return True
    ],
)
def test_check_definiteness(l2_norm, input_val, expected):
    """Test L2EuclideanNorm.check_definiteness with various inputs."""
    assert l2_norm.check_definiteness(input_val) is expected


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y",
    [
        ([1, 2], [3, 4]),
        ([0, 0], [0, 0]),
        ([5, 12], [-5, -12]),
    ],
)
def test_check_triangle_inequality(l2_norm, x, y):
    """Test L2EuclideanNorm.check_triangle_inequality with various inputs."""
    assert l2_norm.check_triangle_inequality(x, y) is True


@pytest.mark.unit
def test_check_triangle_inequality_with_mismatched_types(l2_norm):
    """Test L2EuclideanNorm.check_triangle_inequality with mismatched input types."""
    with pytest.raises(TypeError):
        l2_norm.check_triangle_inequality([1, 2], "string")


@pytest.mark.unit
def test_check_triangle_inequality_with_mismatched_dimensions(l2_norm):
    """Test L2EuclideanNorm.check_triangle_inequality with mismatched dimensions."""
    with pytest.raises(ValueError):
        l2_norm.check_triangle_inequality([1, 2], [3, 4, 5])


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, scalar",
    [
        ([1, 2, 3], 2),
        ([1, 2, 3], -2),
        ([1, 2, 3], 0),
        ([0, 0, 0], 5),
    ],
)
def test_check_absolute_homogeneity(l2_norm, x, scalar):
    """Test L2EuclideanNorm.check_absolute_homogeneity with various inputs."""
    assert l2_norm.check_absolute_homogeneity(x, scalar) is True


@pytest.mark.unit
def test_check_absolute_homogeneity_with_string(l2_norm):
    """Test L2EuclideanNorm.check_absolute_homogeneity with string input."""
    # Homogeneity property doesn't hold for strings in the typical vector sense
    assert l2_norm.check_absolute_homogeneity("abc", 3) is False

    # Test with invalid scalar for string
    with pytest.raises(TypeError):
        l2_norm.check_absolute_homogeneity("abc", -1)


@pytest.mark.unit
def test_serialization(l2_norm):
    """Test serialization and deserialization of L2EuclideanNorm."""
    # Serialize to JSON
    json_data = l2_norm.model_dump_json()

    # Deserialize from JSON
    deserialized_norm = L2EuclideanNorm.model_validate_json(json_data)

    # Check that the deserialized object has the same attributes
    assert deserialized_norm.type == l2_norm.type
    assert deserialized_norm.resource == l2_norm.resource
