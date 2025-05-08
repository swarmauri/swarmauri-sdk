import pytest
import logging
from typing import Set
from swarmauri_standard.similarities.JaccardIndex import JaccardIndex

# Set up logging
logger = logging.getLogger(__name__)

@pytest.fixture
def jaccard_index():
    """
    Fixture providing a JaccardIndex instance for testing.
    
    Returns
    -------
    JaccardIndex
        An instance of the JaccardIndex similarity measure
    """
    return JaccardIndex()

@pytest.mark.unit
def test_type():
    """Test that the type property is correctly set."""
    assert JaccardIndex.type == "JaccardIndex"

@pytest.mark.unit
def test_resource():
    """Test that the resource property is correctly set."""
    assert JaccardIndex.resource == "Similarity"

@pytest.mark.unit
def test_bounds(jaccard_index):
    """Test that the bounds are correctly set."""
    assert jaccard_index.is_bounded is True
    assert jaccard_index.lower_bound == 0.0
    assert jaccard_index.upper_bound == 1.0

@pytest.mark.unit
def test_reflexive(jaccard_index):
    """Test that the similarity measure is reflexive."""
    assert jaccard_index.is_reflexive() is True

@pytest.mark.unit
def test_symmetric(jaccard_index):
    """Test that the similarity measure is symmetric."""
    assert jaccard_index.is_symmetric() is True

@pytest.mark.unit
@pytest.mark.parametrize("a, b, expected", [
    # Identical sets
    ({"a", "b", "c"}, {"a", "b", "c"}, 1.0),
    # Disjoint sets
    ({"a", "b", "c"}, {"d", "e", "f"}, 0.0),
    # Partial overlap
    ({"a", "b", "c"}, {"c", "d", "e"}, 0.2),
    # One set is a subset of the other
    ({"a", "b"}, {"a", "b", "c", "d"}, 0.5),
    # Empty sets
    (set(), set(), 1.0),
    # One empty set
    ({"a", "b", "c"}, set(), 0.0),
    # Single element sets
    ({"a"}, {"a"}, 1.0),
    ({"a"}, {"b"}, 0.0),
])
def test_calculate(jaccard_index, a: Set, b: Set, expected: float):
    """
    Test the Jaccard Index calculation with various sets.
    
    Parameters
    ----------
    jaccard_index : JaccardIndex
        The similarity measure instance
    a : Set
        First set for comparison
    b : Set
        Second set for comparison
    expected : float
        Expected similarity value
    """
    result = jaccard_index.calculate(a, b)
    assert result == pytest.approx(expected)

@pytest.mark.unit
def test_calculate_symmetric_property():
    """Test that the calculation satisfies the symmetric property."""
    jaccard_index = JaccardIndex()
    set_a = {"a", "b", "c", "d"}
    set_b = {"c", "d", "e", "f"}
    
    # Calculate similarity in both directions
    sim_a_b = jaccard_index.calculate(set_a, set_b)
    sim_b_a = jaccard_index.calculate(set_b, set_a)
    
    # Verify symmetry
    assert sim_a_b == sim_b_a

@pytest.mark.unit
def test_calculate_reflexive_property():
    """Test that the calculation satisfies the reflexive property."""
    jaccard_index = JaccardIndex()
    set_a = {"a", "b", "c", "d"}
    
    # Calculate similarity of a set with itself
    sim_a_a = jaccard_index.calculate(set_a, set_a)
    
    # Verify reflexivity (maximum similarity)
    assert sim_a_a == 1.0

@pytest.mark.unit
def test_type_error():
    """Test that TypeError is raised when inputs are not sets."""
    jaccard_index = JaccardIndex()
    
    # Test with non-set inputs
    with pytest.raises(TypeError):
        jaccard_index.calculate("not a set", {"a", "b"})
    
    with pytest.raises(TypeError):
        jaccard_index.calculate({"a", "b"}, "not a set")
    
    with pytest.raises(TypeError):
        jaccard_index.calculate([1, 2, 3], [4, 5, 6])

@pytest.mark.unit
def test_serialization():
    """Test serialization and deserialization of the JaccardIndex class."""
    jaccard_index = JaccardIndex()
    serialized = jaccard_index.model_dump_json()
    deserialized = JaccardIndex.model_validate_json(serialized)
    
    # Verify type and bounds are preserved
    assert deserialized.type == "JaccardIndex"
    assert deserialized.is_bounded == jaccard_index.is_bounded
    assert deserialized.lower_bound == jaccard_index.lower_bound
    assert deserialized.upper_bound == jaccard_index.upper_bound