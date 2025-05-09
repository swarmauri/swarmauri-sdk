import pytest
from swarmauri_standard.swarmauri_standard.metrics import LpMetric
import logging

@pytest.mark.unit
def test_LpMetric_constructor_valid_p():
    """Test initialization of LpMetric with valid p parameter."""
    lp = LpMetric(p=2)
    assert lp.p == 2

@pytest.mark.unit
def test_LpMetric_constructor_invalid_p():
    """Test initialization of LpMetric with invalid p parameter."""
    with pytest.raises(ValueError):
        LpMetric(p=1)
    with pytest.raises(ValueError):
        LpMetric(p=float('inf'))

@pytest.mark.unit
def test_LpMetric_distance_vector():
    """Test Lp distance calculation between vectors."""
    lp = LpMetric(p=2)
    x = [1, 2, 3]
    y = [4, 5, 6]
    distance = lp.distance(x, y)
    assert distance == 5.0

@pytest.mark.unit
def test_LpMetric_distance_matrix():
    """Test Lp distance calculation between matrices."""
    lp = LpMetric(p=2)
    x = [[1, 2], [3, 4]]
    y = [[5, 6], [7, 8]]
    distance = lp.distance(x, y)
    assert distance == 10.0

@pytest.mark.unit
def test_LpMetric_distance_sequence():
    """Test Lp distance calculation between sequences."""
    lp = LpMetric(p=2)
    x = (1, 2, 3)
    y = (4, 5, 6)
    distance = lp.distance(x, y)
    assert distance == 5.0

@pytest.mark.unit
def test_LpMetric_distance_string():
    """Test Lp distance calculation between strings."""
    lp = LpMetric(p=2)
    x = "abc"
    y = "def"
    distance = lp.distance(x, y)
    assert distance == 3.0

@pytest.mark.unit
def test_LpMetric_check_non_negativity():
    """Test non-negativity property of LpMetric."""
    lp = LpMetric(p=2)
    x = [1, 2, 3]
    y = [4, 5, 6]
    assert lp.check_non_negativity(x, y)

@pytest.mark.unit
def test_LpMetric_check_identity():
    """Test identity property of LpMetric."""
    lp = LpMetric(p=2)
    x = [1, 2, 3]
    y = [1, 2, 3]
    assert lp.check_identity(x, y)

@pytest.mark.unit
def test_LpMetric_check_symmetry():
    """Test symmetry property of LpMetric."""
    lp = LpMetric(p=2)
    x = [1, 2, 3]
    y = [4, 5, 6]
    assert lp.check_symmetry(x, y)

@pytest.mark.unit
def test_LpMetric_check_triangle_inequality():
    """Test triangle inequality property of LpMetric."""
    lp = LpMetric(p=2)
    x = [1, 2, 3]
    y = [4, 5, 6]
    z = [7, 8, 9]
    assert lp.check_triangle_inequality(x, y, z)

@pytest.mark.unit
def test_LpMetric_string_representation():
    """Test string representation of LpMetric."""
    lp = LpMetric(p=2)
    assert str(lp) == "LpMetric(p=2)"
    assert repr(lp) == "LpMetric(p=2)"

@pytest.mark.unit
def test_LpMetric_logging():
    """Test logging functionality in LpMetric."""
    lp = LpMetric(p=2)
    with pytest.raises(AssertionError):
        # Using caplog to capture logging output
        # This test will fail if logging is not properly implemented
        lp.distance([1, 2], [3, 4])
        assert "Computing Lp distance" in caplog.text