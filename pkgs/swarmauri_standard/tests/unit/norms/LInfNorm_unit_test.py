import pytest
import numpy as np
import logging
from typing import Any, List, Tuple
from swarmauri_standard.norms.LInfNorm import LInfNorm

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
def linf_norm():
    """
    Fixture that provides an instance of LInfNorm.
    
    Returns
    -------
    LInfNorm
        An instance of the LInfNorm class
    """
    return LInfNorm()

@pytest.mark.unit
def test_resource():
    """
    Test that the resource attribute is correctly set.
    """
    assert LInfNorm.resource == "norm"

@pytest.mark.unit
def test_type():
    """
    Test that the type attribute is correctly set.
    """
    assert LInfNorm.type == "LInfNorm"

@pytest.mark.unit
def test_serialization():
    """
    Test serialization and deserialization of LInfNorm.
    """
    linf_norm = LInfNorm()
    serialized = linf_norm.model_dump_json()
    deserialized = LInfNorm.model_validate_json(serialized)
    assert deserialized.type == linf_norm.type
    assert deserialized.resource == linf_norm.resource

@pytest.mark.unit
def test_name(linf_norm):
    """
    Test the name method returns the correct string.
    """
    assert linf_norm.name() == "L-infinity norm"

@pytest.mark.unit
@pytest.mark.parametrize("vector, expected", [
    ([1, 2, 3], 3.0),
    ([-5, 2, 1], 5.0),
    ([0, 0, 0], 0.0),
    (np.array([1.5, -2.5, 0.5]), 2.5),
    (np.array([-10, -20, -30]), 30.0),
])
def test_compute(linf_norm, vector, expected):
    """
    Test the compute method for various input vectors.
    
    Parameters
    ----------
    linf_norm : LInfNorm
        The LInfNorm instance
    vector : Union[List[float], np.ndarray]
        The input vector for norm computation
    expected : float
        The expected L-infinity norm value
    """
    result = linf_norm.compute(vector)
    assert np.isclose(result, expected)
    assert isinstance(result, float)

@pytest.mark.unit
def test_compute_with_unbounded_domain(linf_norm):
    """
    Test the compute method raises an exception for unbounded domains.
    """
    with pytest.raises(ValueError, match="Domain must be bounded"):
        linf_norm.compute([float('inf'), 1, 2])

@pytest.mark.unit
@pytest.mark.parametrize("x, y, expected", [
    ([1, 2, 3], [4, 5, 6], 3.0),
    ([0, 0, 0], [0, 0, 0], 0.0),
    ([-1, -2, -3], [-4, -5, -6], 3.0),
    (np.array([1.5, 2.5, 3.5]), np.array([1.0, 3.0, 4.0]), 0.5),
])
def test_distance(linf_norm, x, y, expected):
    """
    Test the distance method for various input vectors.
    
    Parameters
    ----------
    linf_norm : LInfNorm
        The LInfNorm instance
    x : Union[List[float], np.ndarray]
        The first input vector
    y : Union[List[float], np.ndarray]
        The second input vector
    expected : float
        The expected L-infinity distance value
    """
    result = linf_norm.distance(x, y)
    assert np.isclose(result, expected)
    assert isinstance(result, float)

@pytest.mark.unit
def test_distance_with_incompatible_dimensions(linf_norm):
    """
    Test the distance method raises an exception for vectors with incompatible dimensions.
    """
    with pytest.raises(ValueError, match="incompatible dimensions"):
        linf_norm.distance([1, 2, 3], [1, 2])

@pytest.mark.unit
def test_distance_with_unbounded_domain(linf_norm):
    """
    Test the distance method raises an exception for unbounded domains.
    """
    with pytest.raises(ValueError, match="Domains must be bounded"):
        linf_norm.distance([1, 2, 3], [float('inf'), 2, 3])

@pytest.mark.unit
@pytest.mark.parametrize("vector, expected_norm", [
    ([3, 6, 9], 1.0),
    ([-5, 2, 1], 1.0),
    (np.array([1.5, -2.5, 0.5]), 1.0),
])
def test_normalize(linf_norm, vector, expected_norm):
    """
    Test the normalize method for various input vectors.
    
    Parameters
    ----------
    linf_norm : LInfNorm
        The LInfNorm instance
    vector : Union[List[float], np.ndarray]
        The input vector to normalize
    expected_norm : float
        The expected norm of the normalized vector
    """
    normalized = linf_norm.normalize(vector)
    
    # Check that the norm of the normalized vector is 1.0
    assert np.isclose(linf_norm.compute(normalized), expected_norm)
    
    # Check that the type of the output matches the input
    assert type(normalized) == type(vector)
    
    # For numpy arrays, check the shape
    if isinstance(vector, np.ndarray):
        assert normalized.shape == vector.shape

@pytest.mark.unit
def test_normalize_zero_vector(linf_norm):
    """
    Test the normalize method raises an exception for a zero vector.
    """
    with pytest.raises(ValueError, match="Cannot normalize a zero vector"):
        linf_norm.normalize([0, 0, 0])

@pytest.mark.unit
def test_normalize_with_unbounded_domain(linf_norm):
    """
    Test the normalize method raises an exception for unbounded domains.
    """
    with pytest.raises(ValueError, match="Domain must be bounded"):
        linf_norm.normalize([float('inf'), 1, 2])

@pytest.mark.unit
@pytest.mark.parametrize("vector, is_unit", [
    ([1, 0, 0], True),
    ([0.5, 1, 0], True),
    ([0.5, 0.5, 0.5], False),
    (np.array([0, 0, 1]), True),
    (np.array([2, 0, 0]), False),
])
def test_is_normalized(linf_norm, vector, is_unit):
    """
    Test the is_normalized method for various input vectors.
    
    Parameters
    ----------
    linf_norm : LInfNorm
        The LInfNorm instance
    vector : Union[List[float], np.ndarray]
        The input vector to check
    is_unit : bool
        Whether the vector is expected to have unit L-infinity norm
    """
    result = linf_norm.is_normalized(vector)
    assert result == is_unit

@pytest.mark.unit
def test_is_normalized_with_tolerance(linf_norm):
    """
    Test the is_normalized method with different tolerance values.
    """
    # Vector with norm slightly different from 1.0
    vector = [1.001, 0, 0]
    
    # Should be considered normalized with a tolerance of 0.01
    assert linf_norm.is_normalized(vector, tolerance=0.01)
    
    # Should not be considered normalized with a tolerance of 0.0001
    assert not linf_norm.is_normalized(vector, tolerance=0.0001)

@pytest.mark.unit
def test_is_normalized_with_unbounded_domain(linf_norm):
    """
    Test the is_normalized method raises an exception for unbounded domains.
    """
    with pytest.raises(ValueError, match="Domain must be bounded"):
        linf_norm.is_normalized([float('inf'), 0, 0])