import pytest
from swarmauri_standard.swarmauri_standard.similarities.GaussianRBFSimilarity import (
    GaussianRBFSimilarity,
)
import logging


@pytest.mark.unit
def test_gaussianrbf_similarity_resource_type():
    """Test that the GaussianRBFSimilarity resource type is correct."""
    assert GaussianRBFSimilarity.resource == "Similarity"


@pytest.mark.unit
def test_gaussianrbf_similarity_gamma_default():
    """Test that the default gamma value is initialized correctly."""
    gaussianrbfsimilarity = GaussianRBFSimilarity()
    assert gaussianrbfsimilarity.gamma == 1.0


@pytest.mark.unit
def test_gaussianrbf_similarity_initialization(caplog):
    """Test the initialization of GaussianRBFSimilarity with valid gamma."""
    with caplog.at_level(logging.INFO):
        gaussianrbfsimilarity = GaussianRBFSimilarity(gamma=2.0)
        assert "GaussianRBFSimilarity initialized with gamma = 2.0" in caplog.text
        assert gaussianrbfsimilarity.gamma == 2.0


@pytest.mark.unit
def test_gaussianrbf_similarity_invalid_gamma():
    """Test that invalid gamma values raise ValueError during initialization."""
    with pytest.raises(ValueError):
        GaussianRBFSimilarity(gamma=-1.0)
    with pytest.raises(ValueError):
        GaussianRBFSimilarity(gamma=0.0)


@pytest.mark.unit
def test_gaussianrbf_similarity_calculation():
    """Test the calculation of similarity for various input types."""
    similarity = GaussianRBFSimilarity()

    # Test with scalar values
    assert similarity.similarity(1, 1) == 1.0
    assert similarity.similarity(1, 2) < 1.0

    # Test with vector inputs
    assert similarity.similarity([1, 2], [1, 2]) == 1.0
    assert similarity.similarity([1, 2], [2, 3]) < 1.0

    # Test with identical inputs
    assert similarity.similarity([1.5, 2.5], [1.5, 2.5]) == 1.0


@pytest.mark.unit
def test_gaussianrbf_similarities_calculation():
    """Test the calculation of similarities for multiple elements."""
    similarity = GaussianRBFSimilarity()

    # Single element
    result = similarity.similarities([1, 2], [3, 4])
    assert isinstance(result, float)
    assert result < 1.0

    # List of elements
    results = similarity.similarities([1, 2], [[3, 4], [5, 6]])
    assert isinstance(results, list)
    assert all(isinstance(res, float) for res in results)
    assert all(res < 1.0 for res in results)


@pytest.mark.unit
def test_gaussianrbf_dissimilarity_calculation():
    """Test the calculation of dissimilarity."""
    similarity = GaussianRBFSimilarity()

    # Test with scalar values
    assert similarity.dissimilarity(1, 1) == 0.0
    assert similarity.dissimilarity(1, 2) > 0.0

    # Test with vector inputs
    assert similarity.dissimilarity([1, 2], [1, 2]) == 0.0
    assert similarity.dissimilarity([1, 2], [2, 3]) > 0.0


@pytest.mark.unit
def test_gaussianrbf_similarity_reflexive():
    """Test the reflexive property of similarity."""
    similarity = GaussianRBFSimilarity()

    # Test with vector
    assert similarity.similarity([1, 2], [1, 2]) == 1.0

    # Test with scalar
    assert similarity.similarity(5, 5) == 1.0


@pytest.mark.unit
def test_gaussianrbf_similarity_bounded():
    """Test that similarity values are bounded between 0 and 1."""
    similarity = GaussianRBFSimilarity()

    # Test with scalar values
    assert 0 <= similarity.similarity(1, 2) <= 1

    # Test with vector inputs
    assert 0 <= similarity.similarity([1, 2], [3, 4]) <= 1


@pytest.mark.unit
def test_gaussianrbf_similarity_symmetric():
    """Test the symmetric property of similarity."""
    similarity = GaussianRBFSimilarity()

    # Test with scalar values
    assert similarity.similarity(1, 2) == similarity.similarity(2, 1)

    # Test with vector inputs
    assert similarity.similarity([1, 2], [3, 4]) == similarity.similarity(
        [3, 4], [1, 2]
    )
