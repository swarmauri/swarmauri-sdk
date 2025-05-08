import logging
import pytest
import numpy as np
from typing import List, Union

from swarmauri_standard.similarities.BhattacharyyaCoefficient import BhattacharyyaCoefficient

# Set up logging
logger = logging.getLogger(__name__)


@pytest.fixture
def bhattacharyya_coefficient():
    """
    Fixture that returns a BhattacharyyaCoefficient instance.
    
    Returns
    -------
    BhattacharyyaCoefficient
        An instance of BhattacharyyaCoefficient
    """
    return BhattacharyyaCoefficient()


@pytest.mark.unit
def test_resource():
    """
    Test that the resource attribute is correctly set.
    """
    assert BhattacharyyaCoefficient.resource == "Similarity"


@pytest.mark.unit
def test_type():
    """
    Test that the type attribute is correctly set.
    """
    assert BhattacharyyaCoefficient.type == "BhattacharyyaCoefficient"


@pytest.mark.unit
def test_initialization(bhattacharyya_coefficient):
    """
    Test that the BhattacharyyaCoefficient initializes correctly.
    
    Parameters
    ----------
    bhattacharyya_coefficient : BhattacharyyaCoefficient
        The fixture providing a BhattacharyyaCoefficient instance
    """
    assert bhattacharyya_coefficient.is_bounded is True
    assert bhattacharyya_coefficient.lower_bound == 0.0
    assert bhattacharyya_coefficient.upper_bound == 1.0


@pytest.mark.unit
def test_serialization(bhattacharyya_coefficient):
    """
    Test that the BhattacharyyaCoefficient can be serialized and deserialized.
    
    Parameters
    ----------
    bhattacharyya_coefficient : BhattacharyyaCoefficient
        The fixture providing a BhattacharyyaCoefficient instance
    """
    serialized = bhattacharyya_coefficient.model_dump_json()
    deserialized = BhattacharyyaCoefficient.model_validate_json(serialized)
    
    assert isinstance(deserialized, BhattacharyyaCoefficient)
    assert deserialized.is_bounded == bhattacharyya_coefficient.is_bounded
    assert deserialized.lower_bound == bhattacharyya_coefficient.lower_bound
    assert deserialized.upper_bound == bhattacharyya_coefficient.upper_bound


@pytest.mark.unit
@pytest.mark.parametrize(
    "a, b, expected",
    [
        ([0.2, 0.3, 0.5], [0.2, 0.3, 0.5], 1.0),  # Identical distributions
        ([0.5, 0.5], [0.5, 0.5], 1.0),  # Identical uniform distributions
        ([1.0, 0.0], [0.0, 1.0], 0.0),  # Completely different distributions
        ([0.3, 0.7], [0.7, 0.3], 0.8775),  # Partially overlapping
        ([0.25, 0.25, 0.25, 0.25], [0.25, 0.25, 0.25, 0.25], 1.0),  # Uniform distributions
    ]
)
def test_calculate(bhattacharyya_coefficient, a, b, expected):
    """
    Test the calculation of Bhattacharyya Coefficient for various distribution pairs.
    
    Parameters
    ----------
    bhattacharyya_coefficient : BhattacharyyaCoefficient
        The fixture providing a BhattacharyyaCoefficient instance
    a : List[float]
        First probability distribution
    b : List[float]
        Second probability distribution
    expected : float
        Expected Bhattacharyya Coefficient value
    """
    result = bhattacharyya_coefficient.calculate(a, b)
    assert np.isclose(result, expected, rtol=1e-4)


@pytest.mark.unit
def test_calculate_with_numpy_arrays(bhattacharyya_coefficient):
    """
    Test the calculation of Bhattacharyya Coefficient with NumPy arrays.
    
    Parameters
    ----------
    bhattacharyya_coefficient : BhattacharyyaCoefficient
        The fixture providing a BhattacharyyaCoefficient instance
    """
    a = np.array([0.2, 0.3, 0.5])
    b = np.array([0.3, 0.4, 0.3])
    
    result = bhattacharyya_coefficient.calculate(a, b)
    expected = 0.9522  # Precomputed value
    
    assert np.isclose(result, expected, rtol=1e-4)


@pytest.mark.unit
def test_error_different_lengths(bhattacharyya_coefficient):
    """
    Test that an error is raised when distributions have different lengths.
    
    Parameters
    ----------
    bhattacharyya_coefficient : BhattacharyyaCoefficient
        The fixture providing a BhattacharyyaCoefficient instance
    """
    a = [0.5, 0.5]
    b = [0.3, 0.3, 0.4]
    
    with pytest.raises(ValueError, match="Distributions must have the same shape"):
        bhattacharyya_coefficient.calculate(a, b)


@pytest.mark.unit
def test_error_not_normalized(bhattacharyya_coefficient):
    """
    Test that an error is raised when distributions are not normalized.
    
    Parameters
    ----------
    bhattacharyya_coefficient : BhattacharyyaCoefficient
        The fixture providing a BhattacharyyaCoefficient instance
    """
    a = [0.5, 0.6]  # Sum = 1.1
    b = [0.5, 0.5]  # Sum = 1.0
    
    with pytest.raises(ValueError, match="Distributions must be normalized"):
        bhattacharyya_coefficient.calculate(a, b)


@pytest.mark.unit
def test_error_negative_values(bhattacharyya_coefficient):
    """
    Test that an error is raised when distributions contain negative values.
    
    Parameters
    ----------
    bhattacharyya_coefficient : BhattacharyyaCoefficient
        The fixture providing a BhattacharyyaCoefficient instance
    """
    a = [0.5, 0.5]
    b = [1.1, -0.1]  # Contains a negative value
    
    with pytest.raises(ValueError, match="Distributions cannot contain negative values"):
        bhattacharyya_coefficient.calculate(a, b)


@pytest.mark.unit
def test_is_reflexive(bhattacharyya_coefficient):
    """
    Test that BhattacharyyaCoefficient is reflexive.
    
    Parameters
    ----------
    bhattacharyya_coefficient : BhattacharyyaCoefficient
        The fixture providing a BhattacharyyaCoefficient instance
    """
    assert bhattacharyya_coefficient.is_reflexive() is True


@pytest.mark.unit
def test_is_symmetric(bhattacharyya_coefficient):
    """
    Test that BhattacharyyaCoefficient is symmetric.
    
    Parameters
    ----------
    bhattacharyya_coefficient : BhattacharyyaCoefficient
        The fixture providing a BhattacharyyaCoefficient instance
    """
    assert bhattacharyya_coefficient.is_symmetric() is True


@pytest.mark.unit
def test_string_representation(bhattacharyya_coefficient):
    """
    Test the string representation of BhattacharyyaCoefficient.
    
    Parameters
    ----------
    bhattacharyya_coefficient : BhattacharyyaCoefficient
        The fixture providing a BhattacharyyaCoefficient instance
    """
    string_rep = str(bhattacharyya_coefficient)
    assert "BhattacharyyaCoefficient" in string_rep
    assert "bounds: [0.0, 1.0]" in string_rep