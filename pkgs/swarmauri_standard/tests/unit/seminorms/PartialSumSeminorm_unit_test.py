import logging
import pytest
import numpy as np
from typing import List, Union
from swarmauri_standard.seminorms.PartialSumSeminorm import PartialSumSeminorm

# Set up logging
logger = logging.getLogger(__name__)

# Fixture for creating a default PartialSumSeminorm instance
@pytest.fixture
def default_seminorm():
    """
    Fixture that returns a default PartialSumSeminorm instance.
    
    Returns
    -------
    PartialSumSeminorm
        A PartialSumSeminorm with default parameters.
    """
    return PartialSumSeminorm()

# Fixture for creating a custom PartialSumSeminorm instance
@pytest.fixture
def custom_seminorm():
    """
    Fixture that returns a custom PartialSumSeminorm instance.
    
    Returns
    -------
    PartialSumSeminorm
        A PartialSumSeminorm with start_index=1 and end_index=3.
    """
    return PartialSumSeminorm(start_index=1, end_index=3)

# Sample input vectors for testing
@pytest.fixture
def sample_vectors():
    """
    Fixture that returns sample vectors for testing.
    
    Returns
    -------
    dict
        Dictionary containing sample vectors of different types.
    """
    return {
        "list": [1.0, 2.0, 3.0, 4.0, 5.0],
        "numpy": np.array([1.0, 2.0, 3.0, 4.0, 5.0]),
        "zeros": np.zeros(5),
        "ones": np.ones(5),
        "negative": [-1.0, -2.0, -3.0, -4.0, -5.0]
    }


@pytest.mark.unit
def test_type():
    """Test that the type attribute is correctly set."""
    seminorm = PartialSumSeminorm()
    assert seminorm.type == "PartialSumSeminorm"


@pytest.mark.unit
def test_default_initialization():
    """Test default initialization of PartialSumSeminorm."""
    seminorm = PartialSumSeminorm()
    assert seminorm.start_index == 0
    assert seminorm.end_index is None


@pytest.mark.unit
def test_custom_initialization():
    """Test custom initialization of PartialSumSeminorm."""
    seminorm = PartialSumSeminorm(start_index=2, end_index=5)
    assert seminorm.start_index == 2
    assert seminorm.end_index == 5


@pytest.mark.unit
def test_validate_start_index():
    """Test validation of start_index."""
    # Valid start_index
    valid_seminorm = PartialSumSeminorm(start_index=0)
    assert valid_seminorm.start_index == 0
    
    # Invalid start_index (negative)
    with pytest.raises(ValueError, match="start_index must be non-negative"):
        PartialSumSeminorm(start_index=-1)


@pytest.mark.unit
def test_validate_end_index():
    """Test validation of end_index."""
    # Valid end_index
    valid_seminorm = PartialSumSeminorm(start_index=0, end_index=5)
    assert valid_seminorm.end_index == 5
    
    # Invalid end_index (less than or equal to start_index)
    with pytest.raises(ValueError, match="end_index must be greater than start_index"):
        PartialSumSeminorm(start_index=3, end_index=3)
    
    with pytest.raises(ValueError, match="end_index must be greater than start_index"):
        PartialSumSeminorm(start_index=3, end_index=2)


@pytest.mark.unit
@pytest.mark.parametrize("input_type", ["list", "numpy"])
def test_evaluate_full_vector(default_seminorm, sample_vectors, input_type):
    """Test evaluation of the seminorm on the full vector."""
    x = sample_vectors[input_type]
    result = default_seminorm.evaluate(x)
    expected = sum(abs(val) for val in x)
    assert result == pytest.approx(expected)


@pytest.mark.unit
def test_evaluate_partial_vector(custom_seminorm, sample_vectors):
    """Test evaluation of the seminorm on a partial vector."""
    x = sample_vectors["list"]
    result = custom_seminorm.evaluate(x)
    # Should sum only elements at indices 1 and 2 (since end_index is 3)
    expected = abs(x[1]) + abs(x[2])
    assert result == pytest.approx(expected)


@pytest.mark.unit
def test_evaluate_with_zero_vector(default_seminorm, sample_vectors):
    """Test evaluation of the seminorm on a zero vector."""
    x = sample_vectors["zeros"]
    result = default_seminorm.evaluate(x)
    assert result == 0.0


@pytest.mark.unit
def test_evaluate_with_negative_values(default_seminorm, sample_vectors):
    """Test evaluation of the seminorm on a vector with negative values."""
    x = sample_vectors["negative"]
    result = default_seminorm.evaluate(x)
    expected = sum(abs(val) for val in x)
    assert result == pytest.approx(expected)


