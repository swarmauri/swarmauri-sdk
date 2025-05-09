import pytest
import numpy as np
from swarmauri_standard.swarmauri_standard.similarities.CosineSimilarity import CosineSimilarity
import logging

@pytest.fixture
def cos_sim():
    """Fixture to provide a CosineSimilarity instance for testing."""
    return CosineSimilarity()

@pytest.mark.unit
def test_cosine_similarity_resource(cos_sim):
    """Test that the resource property is correctly set."""
    assert cos_sim.resource == "Similarity"

@pytest.mark.unit
def test_cosine_similarity_type(cos_sim):
    """Test that the type property is correctly set."""
    assert cos_sim.type == "CosineSimilarity"

@pytest.mark.unit
def test_cosine_similarity_init(cos_sim, caplog):
    """Test that the __init__ method initializes correctly."""
    with caplog.at_level(logging.DEBUG):
        assert "Initialized CosineSimilarity instance" in caplog.text

@pytest.mark.unit
def test_cosine_similarity_similarity(cos_sim):
    """Test the cosine similarity calculation with various inputs."""
    # Test with identical vectors
    x = np.array([1, 2, 3])
    y = np.array([1, 2, 3])
    similarity = cos_sim.similarity(x, y)
    assert similarity == 1.0

    # Test with orthogonal vectors
    x = np.array([1, 0])
    y = np.array([0, 1])
    similarity = cos_sim.similarity(x, y)
    assert similarity == 0.0

    # Test with vectors of different lengths
    x = np.array([1, 2])
    y = np.array([1, 2, 3])
    with pytest.raises(ValueError):
        cos_sim.similarity(x, y)

@pytest.mark.unit
def test_cosine_similarity_zero_vectors(cos_sim):
    """Test handling of zero vectors."""
    x = np.array([0, 0])
    y = np.array([1, 1])
    with pytest.raises(ValueError):
        cos_sim.similarity(x, y)

@pytest.mark.unit
def test_cosine_similarity_similarities(cos_sim):
    """Test calculation of similarities for multiple pairs."""
    pairs = [
        (np.array([1, 1]), np.array([1, 1])),
        (np.array([1, 0]), np.array([0, 1])),
        (np.array([2, 3]), np.array([4, 5]))
    ]
    similarities = cos_sim.similarities(pairs)
    assert isinstance(similarities, list)
    assert all(isinstance(s, float) for s in similarities)

@pytest.mark.unit
def test_cosine_similarity_dissimilarity(cos_sim):
    """Test the dissimilarity calculation."""
    x = np.array([1, 1])
    y = np.array([1, 1])
    dissimilarity = cos_sim.dissimilarity(x, y)
    assert dissimilarity == 0.0

    x = np.array([1, 0])
    y = np.array([0, 1])
    dissimilarity = cos_sim.dissimilarity(x, y)
    assert dissimilarity == 1.0

@pytest.mark.unit
def test_cosine_similarity_dissimilarities(cos_sim):
    """Test calculation of dissimilarities for multiple pairs."""
    pairs = [
        (np.array([1, 1]), np.array([1, 1])),
        (np.array([1, 0]), np.array([0, 1])),
        (np.array([2, 3]), np.array([4, 5]))
    ]
    dissimilarities = cos_sim.dissimilarities(pairs)
    assert isinstance(dissimilarities, list)
    assert all(isinstance(d, float) for d in dissimilarities)