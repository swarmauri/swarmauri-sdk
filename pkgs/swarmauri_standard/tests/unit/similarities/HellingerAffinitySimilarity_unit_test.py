import pytest
import numpy as np
from swarmauri_standard.swarmauri_standard.similarities.HellingerAffinitySimilarity import HellingerAffinitySimilarity

@pytest.fixture
def hellinger_affinity_similarity():
    """Fixture to create an instance of HellingerAffinitySimilarity"""
    return HellingerAffinitySimilarity()

@pytest.mark.unit
def test_similarity_with_valid_distributions(hellinger_affinity_similarity):
    """Test similarity method with valid probability distributions"""
    a = np.array([0.5, 0.5])
    b = np.array([0.5, 0.5])
    assert hellinger_affinity_similarity.similarity(a, b) == 1.0

@pytest.mark.unit
def test_similarity_with_different_distributions(hellinger_affinity_similarity):
    """Test similarity method with different distributions"""
    a = np.array([1.0, 0.0])
    b = np.array([0.0, 1.0])
    similarity_score = hellinger_affinity_similarity.similarity(a, b)
    assert 0.0 <= similarity_score <= 1.0

@pytest.mark.unit
def test_similarity_with_none_inputs(hellinger_affinity_similarity):
    """Test similarity method with None inputs"""
    assert hellinger_affinity_similarity.similarity(None, None) == 1.0
    assert hellinger_affinity_similarity.similarity(None, np.array([0.5, 0.5])) == 0.0

@pytest.mark.unit
def test_similarity_with_invalid_distributions(hellinger_affinity_similarity):
    """Test similarity method with invalid distributions"""
    with pytest.raises(ValueError):
        hellinger_affinity_similarity.similarity([1, 2], [3, 4])
    with pytest.raises(ValueError):
        hellinger_affinity_similarity.similarity(np.array([1.0, -0.5]), np.array([0.5, 0.5]))

@pytest.mark.unit
def test_similarities_with_valid_distributions(hellinger_affinity_similarity):
    """Test similarities method with valid distributions"""
    a = np.array([0.5, 0.5])
    b_list = [np.array([0.5, 0.5]), np.array([0.6, 0.4])]
    scores = hellinger_affinity_similarity.similarities(a, b_list)
    assert len(scores) == 2
    assert all(0.0 <= score <= 1.0 for score in scores)

@pytest.mark.unit
def test_similarities_with_none_inputs(hellinger_affinity_similarity):
    """Test similarities method with None inputs"""
    a = np.array([0.5, 0.5])
    b_list = [None, np.array([0.5, 0.5]), None]
    scores = hellinger_affinity_similarity.similarities(a, b_list)
    assert len(scores) == 3
    assert all(score == 0.0 or score == 1.0 for score in scores)

@pytest.mark.unit
def test_similarities_with_invalid_distributions(hellinger_affinity_similarity):
    """Test similarities method with invalid distributions"""
    a = np.array([0.5, 0.5])
    b_list = [np.array([1.0, -0.5]), np.array([0.6, 0.4])]
    with pytest.raises(ValueError):
        hellinger_affinity_similarity.similarities(a, b_list)

@pytest.mark.unit
def test_dissimilarity_with_valid_distributions(hellinger_affinity_similarity):
    """Test dissimilarity method with valid distributions"""
    a = np.array([0.5, 0.5])
    b = np.array([0.5, 0.5])
    assert hellinger_affinity_similarity.dissimilarity(a, b) == 0.0

@pytest.mark.unit
def test_dissimilarity_with_different_distributions(hellinger_affinity_similarity):
    """Test dissimilarity method with different distributions"""
    a = np.array([1.0, 0.0])
    b = np.array([0.0, 1.0])
    dissimilarity_score = hellinger_affinity_similarity.dissimilarity(a, b)
    assert 0.0 <= dissimilarity_score <= 1.0

@pytest.mark.unit
def test_dissimilarities_with_valid_distributions(hellinger_affinity_similarity):
    """Test dissimilarities method with valid distributions"""
    a = np.array([0.5, 0.5])
    b_list = [np.array([0.5, 0.5]), np.array([0.6, 0.4])]
    scores = hellinger_affinity_similarity.dissimilarities(a, b_list)
    assert len(scores) == 2
    assert all(0.0 <= score <= 1.0 for score in scores)

@pytest.mark.unit
def test_check_boundedness_true(hellinger_affinity_similarity):
    """Test check_boundedness method returns True"""
    assert hellinger_affinity_similarity.check_boundedness(None, None) is True

@pytest.mark.unit
def test_check_reflexivity_true(hellinger_affinity_similarity):
    """Test check_reflexivity method returns True"""
    assert hellinger_affinity_similarity.check_reflexivity(None) is True

@pytest.mark.unit
def test_check_symmetry_true(hellinger_affinity_similarity):
    """Test check_symmetry method returns True"""
    assert hellinger_affinity_similarity.check_symmetry(None, None) is True

@pytest.mark.unit
def test_check_identity_false(hellinger_affinity_similarity):
    """Test check_identity method returns False"""
    assert hellinger_affinity_similarity.check_identity(None, None) is False