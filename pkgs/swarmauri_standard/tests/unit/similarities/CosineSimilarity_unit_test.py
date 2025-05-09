import pytest
import logging
from swarmauri_standard.similarities.CosineSimilarity import CosineSimilarity

@pytest.mark.unit
def test_similarity_with_valid_vectors():
    """Test cosine similarity calculation with valid vectors."""
    cos_sim = CosineSimilarity()
    
    # Test with identical vectors
    x = [1, 2, 3]
    y = [1, 2, 3]
    assert cos_sim.similarity(x, y) == 1.0
    
    # Test with orthogonal vectors
    x = [1, 0]
    y = [0, 1]
    assert cos_sim.similarity(x, y) == 0.0

@pytest.mark.unit
def test_similarity_with_string_vectors():
    """Test cosine similarity with string representations of vectors."""
    cos_sim = CosineSimilarity()
    
    x = "[1, 2, 3]"
    y = "[1, 2, 3]"
    assert cos_sim.similarity(x, y) == 1.0

@pytest.mark.unit
def test_similarity_with_zero_vector():
    """Test that similarity raises ValueError with zero vectors."""
    cos_sim = CosineSimilarity()
    
    x = [0, 0]
    y = [1, 1]
    with pytest.raises(ValueError):
        cos_sim.similarity(x, y)

@pytest.mark.unit
def test_similarities_with_multiple_vectors():
    """Test calculation of similarities for multiple vector pairs."""
    cos_sim = CosineSimilarity()
    
    xs = [[1, 0], [0, 1]]
    ys = [[0, 1], [1, 0]]
    expected = [0.0, 0.0]
    assert cos_sim.similarities(xs, ys) == expected

@pytest.mark.unit
def test_dissimilarity_with_valid_vectors():
    """Test cosine dissimilarity calculation with valid vectors."""
    cos_sim = CosineSimilarity()
    
    x = [1, 2, 3]
    y = [1, 2, 3]
    assert cos_sim.dissimilarity(x, y) == 0.0
    
    x = [1, 0]
    y = [0, 1]
    assert cos_sim.dissimilarity(x, y) == 1.0

@pytest.mark.unit
def test_dissimilarities_with_multiple_vectors():
    """Test calculation of dissimilarities for multiple vector pairs."""
    cos_sim = CosineSimilarity()
    
    xs = [[1, 0], [0, 1]]
    ys = [[0, 1], [1, 0]]
    expected = [1.0, 1.0]
    assert cos_sim.dissimilarities(xs, ys) == expected

@pytest.mark.unit
def test_check_boundedness():
    """Test if cosine similarity is bounded between -1 and 1."""
    cos_sim = CosineSimilarity()
    assert cos_sim.check_boundedness() is True

@pytest.mark.unit
def test_check_reflexivity():
    """Test if cosine similarity satisfies reflexivity."""
    cos_sim = CosineSimilarity()
    assert cos_sim.check_reflexivity() is True

@pytest.mark.unit
def test_check_symmetry():
    """Test if cosine similarity is symmetric."""
    cos_sim = CosineSimilarity()
    assert cos_sim.check_symmetry() is True

@pytest.mark.unit
def test_check_identity():
    """Test if cosine similarity satisfies identity of discernibles."""
    cos_sim = CosineSimilarity()
    assert cos_sim.check_identity() is False

@pytest.mark.unit
def test_class_attributes():
    """Test if class attributes are correctly set."""
    assert CosineSimilarity.type == "CosineSimilarity"
    assert CosineSimilarity.resource == "COSINE_SIMILARITY"