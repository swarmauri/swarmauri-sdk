import logging
from collections import Counter

import pytest
from swarmauri_base.ComponentBase import ResourceTypes
from swarmauri_base.similarities.SimilarityBase import SimilarityBase

from swarmauri_standard.similarities.DiceSimilarity import DiceSimilarity

# Set up logger
logger = logging.getLogger(__name__)


@pytest.fixture
def dice_similarity():
    """
    Fixture that provides a DiceSimilarity instance for tests.

    Returns
    -------
    DiceSimilarity
        An instance of DiceSimilarity
    """
    return DiceSimilarity()


@pytest.mark.unit
def test_inheritance():
    """
    Test that DiceSimilarity inherits from SimilarityBase.
    """
    dice_similarity = DiceSimilarity()
    assert isinstance(dice_similarity, SimilarityBase)


@pytest.mark.unit
def test_resource(dice_similarity):
    """
    Test that the resource attribute is correctly set.
    """
    assert dice_similarity.resource == ResourceTypes.SIMILARITY.value


@pytest.mark.unit
def test_type(dice_similarity):
    """
    Test that the type attribute is correctly set.
    """
    assert dice_similarity.type == "DiceSimilarity"


@pytest.mark.unit
def test_initialization():
    """
    Test that the DiceSimilarity can be initialized.
    """
    dice_similarity = DiceSimilarity()
    assert dice_similarity is not None
    assert dice_similarity.type == "DiceSimilarity"
    assert dice_similarity.resource == ResourceTypes.SIMILARITY.value


@pytest.mark.unit
def test_serialization(dice_similarity):
    """
    Test serialization and deserialization of DiceSimilarity.

    Parameters
    ----------
    dice_similarity : DiceSimilarity
        Instance of DiceSimilarity from fixture
    """
    serialized = dice_similarity.model_dump_json()
    deserialized = DiceSimilarity.model_validate_json(serialized)

    assert deserialized.type == dice_similarity.type
    assert deserialized.resource == dice_similarity.resource


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y, expected",
    [
        # Lists
        ([1, 2, 3], [2, 3, 4], 0.5),
        ([1, 2, 3], [1, 2, 3], 1.0),
        ([1, 2, 3], [4, 5, 6], 0.0),
        # Sets
        (set([1, 2, 3]), set([2, 3, 4]), 0.5),
        (set([1, 2, 3]), set([1, 2, 3]), 1.0),
        (set([1, 2, 3]), set([4, 5, 6]), 0.0),
        # Strings
        ("abc", "bcd", 0.4),
        ("abc", "abc", 1.0),
        ("abc", "def", 0.0),
        # Empty sets
        ([], [], 1.0),
        (set(), set(), 1.0),
        ("", "", 1.0),
        # Mixed types
        ([1, 2, 3], "123", 1.0),
    ],
)
def test_similarity(dice_similarity, x, y, expected):
    """
    Test the similarity method with various inputs.

    Parameters
    ----------
    dice_similarity : DiceSimilarity
        Instance of DiceSimilarity from fixture
    x : Any
        First object to compare
    y : Any
        Second object to compare
    expected : float
        Expected similarity value
    """
    result = dice_similarity.similarity(x, y)
    assert abs(result - expected) < 1e-10


@pytest.mark.unit
def test_convert_to_counter(dice_similarity):
    """
    Test the _convert_to_counter method with various inputs.

    Parameters
    ----------
    dice_similarity : DiceSimilarity
        Instance of DiceSimilarity from fixture
    """
    # Test with list
    counter = dice_similarity._convert_to_counter([1, 2, 2, 3])
    assert counter == Counter({1: 1, 2: 2, 3: 1})

    # Test with tuple
    counter = dice_similarity._convert_to_counter((1, 2, 2, 3))
    assert counter == Counter({1: 1, 2: 2, 3: 1})

    # Test with set
    counter = dice_similarity._convert_to_counter({1, 2, 3})
    assert counter == Counter({1: 1, 2: 1, 3: 1})

    # Test with string
    counter = dice_similarity._convert_to_counter("abbc")
    assert counter == Counter({"a": 1, "b": 2, "c": 1})

    # Test with dict
    counter = dice_similarity._convert_to_counter({"a": 1, "b": 2})
    assert counter == Counter({"a": 1, "b": 1})

    # Test with Counter
    original_counter = Counter({1: 1, 2: 2, 3: 1})
    counter = dice_similarity._convert_to_counter(original_counter)
    assert counter == original_counter


