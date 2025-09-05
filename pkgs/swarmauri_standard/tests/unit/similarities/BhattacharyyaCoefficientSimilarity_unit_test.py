import logging

import numpy as np
import pytest

from swarmauri_standard.similarities.BhattacharyyaCoefficientSimilarity import (
    BhattacharyyaCoefficientSimilarity,
)

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def similarity_instance():
    """
    Fixture that provides a BhattacharyyaCoefficientSimilarity instance.

    Returns
    -------
    BhattacharyyaCoefficientSimilarity
        An instance of the BhattacharyyaCoefficientSimilarity class
    """
    return BhattacharyyaCoefficientSimilarity()


@pytest.mark.unit
def test_initialization():
    """
    Test the initialization of the BhattacharyyaCoefficientSimilarity class.
    """
    similarity = BhattacharyyaCoefficientSimilarity()
    assert similarity.type == "BhattacharyyaCoefficientSimilarity"
    assert similarity.resource == "Similarity"


@pytest.mark.unit
def test_check_bounded(similarity_instance):
    """
    Test that the similarity measure correctly reports as bounded.

    Parameters
    ----------
    similarity_instance : BhattacharyyaCoefficientSimilarity
        The similarity instance from the fixture
    """
    assert similarity_instance.check_bounded() is True


@pytest.mark.unit
@pytest.mark.parametrize(
    "p, q, expected",
    [
        # Identical distributions should have coefficient 1.0
        ([0.2, 0.3, 0.5], [0.2, 0.3, 0.5], 1.0),
        # Completely disjoint distributions should have coefficient 0.0
        ([1.0, 0.0, 0.0], [0.0, 0.0, 1.0], 0.0),
        # Partially overlapping distributions
        ([0.5, 0.5, 0.0], [0.0, 0.5, 0.5], 0.5),
        # More complex distribution
        ([0.1, 0.4, 0.3, 0.2], [0.2, 0.3, 0.4, 0.1], 0.97566303550217),
        # Uniform distributions
        ([0.25, 0.25, 0.25, 0.25], [0.25, 0.25, 0.25, 0.25], 1.0),
    ],
)
def test_similarity(similarity_instance, p, q, expected):
    """
    Test the similarity method with various probability distributions.

    Parameters
    ----------
    similarity_instance : BhattacharyyaCoefficientSimilarity
        The similarity instance from the fixture
    p : List[float]
        First probability distribution
    q : List[float]
        Second probability distribution
    expected : float
        Expected Bhattacharyya coefficient
    """
    result = similarity_instance.similarity(p, q)
    assert np.isclose(result, expected, rtol=1e-5)


@pytest.mark.unit
@pytest.mark.parametrize(
    "p_dict, q_dict, expected",
    [
        # Identical distributions
        ({"A": 0.3, "B": 0.7}, {"A": 0.3, "B": 0.7}, 1.0),
        # Disjoint distributions
        ({"A": 1.0, "B": 0.0}, {"A": 0.0, "B": 1.0}, 0.0),
        # Partially overlapping with different keys
        ({"A": 0.5, "B": 0.5}, {"B": 0.5, "C": 0.5}, 0.5),
        # More complex case with missing keys
        ({"A": 0.4, "B": 0.6}, {"A": 0.3, "B": 0.2, "C": 0.5}, 0.6928203230275509),
    ],
)
def test_similarity_with_dictionaries(similarity_instance, p_dict, q_dict, expected):
    """
    Test the similarity method with dictionary probability distributions.

    Parameters
    ----------
    similarity_instance : BhattacharyyaCoefficientSimilarity
        The similarity instance from the fixture
    p_dict : Dict[str, float]
        First probability distribution as dictionary
    q_dict : Dict[str, float]
        Second probability distribution as dictionary
    expected : float
        Expected Bhattacharyya coefficient
    """
    result = similarity_instance.similarity(p_dict, q_dict)
    assert np.isclose(result, expected, rtol=1e-5)


@pytest.mark.unit
def test_similarity_error_different_dimensions(similarity_instance):
    """
    Test that similarity method raises ValueError for distributions with different dimensions.

    Parameters
    ----------
    similarity_instance : BhattacharyyaCoefficientSimilarity
        The similarity instance from the fixture
    """
    p = [0.5, 0.5]
    q = [0.3, 0.3, 0.4]

    with pytest.raises(ValueError) as excinfo:
        similarity_instance.similarity(p, q)

    assert "Distributions must have the same dimensions" in str(excinfo.value)


