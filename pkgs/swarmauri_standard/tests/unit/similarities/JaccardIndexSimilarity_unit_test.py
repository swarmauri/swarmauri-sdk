import pytest
import logging
from typing import Set
from swarmauri_standard.similarities.JaccardIndexSimilarity import (
    JaccardIndexSimilarity,
)

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def jaccard_similarity():
    """
    Fixture that provides a JaccardIndexSimilarity instance.

    Returns
    -------
    JaccardIndexSimilarity
        An instance of the JaccardIndexSimilarity class
    """
    return JaccardIndexSimilarity()


@pytest.mark.unit
def test_initialization():
    """Test proper initialization of JaccardIndexSimilarity."""
    similarity = JaccardIndexSimilarity()
    assert similarity.type == "JaccardIndexSimilarity"
    assert similarity.resource == "Similarity"


@pytest.mark.unit
def test_serialization(jaccard_similarity):
    """Test serialization and deserialization of JaccardIndexSimilarity."""
    # Serialize to JSON
    serialized = jaccard_similarity.model_dump_json()

    # Deserialize from JSON
    deserialized = JaccardIndexSimilarity.model_validate_json(serialized)

    # Verify the deserialized object matches the original
    assert deserialized.type == jaccard_similarity.type
    assert deserialized.resource == jaccard_similarity.resource


@pytest.mark.unit
@pytest.mark.parametrize(
    "set_a, set_b, expected",
    [
        (set([1, 2, 3]), set([2, 3, 4]), 0.5),  # 2 common elements, 4 total unique
        (set([1, 2, 3, 4]), set([1, 2, 3, 4]), 1.0),  # Identical sets
        (set([1, 2, 3]), set([4, 5, 6]), 0.0),  # No common elements
        (set([]), set([]), 1.0),  # Both empty sets
        (set([1, 2]), set([]), 0.0),  # One empty set
        (set(["a", "b", "c"]), set(["b", "c", "d"]), 0.5),  # String elements
        (set([1, 2, 3]), set([1, 2, 3, 4, 5]), 0.6),  # Subset relation
    ],
)
def test_similarity(jaccard_similarity, set_a: Set, set_b: Set, expected: float):
    """
    Test the similarity method with various sets.

    Parameters
    ----------
    jaccard_similarity : JaccardIndexSimilarity
        The similarity measure instance
    set_a : Set
        First set to compare
    set_b : Set
        Second set to compare
    expected : float
        Expected similarity value
    """
    result = jaccard_similarity.similarity(set_a, set_b)
    assert result == pytest.approx(expected)


@pytest.mark.unit
def test_similarity_type_error(jaccard_similarity):
    """Test that TypeError is raised when inputs are not sets."""
    with pytest.raises(TypeError):
        jaccard_similarity.similarity("not a set", set([1, 2, 3]))

    with pytest.raises(TypeError):
        jaccard_similarity.similarity(set([1, 2, 3]), "not a set")

    with pytest.raises(TypeError):
        jaccard_similarity.similarity([1, 2, 3], [4, 5, 6])


@pytest.mark.unit
def test_similarities(jaccard_similarity):
    """Test the similarities method with multiple comparison sets."""
    reference_set = set([1, 2, 3])
    comparison_sets = [
        set([1, 2, 3, 4]),  # Expected: 0.75
        set([3, 4, 5]),  # Expected: 0.2
        set([1, 2, 3]),  # Expected: 1.0
        set([4, 5, 6]),  # Expected: 0.0
    ]

    expected_results = [0.75, 0.2, 1.0, 0.0]
    results = jaccard_similarity.similarities(reference_set, comparison_sets)

    assert len(results) == len(expected_results)
    for result, expected in zip(results, expected_results):
        assert result == pytest.approx(expected)


@pytest.mark.unit
def test_similarities_type_error(jaccard_similarity):
    """Test that TypeError is raised when inputs to similarities are not sets."""
    with pytest.raises(TypeError):
        jaccard_similarity.similarities("not a set", [set([1, 2, 3])])

    with pytest.raises(TypeError):
        jaccard_similarity.similarities(set([1, 2, 3]), [set([1, 2]), "not a set"])


@pytest.mark.unit
@pytest.mark.parametrize(
    "set_a, set_b, expected",
    [
        (set([1, 2, 3]), set([2, 3, 4]), 0.5),
        (set([1, 2, 3, 4]), set([1, 2, 3, 4]), 0.0),
        (set([1, 2, 3]), set([4, 5, 6]), 1.0),
    ],
)
def test_dissimilarity(jaccard_similarity, set_a: Set, set_b: Set, expected: float):
    """
    Test the dissimilarity method with various sets.

    Parameters
    ----------
    jaccard_similarity : JaccardIndexSimilarity
        The similarity measure instance
    set_a : Set
        First set to compare
    set_b : Set
        Second set to compare
    expected : float
        Expected dissimilarity value
    """
    result = jaccard_similarity.dissimilarity(set_a, set_b)
    assert result == pytest.approx(expected)


@pytest.mark.unit
def test_check_bounded(jaccard_similarity):
    """Test that the similarity measure correctly reports it is bounded."""
    assert jaccard_similarity.check_bounded() is True


@pytest.mark.unit
def test_check_symmetry(jaccard_similarity):
    """Test that the similarity measure correctly reports it is symmetric."""
    set_a = set([1, 2, 3])
    set_b = set([3, 4, 5])
    assert jaccard_similarity.check_symmetry(set_a, set_b) is True


@pytest.mark.unit
def test_check_symmetry_type_error(jaccard_similarity):
    """Test that TypeError is raised when inputs to check_symmetry are not sets."""
    with pytest.raises(TypeError):
        jaccard_similarity.check_symmetry("not a set", set([1, 2, 3]))

    with pytest.raises(TypeError):
        jaccard_similarity.check_symmetry(set([1, 2, 3]), "not a set")


@pytest.mark.unit
def test_symmetry_property(jaccard_similarity):
    """Test that the similarity measure is actually symmetric."""
    set_a = set([1, 2, 3])
    set_b = set([3, 4, 5])

    similarity_ab = jaccard_similarity.similarity(set_a, set_b)
    similarity_ba = jaccard_similarity.similarity(set_b, set_a)

    assert similarity_ab == pytest.approx(similarity_ba)
