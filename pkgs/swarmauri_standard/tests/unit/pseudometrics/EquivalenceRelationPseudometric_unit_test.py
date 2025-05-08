import pytest
import logging
from typing import List, Callable, Any
from swarmauri_standard.pseudometrics.EquivalenceRelationPseudometric import EquivalenceRelationPseudometric

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define some sample equivalence functions for testing
def mod3_equivalence(x: int, y: int) -> bool:
    """
    Equivalence relation based on modulo 3.
    
    Args:
        x: First integer
        y: Second integer
        
    Returns:
        True if x ≡ y (mod 3), False otherwise
    """
    return x % 3 == y % 3

def string_length_equivalence(x: str, y: str) -> bool:
    """
    Equivalence relation based on string length.
    
    Args:
        x: First string
        y: Second string
        
    Returns:
        True if x and y have the same length, False otherwise
    """
    return len(x) == len(y)

def always_true_equivalence(x: Any, y: Any) -> bool:
    """
    Trivial equivalence relation that considers all elements equivalent.
    
    Args:
        x: First element
        y: Second element
        
    Returns:
        Always True
    """
    return True

def broken_equivalence(x: int, y: int) -> bool:
    """
    Broken equivalence relation that violates transitivity.
    
    Args:
        x: First integer
        y: Second integer
        
    Returns:
        A relation that doesn't satisfy transitivity
    """
    # This relation is reflexive and symmetric but not transitive
    if x == y:
        return True
    return (x + y) % 5 == 0


@pytest.fixture
def mod3_pseudometric() -> EquivalenceRelationPseudometric[int]:
    """
    Fixture that creates a pseudometric based on modulo 3 equivalence.
    
    Returns:
        EquivalenceRelationPseudometric instance with mod3 equivalence
    """
    return EquivalenceRelationPseudometric(equivalence_function=mod3_equivalence)


@pytest.fixture
def string_length_pseudometric() -> EquivalenceRelationPseudometric[str]:
    """
    Fixture that creates a pseudometric based on string length equivalence.
    
    Returns:
        EquivalenceRelationPseudometric instance with string length equivalence
    """
    return EquivalenceRelationPseudometric(equivalence_function=string_length_equivalence)


@pytest.mark.unit
def test_initialization():
    """Test that the pseudometric initializes correctly with an equivalence function."""
    # Test with a basic equivalence function
    pseudo = EquivalenceRelationPseudometric(equivalence_function=mod3_equivalence)
    assert pseudo.type == "EquivalenceRelationPseudometric"
    assert callable(pseudo.equivalence_function)
    assert pseudo.equivalence_function(3, 6) is True
    assert pseudo.equivalence_function(3, 7) is False


@pytest.mark.unit
def test_resource_type():
    """Test that the pseudometric has the correct resource type."""
    pseudo = EquivalenceRelationPseudometric(equivalence_function=mod3_equivalence)
    assert pseudo.resource == "Pseudometric"
    assert pseudo.type == "EquivalenceRelationPseudometric"


@pytest.mark.unit
def test_distance_same_class(mod3_pseudometric):
    """Test that points in the same equivalence class have zero distance."""
    # Points in the same equivalence class
    assert mod3_pseudometric.distance(3, 6) == 0.0
    assert mod3_pseudometric.distance(1, 4) == 0.0
    assert mod3_pseudometric.distance(2, 5) == 0.0
    assert mod3_pseudometric.distance(0, 3) == 0.0


@pytest.mark.unit
def test_distance_different_class(mod3_pseudometric):
    """Test that points in different equivalence classes have distance 1."""
    # Points in different equivalence classes
    assert mod3_pseudometric.distance(1, 2) == 1.0
    assert mod3_pseudometric.distance(0, 1) == 1.0
    assert mod3_pseudometric.distance(2, 3) == 1.0


@pytest.mark.unit
def test_distance_with_string_pseudometric(string_length_pseudometric):
    """Test distance calculations with string length equivalence."""
    # Same length strings
    assert string_length_pseudometric.distance("hello", "world") == 0.0
    assert string_length_pseudometric.distance("abc", "xyz") == 0.0
    
    # Different length strings
    assert string_length_pseudometric.distance("hello", "hi") == 1.0
    assert string_length_pseudometric.distance("", "a") == 1.0


@pytest.mark.unit
def test_batch_distance(mod3_pseudometric):
    """Test batch distance calculation."""
    xs = [0, 1, 2, 3, 4]
    ys = [3, 4, 5, 9, 10]
    
    expected = [0.0, 0.0, 0.0, 0.0, 1.0]  # 10 % 3 = 1, not equivalent to 4 % 3 = 1
    result = mod3_pseudometric.batch_distance(xs, ys)
    
    assert result == expected


