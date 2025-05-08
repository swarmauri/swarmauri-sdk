import logging
import pytest
import numpy as np
from swarmauri_standard.norms.L2EuclideanNorm import L2EuclideanNorm

# Configure logging
logger = logging.getLogger(__name__)

@pytest.fixture
def l2_norm():
    """
    Pytest fixture that provides an instance of L2EuclideanNorm.
    
    Returns
    -------
    L2EuclideanNorm
        An instance of the L2EuclideanNorm class
    """
    return L2EuclideanNorm()

@pytest.mark.unit
def test_type():
    """Test that the type attribute is correctly set."""
    assert L2EuclideanNorm.type == "L2EuclideanNorm"

@pytest.mark.unit
def test_resource():
    """Test that the resource attribute is correctly inherited."""
    assert L2EuclideanNorm.resource == "Norm"

@pytest.mark.unit
def test_name(l2_norm):
    """Test that the name method returns the correct string."""
    assert l2_norm.name() == "L2EuclideanNorm"

@pytest.mark.unit
@pytest.mark.parametrize("vector, expected", [
    ([3, 4], 5.0),
    ([1, 0, 0], 1.0),
    ([1, 1, 1, 1], 2.0),
    (np.array([2, 2]), 2.0 * np.sqrt(2)),
    ((5, 12), 13.0),
    ([0, 0, 0], 0.0),
])
def test_compute(l2_norm, vector, expected):
    """
    Test the compute method with various vectors.
    
    Parameters
    ----------
    l2_norm : L2EuclideanNorm
        The norm instance from the fixture
    vector : array-like
        Input vector for testing
    expected : float
        Expected norm value
    """
    result = l2_norm.compute(vector)
    assert np.isclose(result, expected)

@pytest.mark.unit
def test_compute_with_invalid_input(l2_norm):
    """Test that compute raises appropriate exceptions for invalid inputs."""
    with pytest.raises(TypeError):
        l2_norm.compute("not a vector")
    
    with pytest.raises((TypeError, ValueError)):
        l2_norm.compute(None)

@pytest.mark.unit
@pytest.mark.parametrize("x, y, expected", [
    ([1, 0], [0, 1], np.sqrt(2)),
    ([1, 1], [1, 1], 0.0),
    ([3, 4], [0, 0], 5.0),
    (np.array([2, 3]), np.array([5, 7]), 5.0),
    ([0, 0, 0], [1, 1, 1], np.sqrt(3)),
])
def test_distance(l2_norm, x, y, expected):
    """
    Test the distance method with various vector pairs.
    
    Parameters
    ----------
    l2_norm : L2EuclideanNorm
        The norm instance from the fixture
    x : array-like
        First input vector
    y : array-like
        Second input vector
    expected : float
        Expected distance value
    """
    result = l2_norm.distance(x, y)
    assert np.isclose(result, expected)

@pytest.mark.unit
def test_distance_with_incompatible_dimensions(l2_norm):
    """Test that distance raises ValueError for incompatible dimensions."""
    with pytest.raises(ValueError):
        l2_norm.distance([1, 2], [1, 2, 3])

@pytest.mark.unit
def test_distance_with_invalid_input(l2_norm):
    """Test that distance raises appropriate exceptions for invalid inputs."""
    with pytest.raises((TypeError, ValueError)):
        l2_norm.distance("not a vector", [1, 2])
    
    with pytest.raises((TypeError, ValueError)):
        l2_norm.distance([1, 2], None)

@pytest.mark.unit
@pytest.mark.parametrize("vector, expected_type", [
    ([3, 4], list),
    (np.array([3, 4]), np.ndarray),
    ((3, 4), np.ndarray),  # Tuples may convert to ndarray
])
def test_normalize_return_type(l2_norm, vector, expected_type):
    """
    Test that normalize preserves input type when possible.
    
    Parameters
    ----------
    l2_norm : L2EuclideanNorm
        The norm instance from the fixture
    vector : array-like
        Input vector for testing
    expected_type : type
        Expected type of the result
    """
    result = l2_norm.normalize(vector)
    assert isinstance(result, expected_type)

@pytest.mark.unit
@pytest.mark.parametrize("vector", [
    [3, 4],
    [1, 2, 3],
    np.array([5, 12]),
    (7, 24),
])
def test_normalize_produces_unit_vector(l2_norm, vector):
    """
    Test that normalize produces a vector with unit norm.
    
    Parameters
    ----------
    l2_norm : L2EuclideanNorm
        The norm instance from the fixture
    vector : array-like
        Input vector for testing
    """
    normalized = l2_norm.normalize(vector)
    norm = l2_norm.compute(normalized)
    assert np.isclose(norm, 1.0)

@pytest.mark.unit
def test_normalize_zero_vector(l2_norm):
    """Test that normalize raises ValueError for zero vectors."""
    with pytest.raises(ValueError):
        l2_norm.normalize([0, 0, 0])

@pytest.mark.unit
@pytest.mark.parametrize("vector, expected", [
    ([1, 0], True),
    ([0, 1], True),
    ([1/np.sqrt(2), 1/np.sqrt(2)], True),
    ([3, 4], False),
    ([0, 0], False),
])
def test_is_normalized(l2_norm, vector, expected):
    """
    Test the is_normalized method with various vectors.
    
    Parameters
    ----------
    l2_norm : L2EuclideanNorm
        The norm instance from the fixture
    vector : array-like
        Input vector for testing
    expected : bool
        Expected result of normalization check
    """
    result = l2_norm.is_normalized(vector)
    assert result == expected

@pytest.mark.unit
@pytest.mark.parametrize("vector, tolerance, expected", [
    ([1.01, 0], 0.1, True),
    ([1.01, 0], 0.001, False),
    ([0.99, 0], 0.1, True),
    ([0.99, 0], 0.001, False),
])
def test_is_normalized_with_tolerance(l2_norm, vector, tolerance, expected):
    """
    Test the is_normalized method with various tolerances.
    
    Parameters
    ----------
    l2_norm : L2EuclideanNorm
        The norm instance from the fixture
    vector : array-like
        Input vector for testing
    tolerance : float
        Tolerance for the normalization check
    expected : bool
        Expected result of normalization check
    """
    result = l2_norm.is_normalized(vector, tolerance=tolerance)
    assert result == expected

@pytest.mark.unit
def test_serialization():
    """Test that the L2EuclideanNorm can be serialized and deserialized correctly."""
    l2_norm = L2EuclideanNorm()
    serialized = l2_norm.model_dump_json()
    deserialized = L2EuclideanNorm.model_validate_json(serialized)
    
    # Check that the deserialized object has the same type
    assert deserialized.type == l2_norm.type
    
    # Check that the deserialized object behaves the same
    vector = [3, 4]
    assert np.isclose(deserialized.compute(vector), l2_norm.compute(vector))