@pytest.mark.unit
def test_evaluate_out_of_bounds(sample_vectors):
    """Test evaluation with out-of-bounds indices."""
    x = sample_vectors["list"]
    
    # start_index out of bounds
    seminorm_start_out = PartialSumSeminorm(start_index=len(x))
    with pytest.raises(ValueError, match="start_index .* is out of bounds"):
        seminorm_start_out.evaluate(x)
    
    # end_index out of bounds
    seminorm_end_out = PartialSumSeminorm(start_index=0, end_index=len(x) + 1)
    with pytest.raises(ValueError, match="end_index .* is out of bounds"):
        seminorm_end_out.evaluate(x)


@pytest.mark.unit
def test_evaluate_invalid_input_type(default_seminorm):
    """Test evaluation with an invalid input type."""
    with pytest.raises(ValueError, match="Input must be a list or numpy array"):
        default_seminorm.evaluate("not a valid input")


@pytest.mark.unit
@pytest.mark.parametrize("alpha", [0.5, 2.0, -1.0])
def test_scale(default_seminorm, sample_vectors, alpha):
    """Test scaling property of the seminorm."""
    x = sample_vectors["list"]
    
    # Direct scaling
    scaled_result = default_seminorm.scale(x, alpha)
    
    # Manual calculation
    direct_result = abs(alpha) * default_seminorm.evaluate(x)
    
    assert scaled_result == pytest.approx(direct_result)


@pytest.mark.unit
def test_triangle_inequality(default_seminorm, sample_vectors):
    """Test that the triangle inequality holds."""
    x = sample_vectors["list"]
    y = sample_vectors["ones"]
    
    # Check triangle inequality directly
    assert default_seminorm.triangle_inequality(x, y)
    
    # Verify manually
    p_x = default_seminorm.evaluate(x)
    p_y = default_seminorm.evaluate(y)
    p_sum = default_seminorm.evaluate(np.array(x) + np.array(y))
    
    assert p_sum <= p_x + p_y + 1e-10


@pytest.mark.unit
def test_triangle_inequality_different_lengths(default_seminorm, sample_vectors):
    """Test triangle inequality with vectors of different lengths."""
    x = sample_vectors["list"]
    y = [1.0, 2.0]  # Shorter than x
    
    with pytest.raises(ValueError, match="Inputs must have the same length"):
        default_seminorm.triangle_inequality(x, y)


@pytest.mark.unit
@pytest.mark.parametrize("tolerance", [1e-10, 1e-5, 0.1])
def test_is_zero(default_seminorm, sample_vectors, tolerance):
    """Test is_zero method with different tolerances."""
    # Zero vector should be zero regardless of tolerance
    assert default_seminorm.is_zero(sample_vectors["zeros"], tolerance)
    
    # Non-zero vector should not be zero with small tolerance
    assert not default_seminorm.is_zero(sample_vectors["ones"], 1e-10)
    
    # Create a vector with small values that depend on tolerance
    small_vector = np.ones(5) * (tolerance / 10)
    assert default_seminorm.is_zero(small_vector, tolerance)


@pytest.mark.unit
def test_is_definite(default_seminorm):
    """Test is_definite method."""
    # PartialSumSeminorm is not definite by default
    assert not default_seminorm.is_definite()


@pytest.mark.unit
def test_serialization_deserialization():
    """Test serialization and deserialization."""
    original = PartialSumSeminorm(start_index=1, end_index=3)
    serialized = original.model_dump_json()
    deserialized = PartialSumSeminorm.model_validate_json(serialized)
    
    assert deserialized.start_index == original.start_index
    assert deserialized.end_index == original.end_index
    assert deserialized.type == original.type


@pytest.mark.unit
def test_with_specific_vectors():
    """Test with specific vectors to verify partial sum functionality."""
    test_cases = [
        # (seminorm, input_vector, expected_result)
        (PartialSumSeminorm(start_index=0, end_index=3), [1, 2, 3, 4, 5], 6),  # Sum of first 3 elements
        (PartialSumSeminorm(start_index=2), [1, 2, 3, 4, 5], 12),  # Sum from index 2 to end
        (PartialSumSeminorm(start_index=1, end_index=4), [1, -2, 3, -4, 5], 9),  # Sum of absolute values
    ]
    
    for seminorm, input_vector, expected in test_cases:
        result = seminorm.evaluate(input_vector)
        assert result == pytest.approx(expected)