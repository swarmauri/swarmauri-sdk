import logging
from math import exp
from typing import Any, List

import numpy as np
import pytest

from swarmauri_standard.similarities.GaussianRBFSimilarity import GaussianRBFSimilarity

# Set up logger for testing
logger = logging.getLogger(__name__)


@pytest.fixture
def gaussian_rbf_similarity():
    """
    Fixture that returns a default GaussianRBFSimilarity instance.

    Returns
    -------
    GaussianRBFSimilarity
        An instance with default gamma=1.0
    """
    return GaussianRBFSimilarity()


@pytest.fixture
def custom_gamma_similarity():
    """
    Fixture that returns a GaussianRBFSimilarity instance with custom gamma.

    Returns
    -------
    GaussianRBFSimilarity
        An instance with gamma=0.5
    """
    return GaussianRBFSimilarity(gamma=0.5)


@pytest.mark.unit
def test_initialization():
    """Test that the similarity measure initializes correctly with default and custom parameters."""
    # Default initialization
    similarity = GaussianRBFSimilarity()
    assert similarity.gamma == 1.0
    assert similarity.type == "GaussianRBFSimilarity"

    # Custom gamma initialization
    similarity = GaussianRBFSimilarity(gamma=2.5)
    assert similarity.gamma == 2.5


@pytest.mark.unit
def test_serialization(gaussian_rbf_similarity: GaussianRBFSimilarity):
    """
    Test serialization and deserialization of GaussianRBFSimilarity.
    """
    # Serialize the instance to JSON
    serialized = gaussian_rbf_similarity.model_dump_json()

    # Deserialize back to an instance
    deserialized = GaussianRBFSimilarity.model_validate_json(serialized)

    # Check that the deserialized instance has the same properties
    assert deserialized.id == gaussian_rbf_similarity.id
    assert deserialized.type == gaussian_rbf_similarity.type


@pytest.mark.unit
def test_initialization_invalid_gamma():
    """Test that initialization with invalid gamma values raises appropriate exceptions."""
    # Test with zero gamma
    with pytest.raises(ValueError, match="Gamma must be positive"):
        GaussianRBFSimilarity(gamma=0)

    # Test with negative gamma
    with pytest.raises(ValueError, match="Gamma must be positive"):
        GaussianRBFSimilarity(gamma=-1.0)


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y, expected",
    [
        # Identical vectors should have similarity 1.0
        ([0, 0], [0, 0], 1.0),
        # Orthogonal vectors with gamma=1.0
        ([1, 0], [0, 1], exp(-2)),
        # Distant vectors should have low similarity
        ([10, 10], [0, 0], exp(-200)),
        # Single value test
        (5, 5, 1.0),
        # Single value test with difference
        (3, 5, exp(-4)),
    ],
)
def test_similarity(
    gaussian_rbf_similarity: GaussianRBFSimilarity, x: Any, y: Any, expected: float
):
    """
    Test the similarity calculation for various input pairs.

    Parameters
    ----------
    gaussian_rbf_similarity : GaussianRBFSimilarity
        The similarity measure instance
    x : Any
        First input for comparison
    y : Any
        Second input for comparison
    expected : float
        Expected similarity value
    """
    result = gaussian_rbf_similarity.similarity(x, y)
    assert pytest.approx(result, abs=1e-10) == expected


@pytest.mark.unit
@pytest.mark.parametrize(
    "gamma, x, y, expected",
    [
        # Different gamma values affect the decay rate
        (0.5, [1, 1], [2, 2], exp(-0.5 * 2)),
        (2.0, [1, 1], [2, 2], exp(-2.0 * 2)),
        (0.1, [0, 0], [3, 4], exp(-0.1 * 25)),
    ],
)
def test_similarity_with_different_gamma(
    gamma: float, x: List[float], y: List[float], expected: float
):
    """
    Test the similarity calculation with different gamma values.

    Parameters
    ----------
    gamma : float
        The gamma parameter for the RBF kernel
    x : List[float]
        First input vector
    y : List[float]
        Second input vector
    expected : float
        Expected similarity value
    """
    similarity = GaussianRBFSimilarity(gamma=gamma)
    result = similarity.similarity(x, y)
    assert pytest.approx(result, abs=1e-10) == expected


