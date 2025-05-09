import pytest
from swarmauri_standard.swarmauri_standard.norms.L1ManhattanNorm import L1ManhattanNorm
import logging

logger = logging.getLogger(__name__)

@pytest.mark.unit
def test_compute_with_list_input():
    """Test L1 norm computation with list input."""
    norm = L1ManhattanNorm()
    x = [1, 2, 3]
    result = norm.compute(x)
    assert result == 6, "L1 norm calculation failed for list input"

@pytest.mark.unit
def test_compute_with_string_input():
    """Test L1 norm computation with string input."""
    norm = L1ManhattanNorm()
    x = "1 2 3"
    result = norm.compute(x)
    assert result == 6, "L1 norm calculation failed for string input"

@pytest.mark.unit
def test_compute_with_callable_input():
    """Test L1 norm computation with callable input."""
    norm = L1ManhattanNorm()
    
    def vector_generator():
        return [1, 2, 3]
    
    result = norm.compute(vector_generator)
    assert result == 6, "L1 norm calculation failed for callable input"

@pytest.mark.unit
def test_compute_invalid_input():
    """Test L1 norm computation with invalid input type."""
    norm = L1ManhattanNorm()
    x = None
    with pytest.raises(TypeError):
        norm.compute(x)

@pytest.mark.unit
def test_non_negativity():
    """Test non-negativity property of L1 norm."""
    norm = L1ManhattanNorm()
    
    # Test with positive vector
    x = [1, 2, 3]
    norm_value = norm.compute(x)
    assert norm_value >= 0, "Norm value should be non-negative"
    
    # Test with zero vector
    x = [0, 0, 0]
    norm_value = norm.compute(x)
    assert norm_value == 0, "Zero vector should have norm zero"

@pytest.mark.unit
def test_triangle_inequality():
    """Test triangle inequality property of L1 norm."""
    norm = L1ManhattanNorm()
    
    x = [1, 2]
    y = [3, 4]
    
    norm_x = norm.compute(x)
    norm_y = norm.compute(y)
    
    sum_xy = [4, 6]
    norm_sum = norm.compute(sum_xy)
    
    assert norm_sum <= norm_x + norm_y, "Triangle inequality not satisfied"

@pytest.mark.unit
def test_absolute_homogeneity():
    """Test absolute homogeneity property of L1 norm."""
    norm = L1ManhattanNorm()
    x = [1, 2, 3]
    
    # Test with positive scalar
    alpha = 2
    scaled = [2, 4, 6]
    assert norm.compute(scaled) == alpha * norm.compute(x)
    
    # Test with negative scalar
    alpha = -2
    scaled = [-2, -4, -6]
    assert norm.compute(scaled) == abs(alpha) * norm.compute(x)
    
    # Test with zero scalar
    alpha = 0
    scaled = [0, 0, 0]
    assert norm.compute(scaled) == abs(alpha) * norm.compute(x)

@pytest.mark.unit
def test_definiteness():
    """Test definiteness property of L1 norm."""
    norm = L1ManhattanNorm()
    
    # Test non-zero vector
    x = [1, 2]
    norm_value = norm.compute(x)
    assert norm_value != 0, "Non-zero vector should have non-zero norm"
    
    # Test zero vector
    x = [0, 0]
    norm_value = norm.compute(x)
    assert norm_value == 0, "Zero vector should have zero norm"

@pytest.mark.unit
def test_class_attributes():
    """Test class attributes of L1ManhattanNorm."""
    norm = L1ManhattanNorm()
    
    assert norm.type == "L1ManhattanNorm", "Type attribute incorrect"
    assert norm.resource == "norm", "Resource attribute incorrect"