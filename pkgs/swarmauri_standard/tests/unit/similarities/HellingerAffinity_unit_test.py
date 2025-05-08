import pytest
import numpy as np
import logging
from typing import List, Dict, Any
from swarmauri_standard.similarities.HellingerAffinity import HellingerAffinity

# Set up logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture
def hellinger_affinity():
    """
    Fixture that provides a HellingerAffinity instance.
    
    Returns
    -------
    HellingerAffinity
        An instance of the HellingerAffinity class.
    """
    return HellingerAffinity()

@pytest.mark.unit
def test_resource():
    """
    Test that the resource attribute is correctly set.
    """
    assert HellingerAffinity.resource == "Similarity"

@pytest.mark.unit
def test_type():
    """
    Test that the type attribute is correctly set.
    """
    assert HellingerAffinity.type == "HellingerAffinity"

@pytest.mark.unit
def test_initialization(hellinger_affinity):
    """
    Test that HellingerAffinity initializes with correct bounds.
    
    Parameters
    ----------
    hellinger_affinity : HellingerAffinity
        The fixture providing a HellingerAffinity instance.
    """
    assert hellinger_affinity.is_bounded is True
    assert hellinger_affinity.lower_bound == 0.0
    assert hellinger_affinity.upper_bound == 1.0

@pytest.mark.unit
def test_serialization(hellinger_affinity):
    """
    Test that HellingerAffinity can be serialized and deserialized correctly.
    
    Parameters
    ----------
    hellinger_affinity : HellingerAffinity
        The fixture providing a HellingerAffinity instance.
    """
    serialized = hellinger_affinity.model_dump_json()
    deserialized = HellingerAffinity.model_validate_json(serialized)
    
    assert deserialized.type == hellinger_affinity.type
    assert deserialized.is_bounded == hellinger_affinity.is_bounded
    assert deserialized.lower_bound == hellinger_affinity.lower_bound
    assert deserialized.upper_bound == hellinger_affinity.upper_bound

@pytest.mark.unit
@pytest.mark.parametrize("a, b, expected", [
    ([0.5, 0.5], [0.5, 0.5], 1.0),  # Same distributions
    ([1.0, 0.0], [0.0, 1.0], 0.0),  # Completely different distributions
    ([0.3, 0.7], [0.7, 0.3], 0.3 * 0.7 ** 0.5 + 0.7 * 0.3 ** 0.5),  # Different distributions
    ([0.25, 0.25, 0.25, 0.25], [0.25, 0.25, 0.25, 0.25], 1.0),  # Uniform distributions
])
def test_calculate_with_lists(hellinger_affinity, a, b, expected):
    """
    Test HellingerAffinity calculation with list inputs.
    
    Parameters
    ----------
    hellinger_affinity : HellingerAffinity
        The fixture providing a HellingerAffinity instance.
    a : List[float]
        First probability distribution.
    b : List[float]
        Second probability distribution.
    expected : float
        Expected Hellinger Affinity value.
    """
    result = hellinger_affinity.calculate(a, b)
    assert np.isclose(result, expected, rtol=1e-5)

@pytest.mark.unit
@pytest.mark.parametrize("a, b, expected", [
    (np.array([0.5, 0.5]), np.array([0.5, 0.5]), 1.0),
    (np.array([1.0, 0.0]), np.array([0.0, 1.0]), 0.0),
    (np.array([0.3, 0.7]), np.array([0.7, 0.3]), 0.3 * 0.7 ** 0.5 + 0.7 * 0.3 ** 0.5),
])
def test_calculate_with_numpy_arrays(hellinger_affinity, a, b, expected):
    """
    Test HellingerAffinity calculation with numpy array inputs.
    
    Parameters
    ----------
    hellinger_affinity : HellingerAffinity
        The fixture providing a HellingerAffinity instance.
    a : np.ndarray
        First probability distribution.
    b : np.ndarray
        Second probability distribution.
    expected : float
        Expected Hellinger Affinity value.
    """
    result = hellinger_affinity.calculate(a, b)
    assert np.isclose(result, expected, rtol=1e-5)

