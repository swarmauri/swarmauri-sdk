import logging

import numpy as np
import pytest
from swarmauri_core.vectors.IVector import IVector

from swarmauri_standard.seminorms.PointEvaluationSeminorm import PointEvaluationSeminorm

# Configure logging
logger = logging.getLogger(__name__)


@pytest.fixture
def point_evaluation_seminorm():
    """
    Fixture that provides a basic PointEvaluationSeminorm instance for testing.

    Returns
    -------
    PointEvaluationSeminorm
        An instance of PointEvaluationSeminorm with point=0 and absolute=True
    """
    return PointEvaluationSeminorm(point=0, absolute=True)


@pytest.fixture
def sample_function():
    """
    Fixture that provides a sample function for testing.

    Returns
    -------
    Callable
        A function that returns the square of its input
    """

    def func(x):
        return x * x

    return func


@pytest.fixture
def sample_vector():
    """
    Fixture that provides a sample vector for testing.

    Returns
    -------
    list
        A list representing a vector [1, 2, 3, 4, 5]
    """
    return [1, 2, 3, 4, 5]


@pytest.fixture
def sample_dict():
    """
    Fixture that provides a sample dictionary for testing.

    Returns
    -------
    Dict
        A dictionary with various key types
    """
    return {0: 5, 1: 10, 2: 15, "key": 20}


class MockVector(IVector):
    """Mock implementation of IVector for testing purposes."""

    def __init__(self, data):
        self.data = data

    def __getitem__(self, idx):
        return self.data[idx]

    def __add__(self, other):
        if isinstance(other, MockVector):
            return MockVector([a + b for a, b in zip(self.data, other.data)])
        return NotImplemented

    def __mul__(self, scalar):
        return MockVector([item * scalar for item in self.data])


@pytest.fixture
def mock_vector():
    """
    Fixture that provides a mock vector implementing IVector.

    Returns
    -------
    MockVector
        A mock vector with data [1, 2, 3, 4, 5]
    """
    return MockVector([1, 2, 3, 4, 5])


@pytest.mark.unit
def test_initialization():
    """Test that the PointEvaluationSeminorm initializes correctly."""
    # Test with different point types
    seminorm1 = PointEvaluationSeminorm(point=0)
    assert seminorm1.point == 0
    assert seminorm1.absolute is True

    seminorm2 = PointEvaluationSeminorm(point="key", absolute=False)
    assert seminorm2.point == "key"
    assert seminorm2.absolute is False

    seminorm3 = PointEvaluationSeminorm(point=(1, 2))
    assert seminorm3.point == (1, 2)
    assert seminorm3.absolute is True


@pytest.mark.unit
def test_type_attribute():
    """Test that the type attribute is correctly set."""
    seminorm = PointEvaluationSeminorm(point=0)
    assert seminorm.type == "PointEvaluationSeminorm"


@pytest.mark.unit
@pytest.mark.parametrize(
    "point,expected",
    [
        (0, 0),  # f(0) = 0*0 = 0
        (2, 4),  # f(2) = 2*2 = 4
        (-3, 9),  # f(-3) = (-3)*(-3) = 9
    ],
)
def test_compute_with_function(sample_function, point, expected):
    """Test compute method with a function input."""
    seminorm = PointEvaluationSeminorm(point=point)
    result = seminorm.compute(sample_function)
    assert result == expected


@pytest.mark.unit
def test_compute_with_vector(sample_vector):
    """Test compute method with a vector-like input."""
    # Test with different indices
    seminorm1 = PointEvaluationSeminorm(point=0)
    assert seminorm1.compute(sample_vector) == 1

    seminorm2 = PointEvaluationSeminorm(point=2)
    assert seminorm2.compute(sample_vector) == 3

    # Test with out of range index
    seminorm3 = PointEvaluationSeminorm(point=10)
    with pytest.raises(ValueError):
        seminorm3.compute(sample_vector)


@pytest.mark.unit
def test_compute_with_dict(sample_dict):
    """Test compute method with a dictionary input."""
    # Test with existing keys
    seminorm1 = PointEvaluationSeminorm(point=0)
    assert seminorm1.compute(sample_dict) == 5

    seminorm2 = PointEvaluationSeminorm(point="key")
    assert seminorm2.compute(sample_dict) == 20

    # Test with non-existent key
    seminorm3 = PointEvaluationSeminorm(point="nonexistent")
    with pytest.raises(ValueError):
        seminorm3.compute(sample_dict)


@pytest.mark.unit
def test_compute_with_mock_vector(mock_vector):
    """Test compute method with a mock IVector implementation."""
    seminorm = PointEvaluationSeminorm(point=2)
    assert seminorm.compute(mock_vector) == 3


@pytest.mark.unit
def test_compute_with_numpy_array():
    """Test compute method with a numpy array."""
    array = np.array([5, 10, 15, 20, 25])

    seminorm1 = PointEvaluationSeminorm(point=0)
    assert seminorm1.compute(array) == 5

    seminorm2 = PointEvaluationSeminorm(point=3)
    assert seminorm2.compute(array) == 20


