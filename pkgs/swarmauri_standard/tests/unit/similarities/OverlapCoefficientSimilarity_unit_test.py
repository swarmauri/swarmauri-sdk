import logging

import pytest

from swarmauri_standard.similarities.OverlapCoefficientSimilarity import (
    OverlapCoefficientSimilarity,
)

# Set up logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def overlap_similarity():
    """
    Fixture that returns an instance of OverlapCoefficientSimilarity.

    Returns
    -------
    OverlapCoefficientSimilarity
        An instance of the OverlapCoefficientSimilarity class
    """
    return OverlapCoefficientSimilarity()


@pytest.mark.unit
def test_initialization():
    """Test proper initialization of OverlapCoefficientSimilarity."""
    overlap_sim = OverlapCoefficientSimilarity()
    assert overlap_sim.type == "OverlapCoefficientSimilarity"
    assert overlap_sim.resource == "Similarity"


@pytest.mark.unit
def test_convert_to_set(overlap_similarity):
    """Test the _convert_to_set method with various inputs."""
    # Test with already a set
    input_set = {1, 2, 3}
    assert overlap_similarity._convert_to_set(input_set) == input_set

    # Test with list
    assert overlap_similarity._convert_to_set([1, 2, 3]) == {1, 2, 3}

    # Test with tuple
    assert overlap_similarity._convert_to_set((1, 2, 3)) == {1, 2, 3}

    # Test with string
    assert overlap_similarity._convert_to_set("abc") == {"a", "b", "c"}

    # Test with dictionary (should convert keys to set)
    assert overlap_similarity._convert_to_set({"a": 1, "b": 2}) == {"a", "b"}


@pytest.mark.unit
def test_convert_to_set_error(overlap_similarity):
    """Test error handling in _convert_to_set method."""
    # Test with non-convertible type
    with pytest.raises(TypeError):
        overlap_similarity._convert_to_set(123)  # Integer is not iterable


@pytest.mark.unit
@pytest.mark.parametrize(
    "set_a, set_b, expected",
    [
        # Identical sets
        ({1, 2, 3}, {1, 2, 3}, 1.0),
        # One set is subset of the other
        ({1, 2}, {1, 2, 3, 4}, 1.0),
        ({1, 2, 3, 4}, {1, 2}, 1.0),
        # Partial overlap
        ({1, 2, 3}, {2, 3, 4}, 0.6666666666666666),
        # No overlap
        ({1, 2, 3}, {4, 5, 6}, 0.0),
        # Using strings
        ({"a", "b", "c"}, {"b", "c", "d"}, 0.6666666666666666),
        # Using mixed types
        ({1, "a", 3.14}, {1, "a", "b"}, 0.6666666666666666),
    ],
)
def test_similarity(overlap_similarity, set_a, set_b, expected):
    """Test similarity calculation with various inputs."""
    result = overlap_similarity.similarity(set_a, set_b)
    assert abs(result - expected) < 1e-10


@pytest.mark.unit
def test_similarity_with_collections(overlap_similarity):
    """Test similarity with different collection types."""
    # Lists
    assert (
        abs(overlap_similarity.similarity([1, 2, 3], [2, 3, 4]) - 0.6666666666666666)
        < 1e-10
    )

    # Tuples
    assert (
        abs(overlap_similarity.similarity((1, 2, 3), (2, 3, 4)) - 0.6666666666666666)
        < 1e-10
    )

    # Strings
    assert abs(overlap_similarity.similarity("abc", "bcd") - 0.6666666666666666) < 1e-10

    # Mixed
    assert (
        abs(overlap_similarity.similarity({1, 2, 3}, [2, 3, 4]) - 0.6666666666666666)
        < 1e-10
    )


@pytest.mark.unit
def test_similarity_with_duplicates(overlap_similarity):
    """Test similarity with collections containing duplicates."""
    # With lists containing duplicates (should be converted to sets)
    assert (
        abs(
            overlap_similarity.similarity([1, 2, 2, 3], [2, 3, 3, 4])
            - 0.6666666666666666
        )
        < 1e-10
    )


