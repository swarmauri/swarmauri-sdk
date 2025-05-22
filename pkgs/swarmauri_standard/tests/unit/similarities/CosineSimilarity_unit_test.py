import logging

import numpy as np
import pytest

from swarmauri_standard.similarities.CosineSimilarity import CosineSimilarity

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def cosine_similarity():
    """
    Fixture that provides a CosineSimilarity instance.

    Returns
    -------
    CosineSimilarity
        An instance of the CosineSimilarity class
    """
    return CosineSimilarity()


@pytest.mark.unit
def test_type(cosine_similarity):
    """Test that the type attribute is correctly set."""
    assert cosine_similarity.type == "CosineSimilarity"


@pytest.mark.unit
def test_check_bounded(cosine_similarity):
    """Test that the similarity measure is bounded."""
    assert cosine_similarity.check_bounded() is True


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y, expected",
    [
        ([1, 0, 0], [1, 0, 0], 1.0),  # Identical vectors
        ([1, 0, 0], [0, 1, 0], 0.0),  # Orthogonal vectors
        ([1, 0, 0], [-1, 0, 0], -1.0),  # Opposite vectors
        ([1, 1, 0], [1, 0, 0], 1 / np.sqrt(2)),  # 45-degree angle
        ([1, 2, 3], [4, 5, 6], 0.9746318461970762),  # Arbitrary vectors
    ],
)
def test_similarity(cosine_similarity, x, y, expected):
    """
    Test the similarity method with various vector pairs.

    Parameters
    ----------
    cosine_similarity : CosineSimilarity
        The similarity measure instance
    x : List
        First vector
    y : List
        Second vector
    expected : float
        Expected similarity value
    """
    result = cosine_similarity.similarity(x, y)
    assert abs(result - expected) < 1e-10


@pytest.mark.unit
def test_similarity_error_handling(cosine_similarity):
    """Test error handling in the similarity method."""
    # Test with zero vectors
    with pytest.raises(ValueError, match="undefined for zero vectors"):
        cosine_similarity.similarity([0, 0, 0], [1, 2, 3])

    # Test with incompatible dimensions
    with pytest.raises(ValueError, match="Incompatible dimensions"):
        cosine_similarity.similarity([1, 2, 3], [1, 2])


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, ys, expected",
    [
        ([1, 0, 0], [[1, 0, 0], [0, 1, 0], [-1, 0, 0]], [1.0, 0.0, -1.0]),
        ([1, 1, 0], [[1, 0, 0], [0, 1, 0]], [1 / np.sqrt(2), 1 / np.sqrt(2)]),
    ],
)
def test_similarities(cosine_similarity, x, ys, expected):
    """
    Test the similarities method with various vectors.

    Parameters
    ----------
    cosine_similarity : CosineSimilarity
        The similarity measure instance
    x : List
        Reference vector
    ys : List[List]
        List of vectors to compare against the reference
    expected : List[float]
        Expected similarity values
    """
    results = cosine_similarity.similarities(x, ys)
    assert len(results) == len(expected)
    for res, exp in zip(results, expected):
        assert abs(res - exp) < 1e-10


@pytest.mark.unit
def test_similarities_error_handling(cosine_similarity):
    """Test error handling in the similarities method."""
    # Test with zero reference vector
    with pytest.raises(ValueError, match="undefined for zero vectors"):
        cosine_similarity.similarities([0, 0, 0], [[1, 2, 3], [4, 5, 6]])

    # Test with zero comparison vector
    with pytest.raises(ValueError, match="undefined for zero vectors"):
        cosine_similarity.similarities([1, 2, 3], [[0, 0, 0], [4, 5, 6]])

    # Test with incompatible dimensions
    with pytest.raises(ValueError, match="Incompatible dimensions"):
        cosine_similarity.similarities([1, 2, 3], [[1, 2], [4, 5, 6]])


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y, expected",
    [
        ([1, 0, 0], [1, 0, 0], 0.0),  # Identical vectors: 1 - 1 = 0
        ([1, 0, 0], [0, 1, 0], 1.0),  # Orthogonal vectors: 1 - 0 = 1
        ([1, 0, 0], [-1, 0, 0], 2.0),  # Opposite vectors: 1 - (-1) = 2
        ([1, 1, 0], [1, 0, 0], 1 - 1 / np.sqrt(2)),  # 45-degree angle
    ],
)
def test_dissimilarity(cosine_similarity, x, y, expected):
    """
    Test the dissimilarity method with various vector pairs.

    Parameters
    ----------
    cosine_similarity : CosineSimilarity
        The similarity measure instance
    x : List
        First vector
    y : List
        Second vector
    expected : float
        Expected dissimilarity value
    """
    result = cosine_similarity.dissimilarity(x, y)
    assert abs(result - expected) < 1e-10


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y",
    [
        ([1, 0, 0], [0, 1, 0]),
        ([1, 2, 3], [4, 5, 6]),
        ([0.5, 0.5], [0.7, 0.7]),
    ],
)
def test_check_symmetry(cosine_similarity, x, y):
    """
    Test that the cosine similarity is symmetric.

    Parameters
    ----------
    cosine_similarity : CosineSimilarity
        The similarity measure instance
    x : List
        First vector
    y : List
        Second vector
    """
    assert cosine_similarity.check_symmetry(x, y) is True
    # Verify explicitly
    sim_xy = cosine_similarity.similarity(x, y)
    sim_yx = cosine_similarity.similarity(y, x)
    assert abs(sim_xy - sim_yx) < 1e-10


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y, expected",
    [
        ([1, 0, 0], [1, 0, 0], True),  # Identical vectors
        ([1, 0, 0], [2, 0, 0], True),  # Same direction, different magnitude
        ([1, 0, 0], [0, 1, 0], True),  # Different directions
        ([1, 1, 0], [2, 2, 0], True),  # Same direction, different magnitude
    ],
)
def test_check_identity_of_discernibles(cosine_similarity, x, y, expected):
    """
    Test the identity of discernibles property.

    Parameters
    ----------
    cosine_similarity : CosineSimilarity
        The similarity measure instance
    x : List
        First vector
    y : List
        Second vector
    expected : bool
        Expected result
    """
    result = cosine_similarity.check_identity_of_discernibles(x, y)
    assert result is expected


@pytest.mark.unit
def test_serialization_deserialization():
    """Test that the CosineSimilarity can be serialized and deserialized correctly."""
    cosine_sim = CosineSimilarity()
    serialized = cosine_sim.model_dump_json()
    deserialized = CosineSimilarity.model_validate_json(serialized)

    # Check that the type is preserved
    assert deserialized.type == "CosineSimilarity"

    # Verify functionality is preserved
    x = [1, 2, 3]
    y = [4, 5, 6]
    assert abs(cosine_sim.similarity(x, y) - deserialized.similarity(x, y)) < 1e-10


@pytest.mark.unit
def test_numerical_stability():
    """Test the numerical stability of the cosine similarity implementation."""
    cosine_sim = CosineSimilarity()

    # Test with very small values
    x = [1e-10, 2e-10, 3e-10]
    y = [4e-10, 5e-10, 6e-10]
    result = cosine_sim.similarity(x, y)
    # The result should be the same as with larger values with the same proportions
    expected = cosine_sim.similarity([1, 2, 3], [4, 5, 6])
    assert abs(result - expected) < 1e-10

    # Test with large values
    x = [1e10, 2e10, 3e10]
    y = [4e10, 5e10, 6e10]
    result = cosine_sim.similarity(x, y)
    assert abs(result - expected) < 1e-10
