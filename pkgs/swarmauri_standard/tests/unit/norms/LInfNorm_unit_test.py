"""Unit tests for the LInfNorm class in the swarmauri_standard package."""
import pytest
import logging
from swarmauri_standard.norms.LInfNorm import LInfNorm

@pytest.mark.unit
def test_compute_list():
    """Test the compute method with a list input."""
    norm = LInfNorm()
    test_input = [1, 2, 3, 4, 5]
    expected_output = 5
    assert norm.compute(test_input) == expected_output

@pytest.mark.unit
def test_compute_string_numeric():
    """Test the compute method with a string of numeric characters."""
    norm = LInfNorm()
    test_input = "12345"
    expected_output = 5
    assert norm.compute(test_input) == expected_output

@pytest.mark.unit
def test_compute_string_non_numeric():
    """Test the compute method with a string of non-numeric characters."""
    norm = LInfNorm()
    test_input = "abcde"
    # Unicode values for 'a' is 97, 'b' 98, etc.
    expected_output = 101  # ord('e') = 101
    assert norm.compute(test_input) == expected_output

@pytest.mark.unit
def test_compute_callable():
    """Test the compute method with a callable input."""
    norm = LInfNorm(domain=[1, 2, 3])
    test_input = lambda x: x**2
    expected_output = 9  # max(1, 4, 9)
    assert norm.compute(test_input) == expected_output

@pytest.mark.unit
def test_check_non_negativity():
    """Test the check_non_negativity method."""
    norm = LInfNorm()
    test_input = [1, 2, 3]
    norm.check_non_negativity(test_input)
    
    test_input_negative = [-1, -2, -3]
    norm.check_non_negativity(test_input_negative)

@pytest.mark.unit
def test_check_triangle_inequality():
    """Test the triangle inequality check."""
    norm = LInfNorm()
    x = [1, 2]
    y = [3, 4]
    norm.check_triangle_inequality(x, y)

@pytest.mark.unit
def test_check_absolute_homogeneity():
    """Test the absolute homogeneity check."""
    norm = LInfNorm()
    x = [1, 2]
    a = 2.5
    norm.check_absolute_homogeneity(x, a)
    
    a_negative = -2.5
    norm.check_absolute_homogeneity(x, a_negative)

@pytest.mark.unit
def test_check_definiteness():
    """Test the definiteness check."""
    norm = LInfNorm()
    zero_input = [0, 0]
    non_zero_input = [1, 2]
    
    norm.check_definiteness(zero_input)
    norm.check_definiteness(non_zero_input)

@pytest.mark.unit
def test_logging(caplog):
    """Test that logging messages are generated correctly."""
    caplog.set_level(logging.DEBUG)
    norm = LInfNorm()
    test_input = [1, 2, 3]
    
    norm.compute(test_input)
    assert "Computing L-Infinity norm for input:" in caplog.text
    assert "Computed L-Infinity norm:" in caplog.text