@pytest.mark.unit
def test_similarity_empty_sets(overlap_similarity):
    """Test error handling for empty sets."""
    with pytest.raises(ValueError):
        overlap_similarity.similarity(set(), {1, 2, 3})

    with pytest.raises(ValueError):
        overlap_similarity.similarity({1, 2, 3}, set())

    with pytest.raises(ValueError):
        overlap_similarity.similarity(set(), set())


@pytest.mark.unit
def test_similarities(overlap_similarity):
    """Test similarities method with multiple comparisons."""
    x = {1, 2, 3}
    ys = [
        {1, 2, 3},  # identical
        {1, 2},  # subset
        {2, 3, 4},  # partial overlap
        {4, 5, 6},  # no overlap
    ]

    expected = [1.0, 1.0, 0.6666666666666666, 0.0]
    results = overlap_similarity.similarities(x, ys)

    assert len(results) == len(expected)
    for result, exp in zip(results, expected):
        assert abs(result - exp) < 1e-10


@pytest.mark.unit
def test_similarities_empty_sets(overlap_similarity):
    """Test error handling for empty sets in similarities method."""
    x = {1, 2, 3}
    ys = [{1, 2}, set(), {3, 4}]

    with pytest.raises(ValueError):
        overlap_similarity.similarities(x, ys)

    with pytest.raises(ValueError):
        overlap_similarity.similarities(set(), ys)


@pytest.mark.unit
@pytest.mark.parametrize(
    "set_a, set_b, expected",
    [
        ({1, 2, 3}, {1, 2, 3}, 0.0),
        ({1, 2}, {1, 2, 3, 4}, 0.0),
        ({1, 2, 3}, {2, 3, 4}, 0.3333333333333333),
        ({1, 2, 3}, {4, 5, 6}, 1.0),
    ],
)
def test_dissimilarity(overlap_similarity, set_a, set_b, expected):
    """Test dissimilarity calculation."""
    result = overlap_similarity.dissimilarity(set_a, set_b)
    assert abs(result - expected) < 1e-10


@pytest.mark.unit
def test_check_bounded(overlap_similarity):
    """Test check_bounded method."""
    assert overlap_similarity.check_bounded() is True


@pytest.mark.unit
def test_check_reflexivity(overlap_similarity):
    """Test check_reflexivity method."""
    assert overlap_similarity.check_reflexivity({1, 2, 3}) is True

    # Test with other collection types
    assert overlap_similarity.check_reflexivity([1, 2, 3]) is True
    assert overlap_similarity.check_reflexivity("abc") is True

    # Test error handling
    with pytest.raises(ValueError):
        overlap_similarity.check_reflexivity(set())


@pytest.mark.unit
def test_check_symmetry(overlap_similarity):
    """Test check_symmetry method."""
    assert overlap_similarity.check_symmetry({1, 2, 3}, {2, 3, 4}) is True

    # Test with other collection types
    assert overlap_similarity.check_symmetry([1, 2, 3], [2, 3, 4]) is True
    assert overlap_similarity.check_symmetry("abc", "bcd") is True


@pytest.mark.unit
def test_check_identity_of_discernibles(overlap_similarity):
    """Test check_identity_of_discernibles method."""
    # Identical sets should return True
    assert (
        overlap_similarity.check_identity_of_discernibles({1, 2, 3}, {1, 2, 3}) is True
    )

    # Different sets with similarity = 1 (one is subset of other) should return False
    assert overlap_similarity.check_identity_of_discernibles({1, 2}, {1, 2, 3}) is False

    # Different sets with similarity < 1 should return True
    assert (
        overlap_similarity.check_identity_of_discernibles({1, 2, 3}, {2, 3, 4}) is True
    )

    # Test with other collection types
    assert overlap_similarity.check_identity_of_discernibles([1, 2], [1, 2, 3]) is False
    assert overlap_similarity.check_identity_of_discernibles("ab", "abc") is False


@pytest.mark.unit
def test_serialization():
    """Test serialization and deserialization of the component."""
    original = OverlapCoefficientSimilarity()
    serialized = original.model_dump_json()
    deserialized = OverlapCoefficientSimilarity.model_validate_json(serialized)

    assert deserialized.type == original.type
    assert deserialized.resource == original.resource