@pytest.mark.unit
def test_absolute_parameter():
    """Test that the absolute parameter works correctly."""

    # Create a function that returns negative values
    def neg_func(x):
        return -x

    # With absolute=True (default)
    seminorm1 = PointEvaluationSeminorm(point=5)
    assert seminorm1.compute(neg_func) == 5  # |-5| = 5

    # With absolute=False
    seminorm2 = PointEvaluationSeminorm(point=5, absolute=False)
    assert seminorm2.compute(neg_func) == -5


@pytest.mark.unit
def test_triangle_inequality_with_functions():
    """Test the triangle inequality check with functions."""

    def f(x):
        return x

    def g(x):
        return 2 * x

    seminorm = PointEvaluationSeminorm(point=3)
    assert seminorm.check_triangle_inequality(f, g)


@pytest.mark.unit
def test_triangle_inequality_with_vectors():
    """Test the triangle inequality check with vectors."""
    vec1 = [1, 2, 3, 4, 5]
    vec2 = [5, 4, 3, 2, 1]

    seminorm = PointEvaluationSeminorm(point=2)
    assert seminorm.check_triangle_inequality(vec1, vec2)


@pytest.mark.unit
def test_triangle_inequality_with_dicts():
    """Test the triangle inequality check with dictionaries."""
    dict1 = {0: 1, 1: 2, 2: 3}
    dict2 = {0: 4, 1: 5, 2: 6}

    seminorm = PointEvaluationSeminorm(point=1)
    assert seminorm.check_triangle_inequality(dict1, dict2)


@pytest.mark.unit
def test_scalar_homogeneity_with_function(sample_function):
    """Test the scalar homogeneity check with a function."""
    seminorm = PointEvaluationSeminorm(point=2)
    assert seminorm.check_scalar_homogeneity(sample_function, 3)


@pytest.mark.unit
def test_scalar_homogeneity_with_vector(sample_vector):
    """Test the scalar homogeneity check with a vector."""
    seminorm = PointEvaluationSeminorm(point=2)
    assert seminorm.check_scalar_homogeneity(sample_vector, 2.5)


@pytest.mark.unit
def test_scalar_homogeneity_with_dict(sample_dict):
    """Test the scalar homogeneity check with a dictionary."""
    seminorm = PointEvaluationSeminorm(point=1)
    assert seminorm.check_scalar_homogeneity(sample_dict, -2)


@pytest.mark.unit
def test_scalar_homogeneity_with_mock_vector(mock_vector):
    """Test the scalar homogeneity check with a mock vector."""
    seminorm = PointEvaluationSeminorm(point=3)
    assert seminorm.check_scalar_homogeneity(mock_vector, 1.5)


@pytest.mark.unit
def test_to_dict():
    """Test the to_dict method."""
    seminorm = PointEvaluationSeminorm(point="test_point", absolute=False)
    data = seminorm.to_dict()

    assert isinstance(data, dict)
    assert data["type"] == "PointEvaluationSeminorm"
    assert data["point"] == "test_point"
    assert data["absolute"] is False


@pytest.mark.unit
def test_from_dict():
    """Test the from_dict class method."""
    data = {"type": "PointEvaluationSeminorm", "point": "test_point", "absolute": False}

    seminorm = PointEvaluationSeminorm.from_dict(data)

    assert isinstance(seminorm, PointEvaluationSeminorm)
    assert seminorm.point == "test_point"
    assert seminorm.absolute is False


@pytest.mark.unit
def test_from_dict_default_absolute():
    """Test the from_dict method with default absolute value."""
    data = {"type": "PointEvaluationSeminorm", "point": 5}

    seminorm = PointEvaluationSeminorm.from_dict(data)

    assert isinstance(seminorm, PointEvaluationSeminorm)
    assert seminorm.point == 5
    assert seminorm.absolute is True


@pytest.mark.unit
def test_error_unsupported_input_type():
    """Test that compute raises TypeError for unsupported input types."""
    seminorm = PointEvaluationSeminorm(point=0)

    with pytest.raises(TypeError):
        seminorm.compute(123)  # Integer is not callable or indexable


@pytest.mark.unit
def test_error_point_not_in_domain():
    """Test that compute raises ValueError when the point is not in the domain."""
    seminorm = PointEvaluationSeminorm(point=10)

    with pytest.raises(ValueError):
        seminorm.compute([1, 2, 3])  # Index 10 is out of range


@pytest.mark.unit
def test_complex_input_handling():
    """Test handling of complex values."""

    def complex_func(x):
        return complex(x, x)

    seminorm = PointEvaluationSeminorm(point=3)
    result = seminorm.compute(complex_func)

    # For complex number z = a + bi, |z| = sqrt(a² + b²)
    expected = abs(complex(3, 3))
    assert result == expected


@pytest.mark.unit
def test_serialization_roundtrip():
    """Test that a seminorm can be serialized to dict and back without data loss."""
    original = PointEvaluationSeminorm(point="test", absolute=False)
    data = original.to_dict()
    reconstructed = PointEvaluationSeminorm.from_dict(data)

    assert reconstructed.point == original.point
    assert reconstructed.absolute == original.absolute
    assert reconstructed.type == original.type