@pytest.mark.unit
def test_similarity_input_validation(gaussian_rbf_similarity: GaussianRBFSimilarity):
    """
    Test that the similarity function properly validates inputs.

    Parameters
    ----------
    gaussian_rbf_similarity : GaussianRBFSimilarity
        The similarity measure instance
    """
    # Test with incompatible dimensions
    with pytest.raises(ValueError, match="Input shapes must match"):
        gaussian_rbf_similarity.similarity([1, 2, 3], [1, 2])

    # Test with non-numeric inputs
    with pytest.raises(Exception):
        gaussian_rbf_similarity.similarity("string1", "string2")


@pytest.mark.unit
def test_similarities(gaussian_rbf_similarity: GaussianRBFSimilarity):
    """
    Test the similarities method which compares one object to multiple others.

    Parameters
    ----------
    gaussian_rbf_similarity : GaussianRBFSimilarity
        The similarity measure instance
    """
    x = [1, 1]
    ys = [[1, 1], [2, 2], [3, 3]]

    expected = [
        exp(-0 * 1.0),  # Distance to self is 0
        exp(-2 * 1.0),  # Distance to [2,2] is sqrt(2)^2 = 2
        exp(-8 * 1.0),  # Distance to [3,3] is sqrt(8)^2 = 8
    ]

    results = gaussian_rbf_similarity.similarities(x, ys)

    assert len(results) == len(expected)
    for result, exp_val in zip(results, expected):
        assert pytest.approx(result, abs=1e-10) == exp_val


@pytest.mark.unit
def test_similarities_with_numpy_array(gaussian_rbf_similarity: GaussianRBFSimilarity):
    """
    Test the similarities method with numpy array inputs.

    Parameters
    ----------
    gaussian_rbf_similarity : GaussianRBFSimilarity
        The similarity measure instance
    """
    x = np.array([1, 1])
    ys = np.array([[1, 1], [2, 2], [3, 3]])

    expected = [exp(-0 * 1.0), exp(-2 * 1.0), exp(-8 * 1.0)]

    results = gaussian_rbf_similarity.similarities(x, ys)

    assert len(results) == len(expected)
    for result, exp_val in zip(results, expected):
        assert pytest.approx(result, abs=1e-10) == exp_val


@pytest.mark.unit
def test_dissimilarity(gaussian_rbf_similarity: GaussianRBFSimilarity):
    """
    Test the dissimilarity calculation.

    Parameters
    ----------
    gaussian_rbf_similarity : GaussianRBFSimilarity
        The similarity measure instance
    """
    x = [1, 1]
    y = [2, 2]

    similarity = gaussian_rbf_similarity.similarity(x, y)
    dissimilarity = gaussian_rbf_similarity.dissimilarity(x, y)

    assert pytest.approx(dissimilarity, abs=1e-10) == 1.0 - similarity
    assert pytest.approx(dissimilarity, abs=1e-10) == 1.0 - exp(-2)


@pytest.mark.unit
def test_check_bounded(gaussian_rbf_similarity: GaussianRBFSimilarity):
    """
    Test that the similarity measure correctly reports being bounded.

    Parameters
    ----------
    gaussian_rbf_similarity : GaussianRBFSimilarity
        The similarity measure instance
    """
    assert gaussian_rbf_similarity.check_bounded() is True


@pytest.mark.unit
def test_model_validation():
    """Test model validation using Pydantic functionality."""
    similarity = GaussianRBFSimilarity(gamma=1.5)
    json_data = similarity.model_dump_json()
    reconstructed = GaussianRBFSimilarity.model_validate_json(json_data)

    assert reconstructed.gamma == 1.5
    assert reconstructed.type == "GaussianRBFSimilarity"
