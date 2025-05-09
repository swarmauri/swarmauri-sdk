import pytest
import numpy as np
from swarmauri_standard.swarmauri_standard.similarities.HellingerAffinitySimilarity import (
    HellingerAffinitySimilarity,
)


@pytest.mark.unit
def test_hellinger_affinity_similarity_resource() -> None:
    """Test that the resource property is correctly set."""
    assert HellingerAffinitySimilarity.resource == "SIMILARITY"


@pytest.mark.unit
def test_hellinger_affinity_similarity_type() -> None:
    """Test that the type property is correctly set."""
    assert HellingerAffinitySimilarity.type == "HellingerAffinitySimilarity"


@pytest.mark.unit
def test_hellinger_affinity_similarity_similarity() -> None:
    """Test the computation of similarity between probability distributions."""
    similarity = HellingerAffinitySimilarity()

    # Test with identical distributions
    x = np.array([0.5, 0.5])
    y = np.array([0.5, 0.5])
    assert np.isclose(similarity.similarity(x, y), 1.0, atol=1e-8)

    # Test with different distributions
    x = np.array([1.0, 0.0])
    y = np.array([0.0, 1.0])
    similarity_score = similarity.similarity(x, y)
    assert similarity_score < 1.0

    # Test with invalid distribution
    x = np.array([1.5, -0.5])
    with pytest.raises(ValueError):
        similarity.similarity(x, y)


@pytest.mark.unit
def test_hellinger_affinity_similarity_similarities() -> None:
    """Test the computation of similarities with multiple distributions."""
    similarity = HellingerAffinitySimilarity()
    x = np.array([0.5, 0.5])

    # Test with single distribution
    y = np.array([0.5, 0.5])
    result = similarity.similarities(x, y)
    assert np.isclose(result, 1.0, atol=1e-8)

    # Test with list of distributions
    ys = [np.array([0.5, 0.5]), np.array([0.0, 1.0])]
    results = similarity.similarities(x, ys)
    assert len(results) == 2
    assert np.isclose(results[0], 1.0, atol=1e-8)
    assert results[1] < 1.0


@pytest.mark.unit
def test_hellinger_affinity_similarity_dissimilarity() -> None:
    """Test the computation of dissimilarity between probability distributions."""
    dissimilarity = HellingerAffinitySimilarity()

    # Test with identical distributions
    x = np.array([0.5, 0.5])
    y = np.array([0.5, 0.5])
    assert np.isclose(dissimilarity.dissimilarity(x, y), 0.0, atol=1e-8)

    # Test with different distributions
    x = np.array([1.0, 0.0])
    y = np.array([0.0, 1.0])
    dissimilarity_score = dissimilarity.dissimilarity(x, y)
    assert dissimilarity_score > 0.0


@pytest.mark.unit
def test_hellinger_affinity_similarity_check_boundedness() -> None:
    """Test that the measure is bounded between 0 and 1."""
    assert HellingerAffinitySimilarity().check_boundedness(
        np.array([0.5, 0.5]), np.array([0.5, 0.5])
    )


@pytest.mark.unit
def test_hellinger_affinity_similarity_check_reflexivity() -> None:
    """Test the reflexivity of the similarity measure."""
    measure = HellingerAffinitySimilarity()
    x = np.array([0.5, 0.5])
    assert measure.check_reflexivity(x)


@pytest.mark.unit
def test_hellinger_affinity_similarity_check_symmetry() -> None:
    """Test the symmetry of the similarity measure."""
    measure = HellingerAffinitySimilarity()
    x = np.array([0.5, 0.5])
    y = np.array([0.0, 1.0])
    assert measure.check_symmetry(x, y)


@pytest.mark.unit
def test_hellinger_affinity_similarity_check_identity() -> None:
    """Test the identity property of the similarity measure."""
    measure = HellingerAffinitySimilarity()
    x = np.array([0.5, 0.5])
    y = np.array([0.5, 0.5])
    assert measure.check_identity(x, y)

    x = np.array([1.0, 0.0])
    y = np.array([0.0, 1.0])
    assert not measure.check_identity(x, y)


@pytest.mark.unit
def test_hellinger_affinity_similarity_edge_cases() -> None:
    """Test edge cases for the similarity measure."""
    measure = HellingerAffinitySimilarity()

    # Test with one element distributions
    x = np.array([1.0])
    y = np.array([1.0])
    assert np.isclose(measure.similarity(x, y), 1.0, atol=1e-8)

    # Test with zero vectors
    x = np.array([0.0, 0.0])
    y = np.array([0.0, 0.0])
    assert np.isclose(measure.similarity(x, y), 1.0, atol=1e-8)
