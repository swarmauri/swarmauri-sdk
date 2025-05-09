import pytest
import numpy as np
from swarmauri_standard.swarmauri_standard.similarities.BhattacharyyaCoefficientSimilarity import (
    BhattacharyyaCoefficientSimilarity,
)
import logging


@pytest.fixture
def similarity_instance():
    """Fixture to provide a similarity instance for testing."""
    return BhattacharyyaCoefficientSimilarity()


@pytest.mark.unit
def test_similarity_basic(similarity_instance):
    """Test basic functionality of the similarity method."""
    x = [0.5, 0.5]
    y = [0.5, 0.5]
    assert similarity_instance.similarity(x, y) == 1.0


@pytest.mark.unit
def test_similarity_edge_cases(similarity_instance):
    """Test edge cases for the similarity method."""
    # Identical distributions
    x = [1.0, 0.0]
    y = [1.0, 0.0]
    assert similarity_instance.similarity(x, y) == 1.0

    # Completely different distributions
    x = [1.0, 0.0]
    y = [0.0, 1.0]
    assert similarity_instance.similarity(x, y) == 0.0


@pytest.mark.unit
def test_similarity_validation():
    """Test input validation for similarity method."""
    similarity = BhattacharyyaCoefficientSimilarity()

    # Test valid input
    x = [0.3, 0.7]
    y = [0.5, 0.5]
    similarity.similarity(x, y)

    # Test invalid input
    with pytest.raises(ValueError):
        similarity.similarity([1, 2], [3, 4])


@pytest.mark.unit
def test_dissimilarity(similarity_instance):
    """Test basic functionality of the dissimilarity method."""
    x = [0.5, 0.5]
    y = [0.5, 0.5]
    assert similarity_instance.dissimilarity(x, y) == 0.0


@pytest.mark.unit
def test_similarities(similarity_instance):
    """Test similarities method with single and multiple distributions."""
    x = [0.5, 0.5]

    # Single distribution
    y = [0.5, 0.5]
    assert similarity_instance.similarities(x, y) == 1.0

    # Multiple distributions
    ys = [[0.5, 0.5], [0.0, 1.0]]
    expected = [1.0, 0.0]
    assert similarity_instance.similarities(x, ys) == expected


@pytest.mark.unit
def test_dissimilarities(similarity_instance):
    """Test dissimilarities method with single and multiple distributions."""
    x = [0.5, 0.5]

    # Single distribution
    y = [0.5, 0.5]
    assert similarity_instance.dissimilarities(x, y) == 0.0

    # Multiple distributions
    ys = [[0.5, 0.5], [0.0, 1.0]]
    expected = [0.0, 1.0]
    assert similarity_instance.dissimilarities(x, ys) == expected


@pytest.mark.unit
def test_check_boundedness(similarity_instance):
    """Test check_boundedness method."""
    x = [0.5, 0.5]
    y = [0.5, 0.5]
    assert similarity_instance.check_boundedness(x, y) is True


@pytest.mark.unit
def test_check_reflexivity(similarity_instance):
    """Test check_reflexivity method."""
    x = [0.5, 0.5]
    assert similarity_instance.check_reflexivity(x) is True


@pytest.mark.unit
def test_check_symmetry(similarity_instance):
    """Test check_symmetry method."""
    x = [0.5, 0.5]
    y = [0.5, 0.5]
    assert similarity_instance.check_symmetry(x, y) is True


@pytest.mark.unit
def test_check_identity(similarity_instance):
    """Test check_identity method."""
    x = [0.5, 0.5]
    y = [0.5, 0.5]
    assert similarity_instance.check_identity(x, y) is True


@pytest.mark.unit
def test__validate_distribution(similarity_instance):
    """Test validation of distributions."""
    # Valid distribution
    x = [0.5, 0.5]
    result = similarity_instance._validate_distribution(x)
    assert isinstance(result, np.ndarray)

    # Invalid distribution (negative values)
    x = [-0.5, 0.5]
    with pytest.raises(ValueError):
        similarity_instance._validate_distribution(x)

    # Invalid distribution (sum to zero)
    x = [0.0, 0.0]
    with pytest.raises(ValueError):
        similarity_instance._validate_distribution(x)


@pytest.mark.unit
def test_logging(similarity_instance, caplog):
    """Test if logging is correctly implemented."""
    with caplog.at_level(logging.DEBUG):
        similarity_instance.similarity([0.5, 0.5], [0.5, 0.5])
        assert "Bhattacharyya similarity calculated: 1.0" in caplog.text


@pytest.mark.unit
def test_invalid_input_types(similarity_instance):
    """Test handling of invalid input types."""
    # Invalid type for x
    x = "invalid"
    y = [0.5, 0.5]
    with pytest.raises(ValueError):
        similarity_instance.similarity(x, y)

    # Invalid type for y
    x = [0.5, 0.5]
    y = "invalid"
    with pytest.raises(ValueError):
        similarity_instance.similarity(x, y)


@pytest.mark.unit
def test_distribution_length_mismatch(similarity_instance):
    """Test distribution length mismatch handling."""
    x = [0.5, 0.5]
    y = [0.3, 0.3, 0.4]
    with pytest.raises(ValueError):
        similarity_instance.similarity(x, y)


@pytest.mark.unit
def test_distribution_nan_inf(similarity_instance):
    """Test handling of NaN and Inf values."""
    # NaN values
    x = [0.5, np.nan]
    y = [0.5, 0.5]
    with pytest.raises(ValueError):
        similarity_instance.similarity(x, y)

    # Inf values
    x = [0.5, np.inf]
    y = [0.5, 0.5]
    with pytest.raises(ValueError):
        similarity_instance.similarity(x, y)
