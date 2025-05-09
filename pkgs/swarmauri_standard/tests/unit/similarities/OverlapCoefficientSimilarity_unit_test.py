import pytest
import logging
from swarmauri_standard.swarmauri_standard.similarities.OverlapCoefficientSimilarity import OverlapCoefficientSimilarity

@pytest.fixture
def overlap_coefficient_similarity():
    """
    Fixture to provide an instance of OverlapCoefficientSimilarity for testing.
    """
    instance = OverlapCoefficientSimilarity()
    logging.debug("OverlapCoefficientSimilarity instance created for testing")
    return instance

@pytest.mark.unit
def test_similarity_initialization(overlap_coefficient_similarity):
    """
    Test that the OverlapCoefficientSimilarity instance is properly initialized.
    """
    assert isinstance(overlap_coefficient_similarity, OverlapCoefficientSimilarity)
    assert overlap_coefficient_similarity.type == "OverlapCoefficientSimilarity"
    assert overlap_coefficient_similarity.resource == "Similarity"

@pytest.mark.unit
def test_similarity(overlap_coefficient_similarity):
    """
    Test the similarity calculation with various input pairs.
    """
    # Test with equal sets
    set_a = {1, 2, 3}
    set_b = {1, 2, 3}
    assert overlap_coefficient_similarity.similarity(set_a, set_b) == 1.0

    # Test with partially overlapping sets
    set_c = {1, 2}
    set_d = {2, 3}
    assert overlap_coefficient_similarity.similarity(set_c, set_d) == 0.5

    # Test with disjoint sets
    set_e = {1, 2}
    set_f = {3, 4}
    assert overlap_coefficient_similarity.similarity(set_e, set_f) == 0.0

    # Test with one empty set
    set_g = set()
    set_h = {1, 2}
    assert overlap_coefficient_similarity.similarity(set_g, set_h) == 0.0

    # Test with both empty sets
    set_i = set()
    set_j = set()
    assert overlap_coefficient_similarity.similarity(set_i, set_j) == 0.0

@pytest.mark.unit
def test_dissimilarity(overlap_coefficient_similarity):
    """
    Test the dissimilarity calculation with various input pairs.
    """
    # Test with equal sets
    set_a = {1, 2, 3}
    set_b = {1, 2, 3}
    assert overlap_coefficient_similarity.dissimilarity(set_a, set_b) == 0.0

    # Test with partially overlapping sets
    set_c = {1, 2}
    set_d = {2, 3}
    assert overlap_coefficient_similarity.dissimilarity(set_c, set_d) == 0.5

    # Test with disjoint sets
    set_e = {1, 2}
    set_f = {3, 4}
    assert overlap_coefficient_similarity.dissimilarity(set_e, set_f) == 1.0

    # Test with one empty set
    set_g = set()
    set_h = {1, 2}
    assert overlap_coefficient_similarity.dissimilarity(set_g, set_h) == 1.0

    # Test with both empty sets
    set_i = set()
    set_j = set()
    assert overlap_coefficient_similarity.dissimilarity(set_i, set_j) == 0.0

@pytest.mark.unit
def test_similarities(overlap_coefficient_similarity):
    """
    Test batch similarity calculation with multiple input pairs.
    """
    pairs = [
        ({1, 2}, {2, 3}),
        ({3, 4}, {4, 5}),
        ({5, 6}, {6, 7}),
        (set(), {1, 2}),
        ({1, 2}, set())
    ]
    
    expected_results = [0.5, 0.5, 0.5, 0.0, 0.0]
    
    results = overlap_coefficient_similarity.similarities(pairs)
    assert len(results) == len(pairs)
    for result, expected in zip(results, expected_results):
        assert result == expected

@pytest.mark.unit
def test_dissimilarities(overlap_coefficient_similarity):
    """
    Test batch dissimilarity calculation with multiple input pairs.
    """
    pairs = [
        ({1, 2}, {2, 3}),
        ({3, 4}, {4, 5}),
        ({5, 6}, {6, 7}),
        (set(), {1, 2}),
        ({1, 2}, set())
    ]
    
    expected_results = [0.5, 0.5, 0.5, 1.0, 1.0]
    
    results = overlap_coefficient_similarity.dissimilarities(pairs)
    assert len(results) == len(pairs)
    for result, expected in zip(results, expected_results):
        assert result == expected

@pytest.mark.unit
def test_invalid_inputs(overlap_coefficient_similarity):
    """
    Test that invalid inputs raise appropriate ValueError exceptions.
    """
    # Test non-set inputs
    with pytest.raises(ValueError):
        overlap_coefficient_similarity.similarity([1, 2], [3, 4])
    
    # Test empty sets
    with pytest.raises(ValueError):
        overlap_coefficient_similarity.similarity(set(), set())