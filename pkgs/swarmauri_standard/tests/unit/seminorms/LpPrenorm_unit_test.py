import logging
import pytest
import numpy as np
from typing import List, Tuple, Any

from swarmauri_standard.seminorms.LpPrenorm import LpPrenorm

# Set up logging
logger = logging.getLogger(__name__)

@pytest.fixture
def lp_prenorm_default():
    """
    Fixture providing a default LpPrenorm with p=2.
    """
    return LpPrenorm()

@pytest.fixture
def lp_prenorm_custom(p_value):
    """
    Fixture providing a LpPrenorm with custom p value.
    """
    return LpPrenorm(p=p_value)

@pytest.mark.unit
def test_initialization():
    """
    Test that LpPrenorm initializes correctly with default and custom values.
    """
    # Default initialization
    lp_norm = LpPrenorm()
    assert lp_norm.p == 2.0
    assert lp_norm.type == "LpPrenorm"
    
    # Custom initialization
    lp_norm = LpPrenorm(p=3.0)
    assert lp_norm.p == 3.0

@pytest.mark.unit
def test_invalid_initialization():
    """
    Test that LpPrenorm raises appropriate errors for invalid p values.
    """
    # p must be positive
    with pytest.raises(ValueError, match="p must be positive"):
        LpPrenorm(p=0)
    
    with pytest.raises(ValueError, match="p must be positive"):
        LpPrenorm(p=-1.5)

@pytest.mark.unit
@pytest.mark.parametrize("p_value,input_vector,expected", [
    (1.0, [1, 2, 3], 6.0),  # L1 norm (sum of absolutes)
    (2.0, [1, 2, 3], np.sqrt(14)),  # L2 norm (Euclidean)
    (3.0, [1, 2, 3], (1**3 + 2**3 + 3**3)**(1/3)),  # L3 norm
    (2.0, [], 0.0),  # Empty vector
    (2.0, [0, 0, 0], 0.0),  # Zero vector
    (2.0, [-1, -2, -3], np.sqrt(14)),  # Negative values
])
def test_evaluate(p_value, input_vector, expected):
    """
    Test that LpPrenorm.evaluate correctly computes the Lp norm for various inputs.
    """
    lp_norm = LpPrenorm(p=p_value)
    result = lp_norm.evaluate(input_vector)
    assert np.isclose(result, expected)

@pytest.mark.unit
@pytest.mark.parametrize("p_value,input_vector,alpha,expected", [
    (2.0, [1, 2, 3], 2.0, 2 * np.sqrt(14)),  # Positive scaling
    (2.0, [1, 2, 3], -2.0, 2 * np.sqrt(14)),  # Negative scaling (absolute value)
    (2.0, [1, 2, 3], 0.0, 0.0),  # Zero scaling
    (1.0, [1, 1, 1], 3.0, 9.0),  # L1 norm scaling
])
def test_scale(p_value, input_vector, alpha, expected):
    """
    Test that LpPrenorm.scale correctly computes the scaled norm.
    """
    lp_norm = LpPrenorm(p=p_value)
    result = lp_norm.scale(input_vector, alpha)
    assert np.isclose(result, expected)

@pytest.mark.unit
@pytest.mark.parametrize("p_value,x,y", [
    (1.0, [1, 2, 3], [4, 5, 6]),  # L1 norm
    (2.0, [1, 2, 3], [4, 5, 6]),  # L2 norm
    (3.0, [1, 2, 3], [4, 5, 6]),  # L3 norm
    (2.0, [-1, -2, -3], [4, 5, 6]),  # Negative values
    (2.0, [0, 0, 0], [4, 5, 6]),  # Zero vector
])
def test_triangle_inequality(p_value, x, y):
    """
    Test that LpPrenorm satisfies the triangle inequality.
    """
    lp_norm = LpPrenorm(p=p_value)
    assert lp_norm.triangle_inequality(x, y)

@pytest.mark.unit
def test_triangle_inequality_incompatible_shapes():
    """
    Test that triangle_inequality raises an error for incompatible shapes.
    """
    lp_norm = LpPrenorm()
    with pytest.raises(ValueError, match="Incompatible shapes"):
        lp_norm.triangle_inequality([1, 2, 3], [4, 5])

@pytest.mark.unit
@pytest.mark.parametrize("p_value,input_vector,tolerance,expected", [
    (2.0, [0, 0, 0], 1e-10, True),  # Zero vector
    (2.0, [1e-11, 1e-11, 1e-11], 1e-10, True),  # Very small values below tolerance
    (2.0, [1e-9, 1e-9, 1e-9], 1e-10, False),  # Small values above tolerance
    (2.0, [1, 2, 3], 1e-10, False),  # Non-zero vector
])
def test_is_zero(p_value, input_vector, tolerance, expected):
    """
    Test that LpPrenorm.is_zero correctly identifies zero and non-zero vectors.
    """
    lp_norm = LpPrenorm(p=p_value)
    assert lp_norm.is_zero(input_vector, tolerance) == expected

@pytest.mark.unit
def test_is_definite():
    """
    Test that LpPrenorm.is_definite always returns False.
    """
    lp_norm = LpPrenorm()
    assert lp_norm.is_definite() is False
    
    lp_norm = LpPrenorm(p=1.0)
    assert lp_norm.is_definite() is False

@pytest.mark.unit
def test_serialization():
    """
    Test that LpPrenorm can be serialized and deserialized correctly.
    """
    lp_norm = LpPrenorm(p=3.5)
    json_data = lp_norm.model_dump_json()
    
    # Deserialize
    deserialized = LpPrenorm.model_validate_json(json_data)
    
    # Check equality
    assert deserialized.p == lp_norm.p
    assert deserialized.type == lp_norm.type

@pytest.mark.unit
def test_numpy_array_input():
    """
    Test that LpPrenorm works with numpy array inputs.
    """
    lp_norm = LpPrenorm()
    
    # Test with numpy array
    input_array = np.array([1.0, 2.0, 3.0])
    result = lp_norm.evaluate(input_array)
    expected = np.sqrt(14)
    assert np.isclose(result, expected)
    
    # Test with 2D array (should be flattened)
    input_array_2d = np.array([[1.0, 2.0], [3.0, 4.0]])
    result = lp_norm.evaluate(input_array_2d)
    expected = np.sqrt(30)  # sqrt(1^2 + 2^2 + 3^2 + 4^2)
    assert np.isclose(result, expected)