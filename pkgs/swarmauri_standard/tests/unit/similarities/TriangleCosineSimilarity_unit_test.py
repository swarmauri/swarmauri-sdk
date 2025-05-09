import pytest
import logging
from swarmauri_standard.swarmauri_standard.similarities.TriangleCosineSimilarity import TriangleCosineSimilarity
import math

logger = logging.getLogger(__name__)

@pytest.mark.unit
def test_resource():
    """Test that the resource attribute is correctly set."""
    triangle_cosine = TriangleCosineSimilarity()
    assert triangle_cosine.resource == "Similarity"

@pytest.mark.unit
def test_type():
    """Test that the type attribute is correctly set."""
    triangle_cosine = TriangleCosineSimilarity()
    assert triangle_cosine.type == "TriangleCosineSimilarity"

@pytest.mark.unit
def test_serialization():
    """Test serialization and validation of the model."""
    triangle_cosine = TriangleCosineSimilarity()
    model_json = triangle_cosine.model_dump_json()
    validated_id = triangle_cosine.model_validate_json(model_json)
    assert triangle_cosine.id == validated_id

@pytest.mark.unit
def test_similarity_valid_vectors():
    """Test cosine similarity calculation with valid vectors."""
    a = [1, 2, 3]
    b = [4, 5, 6]
    
    triangle_cosine = TriangleCosineSimilarity()
    similarity = triangle_cosine.similarity(a, b)
    
    # Expected value from numpy.corrcoef
    expected = 0.9999999999999999  # Due to floating point precision
    
    assert math.isclose(similarity, expected, rel_tol=1e-9, abs_tol=1e-9)

@pytest.mark.unit
def test_similarity_zero_vector():
    """Test that similarity raises ValueError for zero vectors."""
    triangle_cosine = TriangleCosineSimilarity()
    
    with pytest.raises(ValueError):
        triangle_cosine.similarity([0, 0, 0], [1, 2, 3])

@pytest.mark.unit
def test_similarity_none_input():
    """Test that similarity raises ValueError for None input."""
    triangle_cosine = TriangleCosineSimilarity()
    
    with pytest.raises(ValueError):
        triangle_cosine.similarity(None, [1, 2, 3])

@pytest.mark.unit
def test_similarities():
    """Test computing similarities with multiple vectors."""
    a = [1, 2, 3]
    b_list = [[4, 5, 6], [7, 8, 9]]
    
    triangle_cosine = TriangleCosineSimilarity()
    similarities = triangle_cosine.similarities(a, b_list)
    
    assert isinstance(similarities, tuple)
    assert len(similarities) == 2

@pytest.mark.unit
def test_dissimilarity():
    """Test that dissimilarity is 1 - similarity."""
    a = [1, 2, 3]
    b = [4, 5, 6]
    
    triangle_cosine = TriangleCosineSimilarity()
    similarity = triangle_cosine.similarity(a, b)
    dissimilarity = triangle_cosine.dissimilarity(a, b)
    
    assert math.isclose(dissimilarity, 1.0 - similarity, rel_tol=1e-9, abs_tol=1e-9)

@pytest.mark.unit
def test_check_reflexivity():
    """Test that reflexivity check returns True for valid input."""
    a = [1, 2, 3]
    
    triangle_cosine = TriangleCosineSimilarity()
    is_reflexive = triangle_cosine.check_reflexivity(a)
    
    assert is_reflexive is True

@pytest.mark.unit
def test_check_symmetry():
    """Test that symmetry check returns True for valid input."""
    a = [1, 2, 3]
    b = [4, 5, 6]
    
    triangle_cosine = TriangleCosineSimilarity()
    is_symmetric = triangle_cosine.check_symmetry(a, b)
    
    assert is_symmetric is True

@pytest.mark.unit
def test_check_boundedness():
    """Test that boundedness check returns True."""
    triangle_cosine = TriangleCosineSimilarity()
    is_bounded = triangle_cosine.check_boundedness([1, 2, 3], [4, 5, 6])
    
    assert is_bounded is True

@pytest.mark.unit
def test_dissimilarities():
    """Test computing dissimilarities with multiple vectors."""
    a = [1, 2, 3]
    b_list = [[4, 5, 6], [7, 8, 9]]
    
    triangle_cosine = TriangleCosineSimilarity()
    dissimilarities = triangle_cosine.dissimilarities(a, b_list)
    
    assert isinstance(dissimilarities, tuple)
    assert len(dissimilarities) == 2