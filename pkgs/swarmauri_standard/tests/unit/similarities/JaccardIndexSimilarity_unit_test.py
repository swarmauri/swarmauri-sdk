import pytest
import logging
from typing import Union, List, Tuple
from swarmauri_standard.swarmauri_standard.similarities.JaccardIndexSimilarity import JaccardIndexSimilarity

# Set up basic logging configuration
logging.basicConfig(level=logging.DEBUG)

@pytest.fixture
def jaccard_index_similarity() -> JaccardIndexSimilarity:
    """Fixture providing a JaccardIndexSimilarity instance for testing."""
    return JaccardIndexSimilarity()

@pytest.mark.unit
def test_similarity_empty_sets(jaccard_index_similarity: JaccardIndexSimilarity) -> None:
    """Test Jaccard Index similarity calculation with empty sets."""
    assert jaccard_index_similarity.similarity(set(), set()) == 1.0

@pytest.mark.unit
def test_similarity_identical_sets(jaccard_index_similarity: JaccardIndexSimilarity) -> None:
    """Test Jaccard Index similarity when input sets are identical."""
    test_set = {"a", "b", "c"}
    assert jaccard_index_similarity.similarity(test_set, test_set) == 1.0

@pytest.mark.unit
def test_similarity_disjoint_sets(jaccard_index_similarity: JaccardIndexSimilarity) -> None:
    """Test Jaccard Index similarity when input sets are disjoint."""
    set1 = {"a", "b"}
    set2 = {"c", "d"}
    assert jaccard_index_similarity.similarity(set1, set2) == 0.0

@pytest.mark.unit
def test_similarity_overlapping_sets(jaccard_index_similarity: JaccardIndexSimilarity) -> None:
    """Test Jaccard Index similarity with partially overlapping sets."""
    set1 = {"a", "b", "c"}
    set2 = {"b", "c", "d"}
    assert jaccard_index_similarity.similarity(set1, set2) == 2/5 == 0.4

@pytest.mark.unit
def test_similarity_with_different_types(jaccard_index_similarity: JaccardIndexSimilarity) -> None:
    """Test Jaccard Index similarity with different input types (list, tuple)."""
    list_input = ["a", "b", "c"]
    tuple_input = ("b", "c", "d")
    
    similarity_list = jaccard_index_similarity.similarity(list_input, tuple_input)
    assert similarity_list == 2/5 == 0.4

@pytest.mark.unit
def test_similarities_single(jaccard_index_similarity: JaccardIndexSimilarity) -> None:
    """Test similarities method with a single set."""
    set1 = {"a", "b"}
    set2 = {"b", "c"}
    result = jaccard_index_similarity.similarities(set1, set2)
    assert isinstance(result, float) and result == 0.5

@pytest.mark.unit
def test_similarities_batch(jaccard_index_similarity: JaccardIndexSimilarity) -> None:
    """Test similarities method with multiple sets."""
    set1 = {"a", "b"}
    set2 = {"b", "c"}
    set3 = {"d", "e"}
    
    results = jaccard_index_similarity.similarities(set1, [set2, set3])
    assert isinstance(results, list) and len(results) == 2
    assert results[0] == 0.5 and results[1] == 0.0

@pytest.mark.unit
def test_dissimilarity(jaccard_index_similarity: JaccardIndexSimilarity) -> None:
    """Test dissimilarity calculation."""
    set1 = {"a", "b"}
    set2 = {"b", "c"}
    assert jaccard_index_similarity.dissimilarity(set1, set2) == 0.5

@pytest.mark.unit
def test_dissimilarities(jaccard_index_similarity: JaccardIndexSimilarity) -> None:
    """Test dissimilarities method with multiple sets."""
    set1 = {"a", "b"}
    set2 = {"b", "c"}
    set3 = {"d", "e"}
    
    results = jaccard_index_similarity.dissimilarities(set1, [set2, set3])
    assert isinstance(results, list) and len(results) == 2
    assert results[0] == 0.5 and results[1] == 1.0

@pytest.mark.unit
def test_check_boundedness(jaccard_index_similarity: JaccardIndexSimilarity) -> None:
    """Test if the similarity measure is bounded between 0 and 1."""
    assert jaccard_index_similarity.check_boundedness({"a"}, {"a"}) is True

@pytest.mark.unit
def test_check_reflexivity(jaccard_index_similarity: JaccardIndexSimilarity) -> None:
    """Test if the similarity measure is reflexive."""
    test_set = {"a", "b", "c"}
    assert jaccard_index_similarity.check_reflexivity(test_set) is True

@pytest.mark.unit
def test_check_symmetry(jaccard_index_similarity: JaccardIndexSimilarity) -> None:
    """Test if the similarity measure is symmetric."""
    set1 = {"a", "b"}
    set2 = {"b", "c"}
    assert jaccard_index_similarity.check_symmetry(set1, set2) is True

@pytest.mark.unit
def test_check_identity(jaccard_index_similarity: JaccardIndexSimilarity) -> None:
    """Test if the similarity measure satisfies identity."""
    set1 = {"a", "b"}
    set2 = {"a", "b"}
    assert jaccard_index_similarity.check_identity(set1, set2) is True

@pytest.mark.unit
@pytest.mark.parametrize("x,y,expected", [
    ({"a", "b"}, {"b", "c"}, 0.5),
    ({"a"}, {"a", "b"}, 0.5),
    ({"x", "y", "z"}, {"a", "b", "c"}, 0.0),
])
def test_similarity_parametrized(jaccard_index_similarity: JaccardIndexSimilarity, x, y, expected) -> None:
    """Parametrized test for similarity method with various inputs."""
    assert jaccard_index_similarity.similarity(x, y) == expected

@pytest.mark.unit
def test_similarity_value_range(jaccard_index_similarity: JaccardIndexSimilarity) -> None:
    """Test if similarity values stay within valid range [0,1]."""
    # Test with empty sets
    assert 0.0 <= jaccard_index_similarity.similarity(set(), set()) <= 1.0
    # Test with identical sets
    test_set = {"a", "b", "c"}
    assert 0.0 <= jaccard_index_similarity.similarity(test_set, test_set) <= 1.0
    # Test with disjoint sets
    set1 = {"a", "b"}
    set2 = {"c", "d"}
    assert 0.0 <= jaccard_index_similarity.similarity(set1, set2) <= 1.0