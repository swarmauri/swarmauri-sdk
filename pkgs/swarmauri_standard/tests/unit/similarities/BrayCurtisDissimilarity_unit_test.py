import logging
import pytest
import numpy as np
from typing import List, Tuple, Any

from swarmauri_standard.similarities.BrayCurtisDissimilarity import BrayCurtisDissimilarity

# Set up logging
logger = logging.getLogger(__name__)

@pytest.fixture
def dissimilarity_instance():
    """
    Create a BrayCurtisDissimilarity instance for testing.
    
    Returns
    -------
    BrayCurtisDissimilarity
        An instance of the BrayCurtisDissimilarity class
    """
    return BrayCurtisDissimilarity()

@pytest.mark.unit
def test_initialization():
    """Test the initialization of BrayCurtisDissimilarity."""
    dissimilarity = BrayCurtisDissimilarity()
    assert dissimilarity.type == "BrayCurtisDissimilarity"
    assert dissimilarity.is_bounded is True
    assert dissimilarity.lower_bound == 0.0
    assert dissimilarity.upper_bound == 1.0

@pytest.mark.unit
def test_validate_type():
    """Test the type validator works correctly."""
    dissimilarity = BrayCurtisDissimilarity()
    assert dissimilarity.type == "BrayCurtisDissimilarity"
    
    # The validator should be called during initialization, 
    # so we don't need to explicitly test it raising errors

@pytest.mark.unit
def test_is_reflexive(dissimilarity_instance):
    """Test that the measure is reflexive."""
    assert dissimilarity_instance.is_reflexive() is True

@pytest.mark.unit
def test_is_symmetric(dissimilarity_instance):
    """Test that the measure is symmetric."""
    assert dissimilarity_instance.is_symmetric() is True

@pytest.mark.unit
def test_str_representation(dissimilarity_instance):
    """Test the string representation of the class."""
    expected_str = "BrayCurtisDissimilarity (bounds: [0.0, 1.0])"
    assert str(dissimilarity_instance) == expected_str

@pytest.mark.unit
@pytest.mark.parametrize(
    "a, b, expected",
    [
        ([1, 2, 3], [1, 2, 3], 0.0),  # Identical vectors
        ([0, 0, 0], [0, 0, 0], 0.0),  # Zero vectors
        ([1, 0, 0], [0, 1, 0], 1.0),  # Completely different vectors
        ([4, 2, 0], [2, 4, 0], 0.5),  # Partially different vectors
        ([1, 1, 1], [2, 2, 2], 0.5),  # Scaled vectors
        ([0.5, 1.5, 2.5], [0.5, 1.5, 2.5], 0.0),  # Identical float vectors
        (np.array([1, 2, 3]), np.array([1, 2, 3]), 0.0),  # Numpy arrays
    ]
)
def test_calculate(dissimilarity_instance, a, b, expected):
    """
    Test the calculate method with various inputs.
    
    Parameters
    ----------
    dissimilarity_instance : BrayCurtisDissimilarity
        The instance to test
    a : List[float] or np.ndarray
        First vector
    b : List[float] or np.ndarray
        Second vector
    expected : float
        Expected dissimilarity value
    """
    result = dissimilarity_instance.calculate(a, b)
    assert np.isclose(result, expected), f"Expected {expected}, got {result}"

@pytest.mark.unit
def test_calculate_symmetric_property(dissimilarity_instance):
    """Test that the calculation is symmetric: d(a,b) = d(b,a)."""
    a = [1, 3, 5, 7]
    b = [2, 4, 6, 8]
    
    result_ab = dissimilarity_instance.calculate(a, b)
    result_ba = dissimilarity_instance.calculate(b, a)
    
    assert np.isclose(result_ab, result_ba)

@pytest.mark.unit
def test_calculate_reflexive_property(dissimilarity_instance):
    """Test that the calculation is reflexive: d(a,a) = 0."""
    a = [1, 3, 5, 7]
    
    result = dissimilarity_instance.calculate(a, a)
    
    assert np.isclose(result, 0.0)

@pytest.mark.unit
def test_calculate_with_different_lengths(dissimilarity_instance):
    """Test that the calculate method raises an error for different length vectors."""
    a = [1, 2, 3]
    b = [1, 2, 3, 4]
    
    with pytest.raises(ValueError) as excinfo:
        dissimilarity_instance.calculate(a, b)
    
    assert "Input vectors must have the same shape" in str(excinfo.value)

@pytest.mark.unit
def test_calculate_with_negative_values(dissimilarity_instance):
    """Test that the calculate method raises an error for negative values."""
    a = [1, 2, -3]
    b = [1, 2, 3]
    
    with pytest.raises(ValueError) as excinfo:
        dissimilarity_instance.calculate(a, b)
    
    assert "Input vectors must be non-negative" in str(excinfo.value)

@pytest.mark.unit
def test_serialization(dissimilarity_instance):
    """Test that the class can be serialized and deserialized correctly."""
    # Serialize
    json_str = dissimilarity_instance.model_dump_json()
    
    # Deserialize
    deserialized = BrayCurtisDissimilarity.model_validate_json(json_str)
    
    # Check that the original and deserialized objects have the same attributes
    assert deserialized.type == dissimilarity_instance.type
    assert deserialized.is_bounded == dissimilarity_instance.is_bounded
    assert deserialized.lower_bound == dissimilarity_instance.lower_bound
    assert deserialized.upper_bound == dissimilarity_instance.upper_bound

@pytest.mark.unit
def test_bounds_consistency(dissimilarity_instance):
    """Test that calculated values stay within the defined bounds."""
    test_vectors = [
        ([1, 2, 3], [4, 5, 6]),
        ([0, 0, 0], [1, 1, 1]),
        ([10, 20, 30], [5, 15, 25])
    ]
    
    for a, b in test_vectors:
        result = dissimilarity_instance.calculate(a, b)
        assert dissimilarity_instance.lower_bound <= result <= dissimilarity_instance.upper_bound