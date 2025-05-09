import pytest
import numpy as np
from swarmauri_standard.swarmauri_standard.similarities.CosineSimilarity import CosineSimilarity

@pytest.fixture
def cosine_similarity_instance():
    """Fixture to provide a CosineSimilarity instance for testing."""
    instance = CosineSimilarity()
    yield instance
    # Cleanup if needed

@pytest.mark.unit
def test_cosine_similarity_type(cosine_similarity_instance):
    """Test that the type is correctly set to 'CosineSimilarity'."""
    assert cosine_similarity_instance.type == "CosineSimilarity"

@pytest.mark.unit
def test_cosine_similarity_resource(cosine_similarity_instance):
    """Test that the resource type is correctly set to 'Similarity'."""
    assert cosine_similarity_instance.resource == "Similarity"

@pytest.mark.unit
def test_cosine_similarity_similarity(cosine_similarity_instance):
    """Test the cosine similarity calculation with sample vectors."""
    # Test vectors
    x = np.array([1, 2, 3])
    y = np.array([4, 5, 6])
    
    # Calculate similarity
    similarity = cosine_similarity_instance.similarity(x, y)
    
    # Verify result is within expected bounds
    assert isinstance(similarity, float)
    assert -1.0 <= similarity <= 1.0

@pytest.mark.unit
def test_cosine_similarity_zero_vectors(cosine_similarity_instance):
    """Test that zero vectors raise ValueError."""
    x = np.array([0, 0, 0])
    y = np.array([1, 2, 3])
    
    with pytest.raises(ValueError):
        cosine_similarity_instance.similarity(x, y)

@pytest.mark.unit
def test_cosine_similarity_with_strings(cosine_similarity_instance):
    """Test that string inputs are processed correctly."""
    x = "test_string"
    y = "test_string"
    
    similarity = cosine_similarity_instance.similarity(x, y)
    assert isinstance(similarity, float)

@pytest.mark.unit
def test_cosine_similarity_with_callable(cosine_similarity_instance):
    """Test that callable inputs are processed correctly."""
    def vector_callable():
        return np.array([1, 2, 3])
    
    similarity = cosine_similarity_instance.similarity(vector_callable, vector_callable)
    assert isinstance(similarity, float)

@pytest.mark.unit
def test_cosine_similarity_multiple_vectors(cosine_similarity_instance):
    """Test that multiple vectors are processed correctly."""
    x = np.array([1, 2, 3])
    y_list = [np.array([4, 5, 6]), np.array([7, 8, 9])]
    
    similarities = cosine_similarity_instance.similarities(x, y_list)
    assert isinstance(similarities, list)
    assert all(isinstance(s, float) for s in similarities)

@pytest.mark.unit
def test_cosine_similarity_dissimilarity(cosine_similarity_instance):
    """Test the dissimilarity calculation."""
    x = np.array([1, 2, 3])
    y = np.array([4, 5, 6])
    
    similarity = cosine_similarity_instance.similarity(x, y)
    dissimilarity = cosine_similarity_instance.dissimilarity(x, y)
    
    assert isinstance(dissimilarity, float)
    assert np.isclose(dissimilarity, 1.0 - similarity)

@pytest.mark.unit
def test_cosine_similarity_boundedness(cosine_similarity_instance):
    """Test that the measure is bounded."""
    assert cosine_similarity_instance.check_boundedness(
        np.array([1, 2, 3]), np.array([4, 5, 6])
    ) is True

@pytest.mark.unit
def test_cosine_similarity_reflexivity(cosine_similarity_instance):
    """Test reflexivity of the measure."""
    x = np.array([1, 2, 3])
    assert cosine_similarity_instance.check_reflexivity(x) is True

@pytest.mark.unit
def test_cosine_similarity_symmetry(cosine_similarity_instance):
    """Test symmetry of the measure."""
    x = np.array([1, 2, 3])
    y = np.array([4, 5, 6])
    assert cosine_similarity_instance.check_symmetry(x, y) is True

@pytest.mark.unit
def test_cosine_similarity_identity(cosine_similarity_instance):
    """Test identity of the measure."""
    x = np.array([1, 2, 3])
    y = np.array([1, 2, 3])
    assert cosine_similarity_instance.check_identity(x, y) is True