import pytest
from swarmauri_standard.pseudometrics import ZeroPseudometric
import logging

@pytest.mark.unit
def test_type():
    """Test that the type attribute is correctly set."""
    assert ZeroPseudometric.type == "ZeroPseudometric"

@pytest.mark.unit
def test_resource():
    """Test that the resource attribute is correctly set."""
    assert ZeroPseudometric.resource == "PSEUDOMETRIC"

@pytest.mark.unit
def test_distance():
    """Test the distance method with various inputs."""
    pseudometric = ZeroPseudometric()
    
    # Test with strings
    assert pseudometric.distance("test1", "test2") == 0.0
    
    # Test with numbers
    assert pseudometric.distance(123, 456) == 0.0
    
    # Test with None
    assert pseudometric.distance(None, None) == 0.0
    
    # Test with mixed types
    assert pseudometric.distance("test", 123) == 0.0

@pytest.mark.unit
def test_distances():
    """Test the distances method with various input sequences."""
    pseudometric = ZeroPseudometric()
    
    # Test with empty sequences
    assert pseudometric.distances([], []) == []
    
    # Test with sequences of different lengths
    assert len(pseudometric.distances([1, 2, 3], ["a", "b"])) == 2
    
    # Test with sequences of same length
    result = pseudometric.distances([1, 2, 3], [4, 5, 6])
    assert len(result) == 3
    assert all(x == 0.0 for x in result)

@pytest.mark.unit
def test_logging(caplog):
    """Test that logging messages are correctly generated."""
    pseudometric = ZeroPseudometric()
    
    # Test distance method logging
    with caplog.at_level(logging.DEBUG):
        pseudometric.distance("test1", "test2")
        assert "Computing ZeroPseudometric distance" in caplog.text
    
    # Test distances method logging
    with caplog.at_level(logging.DEBUG):
        pseudometric.distances([1, 2], [3, 4])
        assert "Computing ZeroPseudometric distances" in caplog.text

@pytest.mark.unit
@pytest.mark.parametrize("x,y,expected", [
    ("test1", "test2", 0.0),
    (123, 456, 0.0),
    (None, None, 0.0),
    ("test", 123, 0.0),
])
def test_distance_parameterized(x, y, expected):
    """Parameterized test for the distance method."""
    pseudometric = ZeroPseudometric()
    assert pseudometric.distance(x, y) == expected