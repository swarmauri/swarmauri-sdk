import pytest
import logging
from collections import Counter
from typing import Dict, Set, List, Union

from swarmauri_standard.similarities.Dice import Dice

# Set up logging for tests
logger = logging.getLogger(__name__)


@pytest.fixture
def dice_similarity():
    """
    Fixture providing a Dice similarity instance for testing.
    
    Returns
    -------
    Dice
        An instance of Dice similarity measure
    """
    return Dice()


@pytest.mark.unit
def test_dice_initialization():
    """Test that Dice similarity measure initializes correctly."""
    dice = Dice()
    assert dice.type == "Dice"
    assert dice.resource == "Similarity"
    assert dice.is_bounded is True
    assert dice.lower_bound == 0.0
    assert dice.upper_bound == 1.0


@pytest.mark.unit
def test_dice_string_representation():
    """Test the string representation of Dice similarity."""
    dice = Dice()
    assert str(dice) == "Dice Similarity (bounds: [0.0, 1.0])"


@pytest.mark.unit
def test_dice_properties():
    """Test the basic properties of Dice similarity."""
    dice = Dice()
    assert dice.is_reflexive() is True
    assert dice.is_symmetric() is True


@pytest.mark.unit
@pytest.mark.parametrize(
    "a, b, expected", [
        # Sets
        ({"a", "b", "c"}, {"a", "c", "d"}, 0.5),
        ({"a", "b", "c"}, {"a", "b", "c"}, 1.0),
        ({"a", "b", "c"}, {"d", "e", "f"}, 0.0),
        (set(), set(), 1.0),  # Empty sets should return 1.0
        ({"a", "b"}, set(), 0.0),
        
        # Lists
        (["a", "b", "c"], ["a", "c", "d"], 0.5),
        (["a", "b", "c"], ["a", "b", "c"], 1.0),
        (["a", "b", "c"], ["d", "e", "f"], 0.0),
        ([], [], 1.0),  # Empty lists should return 1.0
        (["a", "b"], [], 0.0),
        
        # Lists with duplicates (multisets)
        (["a", "a", "b"], ["a", "b", "b"], 2/3),
        (["a", "a", "a"], ["a", "a"], 0.8),
        (["a", "a", "b", "c"], ["a", "d", "e"], 1/5),
    ]
)
def test_dice_calculate_with_different_collections(
    dice_similarity: Dice, a: Union[Set[str], List[str]], b: Union[Set[str], List[str]], expected: float
):
    """
    Test Dice similarity calculation with different collection types.
    
    Parameters
    ----------
    dice_similarity : Dice
        Dice similarity instance
    a : Union[Set[str], List[str]]
        First collection
    b : Union[Set[str], List[str]]
        Second collection
    expected : float
        Expected similarity value
    """
    result = dice_similarity.calculate(a, b)
    assert pytest.approx(result, abs=1e-10) == expected


@pytest.mark.unit
def test_dice_with_counters():
    """Test Dice similarity with Counter objects."""
    dice = Dice()
    a = Counter(["a", "a", "b", "c"])
    b = Counter(["a", "b", "b", "d"])
    
    # Expected: 2 * (1 'a' + 1 'b') / (4 + 4) = 2 * 2 / 8 = 0.5
    assert pytest.approx(dice.calculate(a, b), abs=1e-10) == 0.5


@pytest.mark.unit
def test_dice_with_dictionaries():
    """Test Dice similarity with dictionaries representing multisets."""
    dice = Dice()
    a = {"a": 2, "b": 1, "c": 1}
    b = {"a": 1, "b": 2, "d": 1}
    
    # Expected: 2 * (1 'a' + 1 'b') / (4 + 4) = 2 * 2 / 8 = 0.5
    assert pytest.approx(dice.calculate(a, b), abs=1e-10) == 0.5


@pytest.mark.unit
def test_dice_edge_cases():
    """Test Dice similarity with edge cases."""
    dice = Dice()
    
    # Empty collections
    assert dice.calculate([], []) == 1.0
    assert dice.calculate({}, {}) == 1.0
    assert dice.calculate(Counter(), Counter()) == 1.0
    
    # One empty collection
    assert dice.calculate(["a", "b"], []) == 0.0
    assert dice.calculate(set(), {"a", "b"}) == 0.0
    assert dice.calculate(Counter(["a", "b"]), Counter()) == 0.0


@pytest.mark.unit
def test_dice_serialization():
    """Test that Dice objects can be serialized and deserialized correctly."""
    dice = Dice()
    serialized = dice.model_dump_json()
    deserialized = Dice.model_validate_json(serialized)
    
    assert isinstance(deserialized, Dice)
    assert deserialized.type == dice.type
    assert deserialized.resource == dice.resource
    assert deserialized.is_bounded == dice.is_bounded
    assert deserialized.lower_bound == dice.lower_bound
    assert deserialized.upper_bound == dice.upper_bound