@pytest.mark.unit
def test_convert_to_counter_errors(dice_similarity):
    """
    Test that _convert_to_counter raises appropriate errors for invalid inputs.

    Parameters
    ----------
    dice_similarity : DiceSimilarity
        Instance of DiceSimilarity from fixture
    """
    # Test with an object that can't be converted to a Counter
    with pytest.raises(TypeError):
        dice_similarity._convert_to_counter(123)


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, ys, expected",
    [
        # Multiple comparisons with lists
        ([1, 2, 3], [[2, 3, 4], [1, 2, 3], [4, 5, 6]], [0.5, 1.0, 0.0]),
        # Multiple comparisons with strings
        ("abc", ["bcd", "abc", "def"], [0.4, 1.0, 0.0]),
        # Empty sets
        ([], [[], [1, 2], []], [1.0, 0.0, 1.0]),
    ],
)
def test_similarities(dice_similarity, x, ys, expected):
    """
    Test the similarities method with various inputs.

    Parameters
    ----------
    dice_similarity : DiceSimilarity
        Instance of DiceSimilarity from fixture
    x : Any
        Reference object
    ys : List[Any]
        List of objects to compare against the reference
    expected : List[float]
        Expected similarity values
    """
    results = dice_similarity.similarities(x, ys)
    assert len(results) == len(expected)
    for result, exp in zip(results, expected):
        assert abs(result - exp) < 1e-10


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y, expected",
    [
        # Lists
        ([1, 2, 3], [2, 3, 4], 0.5),
        ([1, 2, 3], [1, 2, 3], 0.0),
        ([1, 2, 3], [4, 5, 6], 1.0),
    ],
)
def test_dissimilarity(dice_similarity, x, y, expected):
    """
    Test the dissimilarity method with various inputs.

    Parameters
    ----------
    dice_similarity : DiceSimilarity
        Instance of DiceSimilarity from fixture
    x : Any
        First object to compare
    y : Any
        Second object to compare
    expected : float
        Expected dissimilarity value
    """
    result = dice_similarity.dissimilarity(x, y)
    assert abs(result - expected) < 1e-10


@pytest.mark.unit
def test_check_bounded(dice_similarity):
    """
    Test that the check_bounded method returns True.

    Parameters
    ----------
    dice_similarity : DiceSimilarity
        Instance of DiceSimilarity from fixture
    """
    assert dice_similarity.check_bounded() is True


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y",
    [
        ([1, 2, 3], [2, 3, 4]),
        ("abc", "bcd"),
        (set([1, 2, 3]), set([2, 3, 4])),
        ([1, 1, 2, 3], [1, 2, 2, 3]),
    ],
)
def test_check_symmetry(dice_similarity, x, y):
    """
    Test that the check_symmetry method returns True for various inputs.

    Parameters
    ----------
    dice_similarity : DiceSimilarity
        Instance of DiceSimilarity from fixture
    x : Any
        First object to compare
    y : Any
        Second object to compare
    """
    assert dice_similarity.check_symmetry(x, y) is True


@pytest.mark.unit
def test_symmetry_direct_comparison(dice_similarity):
    """
    Test symmetry by directly comparing similarity(x,y) and similarity(y,x).

    Parameters
    ----------
    dice_similarity : DiceSimilarity
        Instance of DiceSimilarity from fixture
    """
    x = [1, 2, 3, 3]
    y = [2, 3, 4, 4]

    similarity_xy = dice_similarity.similarity(x, y)
    similarity_yx = dice_similarity.similarity(y, x)

    assert abs(similarity_xy - similarity_yx) < 1e-10