@pytest.mark.unit
def test_similarity_error_not_normalized(similarity_instance):
    """
    Test that similarity method raises ValueError for non-normalized distributions.

    Parameters
    ----------
    similarity_instance : BhattacharyyaCoefficientSimilarity
        The similarity instance from the fixture
    """
    p = [0.5, 0.6]  # Sum = 1.1
    q = [0.5, 0.5]  # Sum = 1.0

    with pytest.raises(ValueError) as excinfo:
        similarity_instance.similarity(p, q)

    assert "not normalized" in str(excinfo.value)


@pytest.mark.unit
def test_similarities(similarity_instance):
    """
    Test the similarities method with multiple distributions.

    Parameters
    ----------
    similarity_instance : BhattacharyyaCoefficientSimilarity
        The similarity instance from the fixture
    """
    p = [0.2, 0.3, 0.5]
    qs = [
        [0.2, 0.3, 0.5],  # Identical, expect 1.0
        [0.5, 0.3, 0.2],  # Different, expect ~0.83
        [1.0, 0.0, 0.0],  # Very different, expect ~0.45
    ]

    expected = [1.0, 0.9324555320336758, 0.4472135954999579]
    results = similarity_instance.similarities(p, qs)

    assert len(results) == len(expected)
    for res, exp in zip(results, expected):
        assert np.isclose(res, exp, rtol=1e-5)


@pytest.mark.unit
def test_similarities_with_dictionaries(similarity_instance):
    """
    Test the similarities method with dictionary distributions.

    Parameters
    ----------
    similarity_instance : BhattacharyyaCoefficientSimilarity
        The similarity instance from the fixture
    """
    p_dict = {"A": 0.3, "B": 0.7}
    q_dicts = [
        {"A": 0.3, "B": 0.7},  # Identical, expect 1.0
        {"A": 0.7, "B": 0.3},  # Different, expect ~0.83
        {"A": 0.0, "B": 0.0, "C": 1.0},  # Disjoint, expect 0.0
    ]

    expected = [1.0, 0.916515138991168, 0.0]
    results = similarity_instance.similarities(p_dict, q_dicts)

    assert len(results) == len(expected)
    for res, exp in zip(results, expected):
        assert np.isclose(res, exp, rtol=1e-5)


@pytest.mark.unit
@pytest.mark.parametrize(
    "p, q, expected",
    [
        ([0.2, 0.3, 0.5], [0.2, 0.3, 0.5], 0.0),  # Identical: dissimilarity = 0
        ([1.0, 0.0, 0.0], [0.0, 0.0, 1.0], 1.0),  # Disjoint: dissimilarity = 1
        ([0.5, 0.5, 0.0], [0.0, 0.5, 0.5], 0.5),  # Partial overlap
        (
            [0.1, 0.4, 0.3, 0.2],
            [0.2, 0.3, 0.4, 0.1],
            0.02433696449782996,
        ),  # Small dissimilarity
    ],
)
def test_dissimilarity(similarity_instance, p, q, expected):
    """
    Test the dissimilarity method with various probability distributions.

    Parameters
    ----------
    similarity_instance : BhattacharyyaCoefficientSimilarity
        The similarity instance from the fixture
    p : List[float]
        First probability distribution
    q : List[float]
        Second probability distribution
    expected : float
        Expected dissimilarity value
    """
    result = similarity_instance.dissimilarity(p, q)
    assert np.isclose(result, expected, rtol=1e-5)


@pytest.mark.unit
def test_serialization():
    """
    Test the serialization and deserialization of the BhattacharyyaCoefficientSimilarity class.
    """
    # Create an instance
    similarity = BhattacharyyaCoefficientSimilarity()

    # Serialize to JSON
    json_str = similarity.model_dump_json()

    # Deserialize from JSON
    deserialized = BhattacharyyaCoefficientSimilarity.model_validate_json(json_str)

    # Check that the deserialized object has the same type
    assert deserialized.type == similarity.type
    assert deserialized.resource == similarity.resource


@pytest.mark.unit
def test_error_handling(similarity_instance):
    """
    Test error handling for invalid inputs.

    Parameters
    ----------
    similarity_instance : BhattacharyyaCoefficientSimilarity
        The similarity instance from the fixture
    """
    # Test with non-numeric input
    with pytest.raises(ValueError):
        similarity_instance.similarity(["a", "b"], [0.5, 0.5])

    # Test with negative probabilities
    with pytest.raises(ValueError):
        similarity_instance.similarity([-0.1, 1.1], [0.5, 0.5])
