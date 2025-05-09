import pytest
import logging
from swarmauri_standard.similarities.TanimotoSimilarity import TanimotoSimilarity

logger = logging.getLogger(__name__)


@pytest.mark.unit
def test_tanimoto_similarity_init():
    """Test initialization of TanimotoSimilarity class."""
    similarity = TanimotoSimilarity()
    assert similarity.type == "TanimotoSimilarity"
    assert similarity.is_symmetric is True
    assert similarity.is_bounded is True


@pytest.mark.unit
@pytest.mark.parametrize(
    "x,y,expected_similarity",
    [
        ([1.0, 0.0], [1.0, 0.0], 1.0),
        ([1.0, 0.0], [0.0, 1.0], 0.0),
        ([1.0, 1.0], [1.0, 1.0], 1.0),
        ([1.0, 1.0], [1.0, 0.0], 0.5),
        ([0.0, 0.0], [0.0, 0.0], 1.0),
        ([0.0, 0.0], [1.0, 1.0], 0.0),
    ],
)
def test_tanimoto_similarity(x, y, expected_similarity):
    """Test Tanimoto similarity calculations with various inputs."""
    similarity = TanimotoSimilarity()
    result = similarity.similarity(x, y)
    assert result == pytest.approx(expected_similarity)


@pytest.mark.unit
def test_tanimoto_similarities_batch():
    """Test batch Tanimoto similarity calculations."""
    x = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
    y = [[1.0, 0.0], [1.0, 1.0], [0.0, 0.0]]
    expected = [1.0, 0.5, 0.0]
    similarity = TanimotoSimilarity()
    results = similarity.similarities(x, y)
    for res, exp in zip(results, expected):
        assert res == pytest.approx(exp)


@pytest.mark.unit
@pytest.mark.parametrize(
    "x,y,expected_dissimilarity",
    [
        ([1.0, 0.0], [1.0, 0.0], 0.0),
        ([1.0, 0.0], [0.0, 1.0], 1.0),
        ([1.0, 1.0], [1.0, 1.0], 0.0),
        ([1.0, 1.0], [1.0, 0.0], 0.5),
        ([0.0, 0.0], [0.0, 0.0], 0.0),
        ([0.0, 0.0], [1.0, 1.0], 1.0),
    ],
)
def test_tanimoto_dissimilarity(x, y, expected_dissimilarity):
    """Test Tanimoto dissimilarity calculations with various inputs."""
    similarity = TanimotoSimilarity()
    result = similarity.dissimilarity(x, y)
    assert result == pytest.approx(expected_dissimilarity)


@pytest.mark.unit
def test_tanimoto_dissimilarities_batch():
    """Test batch Tanimoto dissimilarity calculations."""
    x = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
    y = [[1.0, 0.0], [1.0, 1.0], [0.0, 0.0]]
    expected = [0.0, 0.5, 1.0]
    similarity = TanimotoSimilarity()
    results = similarity.dissimilarities(x, y)
    for res, exp in zip(results, expected):
        assert res == pytest.approx(exp)


@pytest.mark.unit
def test_tanimoto_similarity_check_boundedness():
    """Test if Tanimoto similarity is bounded between 0 and 1."""
    similarity = TanimotoSimilarity()
    assert similarity.check_boundedness() is True


@pytest.mark.unit
def test_tanimoto_similarity_check_reflexivity():
    """Test if Tanimoto similarity satisfies reflexivity."""
    similarity = TanimotoSimilarity()
    assert similarity.check_reflexivity() is True


@pytest.mark.unit
def test_tanimoto_similarity_check_symmetry():
    """Test if Tanimoto similarity is symmetric."""
    similarity = TanimotoSimilarity()
    assert similarity.check_symmetry() is True


@pytest.mark.unit
def test_tanimoto_similarity_check_identity():
    """Test if Tanimoto similarity satisfies identity of discernibles."""
    similarity = TanimotoSimilarity()
    assert similarity.check_identity() is False