@pytest.mark.unit
@pytest.mark.parametrize("a, b, expected", [
    ({"a": 0.5, "b": 0.5}, {"a": 0.5, "b": 0.5}, 1.0),
    ({"a": 1.0, "b": 0.0}, {"a": 0.0, "b": 1.0}, 0.0),
    ({"a": 0.3, "b": 0.7}, {"a": 0.7, "b": 0.3}, 0.3 * 0.7 ** 0.5 + 0.7 * 0.3 ** 0.5),
])
def test_calculate_with_dictionaries(hellinger_affinity, a, b, expected):
    """
    Test HellingerAffinity calculation with dictionary inputs.
    
    Parameters
    ----------
    hellinger_affinity : HellingerAffinity
        The fixture providing a HellingerAffinity instance.
    a : Dict[Any, float]
        First probability distribution.
    b : Dict[Any, float]
        Second probability distribution.
    expected : float
        Expected Hellinger Affinity value.
    """
    result = hellinger_affinity.calculate(a, b)
    assert np.isclose(result, expected, rtol=1e-5)

@pytest.mark.unit
def test_is_reflexive(hellinger_affinity):
    """
    Test that HellingerAffinity is reflexive.
    
    Parameters
    ----------
    hellinger_affinity : HellingerAffinity
        The fixture providing a HellingerAffinity instance.
    """
    assert hellinger_affinity.is_reflexive() is True

@pytest.mark.unit
def test_is_symmetric(hellinger_affinity):
    """
    Test that HellingerAffinity is symmetric.
    
    Parameters
    ----------
    hellinger_affinity : HellingerAffinity
        The fixture providing a HellingerAffinity instance.
    """
    assert hellinger_affinity.is_symmetric() is True

@pytest.mark.unit
def test_string_representation(hellinger_affinity):
    """
    Test the string representation of HellingerAffinity.
    
    Parameters
    ----------
    hellinger_affinity : HellingerAffinity
        The fixture providing a HellingerAffinity instance.
    """
    expected = "HellingerAffinity (bounds: [0.0, 1.0])"
    assert str(hellinger_affinity) == expected

@pytest.mark.unit
def test_invalid_distribution_negative_values(hellinger_affinity):
    """
    Test that an error is raised for distributions with negative values.
    
    Parameters
    ----------
    hellinger_affinity : HellingerAffinity
        The fixture providing a HellingerAffinity instance.
    """
    with pytest.raises(ValueError, match="contains negative values"):
        hellinger_affinity.calculate([0.5, -0.5], [0.5, 0.5])

@pytest.mark.unit
def test_invalid_distribution_sum_not_one(hellinger_affinity):
    """
    Test that an error is raised for distributions that don't sum to 1.
    
    Parameters
    ----------
    hellinger_affinity : HellingerAffinity
        The fixture providing a HellingerAffinity instance.
    """
    with pytest.raises(ValueError, match="must sum to 1"):
        hellinger_affinity.calculate([0.5, 0.6], [0.5, 0.5])

@pytest.mark.unit
def test_different_dimensions(hellinger_affinity):
    """
    Test that an error is raised when distributions have different dimensions.
    
    Parameters
    ----------
    hellinger_affinity : HellingerAffinity
        The fixture providing a HellingerAffinity instance.
    """
    with pytest.raises(ValueError, match="must have the same dimensions"):
        hellinger_affinity.calculate([0.5, 0.5], [0.3, 0.3, 0.4])

@pytest.mark.unit
def test_unsupported_type(hellinger_affinity):
    """
    Test that an error is raised for unsupported input types.
    
    Parameters
    ----------
    hellinger_affinity : HellingerAffinity
        The fixture providing a HellingerAffinity instance.
    """
    with pytest.raises(TypeError, match="Unsupported type"):
        hellinger_affinity.calculate("not a distribution", [0.5, 0.5])

@pytest.mark.unit
def test_bounds_property(hellinger_affinity):
    """
    Test that the bounds property returns the correct values.
    
    Parameters
    ----------
    hellinger_affinity : HellingerAffinity
        The fixture providing a HellingerAffinity instance.
    """
    # Calculate affinity for identical distributions (should be 1.0)
    identical = hellinger_affinity.calculate([0.5, 0.5], [0.5, 0.5])
    assert np.isclose(identical, hellinger_affinity.upper_bound)
    
    # Calculate affinity for completely different distributions (should be 0.0)
    different = hellinger_affinity.calculate([1.0, 0.0], [0.0, 1.0])
    assert np.isclose(different, hellinger_affinity.lower_bound)