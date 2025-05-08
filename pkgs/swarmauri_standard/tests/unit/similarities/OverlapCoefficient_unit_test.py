import pytest
import logging
from typing import Set
from swarmauri_standard.similarities.OverlapCoefficient import OverlapCoefficient

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def overlap_coefficient() -> OverlapCoefficient:
    """
    Fixture that provides an instance of OverlapCoefficient for testing.
    
    Returns
    -------
    OverlapCoefficient
        An instance of the OverlapCoefficient similarity measure
    """
    return OverlapCoefficient()


@pytest.mark.unit
def test_type():
    """Test that the type property is correctly set."""
    assert OverlapCoefficient.type == "OverlapCoefficient"


@pytest.mark.unit
def test_resource():
    """Test that the resource property is correctly set."""
    assert OverlapCoefficient.resource == "Similarity"


@pytest.mark.unit
def test_initialization(overlap_coefficient):
    """Test initialization of OverlapCoefficient instance."""
    assert overlap_coefficient.is_bounded is True
    assert overlap_coefficient.lower_bound == 0.0
    assert overlap_coefficient.upper_bound == 1.0


@pytest.mark.unit
def test_is_reflexive(overlap_coefficient):
    """Test that OverlapCoefficient is reflexive."""
    assert overlap_coefficient.is_reflexive() is True


@pytest.mark.unit
def test_is_symmetric(overlap_coefficient):
    """Test that OverlapCoefficient is symmetric."""
    assert overlap_coefficient.is_symmetric() is True


@pytest.mark.unit
@pytest.mark.parametrize("set_a, set_b, expected", [
    ({"a", "b", "c"}, {"a", "b", "c"}, 1.0),  # Identical sets
    ({"a", "b", "c"}, {"a", "b", "c", "d"}, 1.0),  # First set is subset of second
    ({"a", "b", "c", "d"}, {"a", "b", "c"}, 1.0),  # Second set is subset of first
    ({"a", "b", "c"}, {"d", "e", "f"}, 0.0),  # No overlap
    ({"a", "b", "c"}, {"c", "d", "e"}, 1/3),  # Partial overlap
    ({"a", "b"}, {"a", "b", "c", "d", "e"}, 1.0),  # Complete overlap of smaller set
])
def test_calculate(overlap_coefficient, set_a, set_b, expected):
    """
    Test calculate method with various sets.
    
    Parameters
    ----------
    overlap_coefficient : OverlapCoefficient
        The similarity measure instance
    set_a : Set
        First set for comparison
    set_b : Set
        Second set for comparison
    expected : float
        Expected similarity value
    """
    result = overlap_coefficient.calculate(set_a, set_b)
    assert result == pytest.approx(expected)


@pytest.mark.unit
def test_calculate_with_empty_sets(overlap_coefficient):
    """Test that calculate raises ValueError when given empty sets."""
    with pytest.raises(ValueError):
        overlap_coefficient.calculate(set(), {"a", "b", "c"})
    
    with pytest.raises(ValueError):
        overlap_coefficient.calculate({"a", "b", "c"}, set())
    
    with pytest.raises(ValueError):
        overlap_coefficient.calculate(set(), set())


@pytest.mark.unit
def test_string_representation(overlap_coefficient):
    """Test the string representation of OverlapCoefficient."""
    expected_str = "OverlapCoefficient (bounds: [0.0, 1.0])"
    assert str(overlap_coefficient) == expected_str


@pytest.mark.unit
def test_serialization():
    """Test serialization and deserialization of OverlapCoefficient."""
    original = OverlapCoefficient()
    serialized = original.model_dump_json()
    deserialized = OverlapCoefficient.model_validate_json(serialized)
    
    # Verify the deserialized object has the same properties
    assert deserialized.type == original.type
    assert deserialized.is_bounded == original.is_bounded
    assert deserialized.lower_bound == original.lower_bound
    assert deserialized.upper_bound == original.upper_bound


@pytest.mark.unit
def test_with_different_types():
    """Test that OverlapCoefficient works with different element types."""
    oc = OverlapCoefficient[int]()
    set_a = {1, 2, 3}
    set_b = {2, 3, 4}
    result = oc.calculate(set_a, set_b)
    assert result == 2/3  # 2 common elements out of 3 elements in each set


@pytest.mark.unit
def test_large_sets(overlap_coefficient):
    """Test performance with large sets."""
    large_set_a = set(range(1000))
    large_set_b = set(range(500, 1500))
    
    # Expected: 500 common elements, min size is 1000
    expected = 500 / 1000
    
    result = overlap_coefficient.calculate(large_set_a, large_set_b)
    assert result == expected