@pytest.mark.unit
def test_batch_distance_different_lengths(mod3_pseudometric):
    """Test that batch_distance raises an error for different length inputs."""
    xs = [0, 1, 2]
    ys = [3, 4]
    
    with pytest.raises(ValueError) as excinfo:
        mod3_pseudometric.batch_distance(xs, ys)
    
    assert "Input lists must have the same length" in str(excinfo.value)


@pytest.mark.unit
def test_pairwise_distances(mod3_pseudometric):
    """Test pairwise distance calculation."""
    points = [0, 1, 2, 3, 4]
    
    result = mod3_pseudometric.pairwise_distances(points)
    
    # Expected distance matrix:
    # - 0 and 3 are in the same class (mod 3 = 0)
    # - 1 and 4 are in the same class (mod 3 = 1)
    # - 2 is in its own class (mod 3 = 2)
    expected = [
        [0.0, 1.0, 1.0, 0.0, 1.0],  # 0 compared to all
        [1.0, 0.0, 1.0, 1.0, 0.0],  # 1 compared to all
        [1.0, 1.0, 0.0, 1.0, 1.0],  # 2 compared to all
        [0.0, 1.0, 1.0, 0.0, 1.0],  # 3 compared to all
        [1.0, 0.0, 1.0, 1.0, 0.0],  # 4 compared to all
    ]
    
    assert result == expected


@pytest.mark.unit
def test_validate_equivalence_properties_valid():
    """Test validation of valid equivalence properties."""
    # Test with mod3 equivalence (which is a valid equivalence relation)
    pseudo = EquivalenceRelationPseudometric(equivalence_function=mod3_equivalence)
    sample_points = [0, 1, 2, 3, 4, 5, 6]
    
    assert pseudo.validate_equivalence_properties(sample_points) is True


@pytest.mark.unit
def test_validate_equivalence_properties_trivial():
    """Test validation with trivial equivalence relation."""
    # Test with trivial equivalence (all elements equivalent)
    pseudo = EquivalenceRelationPseudometric(equivalence_function=always_true_equivalence)
    sample_points = ["a", 1, None, True, [1, 2, 3]]
    
    assert pseudo.validate_equivalence_properties(sample_points) is True


@pytest.mark.unit
def test_validate_equivalence_properties_broken():
    """Test validation with a broken equivalence relation."""
    # Test with broken equivalence (violates transitivity)
    pseudo = EquivalenceRelationPseudometric(equivalence_function=broken_equivalence)
    
    # We need specific points that demonstrate the transitivity violation:
    # broken_equivalence(1, 4) = True (1+4=5, which is divisible by 5)
    # broken_equivalence(4, 6) = True (4+6=10, which is divisible by 5)
    # broken_equivalence(1, 6) = False (1+6=7, which is not divisible by 5)
    sample_points = [1, 4, 6]
    
    assert pseudo.validate_equivalence_properties(sample_points) is False


@pytest.mark.unit
@pytest.mark.parametrize("x,y,expected", [
    (0, 3, 0.0),  # same class
    (1, 7, 0.0),  # same class
    (2, 8, 0.0),  # same class
    (1, 2, 1.0),  # different classes
    (0, 1, 1.0),  # different classes
])
def test_distance_parameterized(mod3_pseudometric, x, y, expected):
    """Parameterized test for distance calculation."""
    assert mod3_pseudometric.distance(x, y) == expected


@pytest.mark.unit
def test_pseudometric_properties(mod3_pseudometric):
    """Test that the pseudometric satisfies the required properties."""
    # Sample points
    points = [0, 1, 2, 3, 4, 5]
    
    # Non-negativity: d(x,y) >= 0
    for x in points:
        for y in points:
            assert mod3_pseudometric.distance(x, y) >= 0.0
    
    # Identity of indiscernibles (one direction): d(x,x) = 0
    for x in points:
        assert mod3_pseudometric.distance(x, x) == 0.0
    
    # Symmetry: d(x,y) = d(y,x)
    for x in points:
        for y in points:
            assert mod3_pseudometric.distance(x, y) == mod3_pseudometric.distance(y, x)
    
    # Triangle inequality: d(x,z) <= d(x,y) + d(y,z)
    for x in points:
        for y in points:
            for z in points:
                assert mod3_pseudometric.distance(x, z) <= (
                    mod3_pseudometric.distance(x, y) + mod3_pseudometric.distance(y, z)
                )