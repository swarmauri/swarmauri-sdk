import pytest
import numpy as np
import logging
from swarmauri_standard.similarities.GaussianRBFSimilarity import GaussianRBFSimilarity

logger = logging.getLogger(__name__)


@pytest.fixture
def gaussianrbfsimilarity():
    """
    Fixture providing a GaussianRBFSimilarity instance with default parameters.
    """
    return GaussianRBFSimilarity(gamma=1.0)


@pytest.mark.unit
def test_resource():
    """
    Test that the resource property returns the correct value.
    """
    assert GaussianRBFSimilarity.resource == "Similarity"


@pytest.mark.unit
def test_type():
    """
    Test that the type property returns the correct value.
    """
    assert GaussianRBFSimilarity.type == "GaussianRBFSimilarity"


@pytest.mark.unit
def test_similarity(gaussianrbfsimilarity):
    """
    Test the similarity method with various input types and values.
    """
    # Test with 0D arrays (scalars)
    x = 1.0
    y = 2.0
    similarity = gaussianrbfsimilarity.similarity(x, y)
    assert isinstance(similarity, float)

    # Test with 1D arrays
    x = np.array([1.0, 2.0])
    y = np.array([3.0, 4.0])
    similarity = gaussianrbfsimilarity.similarity(x, y)
    assert isinstance(similarity, float)

    # Test with 2D arrays
    x = np.array([[1.0, 2.0], [3.0, 4.0]])
    y = np.array([[5.0, 6.0], [7.0, 8.0]])
    similarity = gaussianrbfsimilarity.similarity(x, y)
    assert isinstance(similarity, float)

    # Test with 3D arrays
    x = np.random.rand(2, 3, 4)
    y = np.random.rand(2, 3, 4)
    similarity = gaussianrbfsimilarity.similarity(x, y)
    assert isinstance(similarity, float)


@pytest.mark.unit
@pytest.mark.parametrize(
    "gamma,expected_exception",
    [(0.0, ValueError), (-1.0, ValueError), (-0.5, ValueError)],
)
def test_init_invalid_gamma(gamma, expected_exception):
    """
    Test that initializing with invalid gamma values raises ValueError.
    """
    with pytest.raises(expected_exception):
        GaussianRBFSimilarity(gamma=gamma)


@pytest.mark.unit
def test_dissimilarity(gaussianrbfsimilarity):
    """
    Test the dissimilarity method with various input types and values.
    """
    # Test with 0D arrays (scalars)
    x = 1.0
    y = 2.0
    dissimilarity = gaussianrbfsimilarity.dissimilarity(x, y)
    assert isinstance(dissimilarity, float)

    # Test with 1D arrays
    x = np.array([1.0, 2.0])
    y = np.array([3.0, 4.0])
    dissimilarity = gaussianrbfsimilarity.dissimilarity(x, y)
    assert isinstance(dissimilarity, float)

    # Test with 2D arrays
    x = np.array([[1.0, 2.0], [3.0, 4.0]])
    y = np.array([[5.0, 6.0], [7.0, 8.0]])
    dissimilarity = gaussianrbfsimilarity.dissimilarity(x, y)
    assert isinstance(dissimilarity, float)

    # Test with 3D arrays
    x = np.random.rand(2, 3, 4)
    y = np.random.rand(2, 3, 4)
    dissimilarity = gaussianrbfsimilarity.dissimilarity(x, y)
    assert isinstance(dissimilarity, float)


@pytest.mark.unit
def test_check_boundedness(gaussianrbfsimilarity):
    """
    Test that check_boundedness returns True.
    """
    assert gaussianrbfsimilarity.check_boundedness() is True


@pytest.mark.unit
def test_check_reflexivity(gaussianrbfsimilarity):
    """
    Test that the similarity measure is reflexive.
    """
    # Test with 0D arrays (scalars)
    x = 1.0
    y = x
    similarity = gaussianrbfsimilarity.similarity(x, y)
    assert similarity == 1.0

    # Test with 1D arrays
    x = np.array([1.0, 2.0])
    y = x
    similarity = gaussianrbfsimilarity.similarity(x, y)
    assert similarity == 1.0

    # Test with 2D arrays
    x = np.array([[1.0, 2.0], [3.0, 4.0]])
    y = x
    similarity = gaussianrbfsimilarity.similarity(x, y)
    assert similarity == 1.0

    # Test with 3D arrays
    x = np.random.rand(2, 3, 4)
    y = x
    similarity = gaussianrbfsimilarity.similarity(x, y)
    assert similarity == 1.0


@pytest.mark.unit
def test_check_symmetry(gaussianrbfsimilarity):
    """
    Test that the similarity measure is symmetric.
    """
    x = np.array([1.0, 2.0])
    y = np.array([3.0, 4.0])

    similarity_xy = gaussianrbfsimilarity.similarity(x, y)
    similarity_yx = gaussianrbfsimilarity.similarity(y, x)

    assert similarity_xy == similarity_yx


@pytest.mark.unit
def test_check_identity(gaussianrbfsimilarity):
    """
    Test that the similarity measure satisfies identity of discernibles.
    """
    x = np.array([1.0, 2.0])
    y = np.array([3.0, 4.0])

    similarity = gaussianrbfsimilarity.similarity(x, y)
    assert similarity < 1.0
