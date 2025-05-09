import pytest
import logging
from swarmauri_standard.swarmauri_standard.similarities.TriangleCosineSimilarity import (
    TriangleCosineSimilarity,
)


@pytest.mark.unit
class TestTriangleCosineSimilarity:
    """Unit tests for TriangleCosineSimilarity class."""

    def test_similarity_zero_vectors(self):
        """Test that similarity raises ValueError for zero vectors."""
        logger = logging.getLogger(__name__)
        triangle_cosine = TriangleCosineSimilarity()

        with pytest.raises(ValueError):
            triangle_cosine.similarity([0.0, 0.0], [1.0, 2.0])

        with pytest.raises(ValueError):
            triangle_cosine.similarity([1.0, 2.0], [0.0, 0.0])

    def test_similarity_different_length_vectors(self):
        """Test that similarity raises ValueError for vectors of different lengths."""
        logger = logging.getLogger(__name__)
        triangle_cosine = TriangleCosineSimilarity()

        with pytest.raises(ValueError):
            triangle_cosine.similarity([1.0, 2.0], [3.0, 4.0, 5.0])

    @pytest.mark.parametrize(
        "x,y,expected_similarity",
        [
            ([3.0, 4.0], [3.0, 4.0], 1.0),  # Identical vectors
            ([1.0, 0.0], [0.0, 1.0], 0.0),  # Orthogonal vectors
            ([1.0, 1.0], [1.0, 0.0], 0.7071067811865476),  # 45 degree angle
        ],
    )
    def test_similarity_valid_vectors(self, x, y, expected_similarity):
        """Test that similarity returns correct values for valid vectors."""
        logger = logging.getLogger(__name__)
        triangle_cosine = TriangleCosineSimilarity()

        similarity = triangle_cosine.similarity(x, y)
        assert abs(similarity - expected_similarity) < 1e-9

    def test_dissimilarity(self):
        """Test that dissimilarity returns 1 - similarity."""
        logger = logging.getLogger(__name__)
        triangle_cosine = TriangleCosineSimilarity()

        x = [1.0, 2.0]
        y = [2.0, 1.0]
        similarity = triangle_cosine.similarity(x, y)
        dissimilarity = triangle_cosine.dissimilarity(x, y)

        assert abs(dissimilarity - (1.0 - similarity)) < 1e-9

    def test_similarities_single_vector(self):
        """Test that similarities returns single similarity score."""
        logger = logging.getLogger(__name__)
        triangle_cosine = TriangleCosineSimilarity()

        x = [1.0, 2.0]
        y = [2.0, 1.0]
        score = triangle_cosine.similarities(x, y)

        assert isinstance(score, float)

    def test_similarities_multiple_vectors(self):
        """Test that similarities returns list of scores for multiple vectors."""
        logger = logging.getLogger(__name__)
        triangle_cosine = TriangleCosineSimilarity()

        x = [1.0, 2.0]
        ys = [[2.0, 1.0], [3.0, 4.0]]
        scores = triangle_cosine.similarities(x, ys)

        assert isinstance(scores, list)
        assert len(scores) == len(ys)

    def test_check_boundedness(self):
        """Test that check_boundedness returns True."""
        logger = logging.getLogger(__name__)
        triangle_cosine = TriangleCosineSimilarity()

        x = [1.0, 2.0]
        y = [2.0, 1.0]
        bounded = triangle_cosine.check_boundedness(x, y)
        assert bounded is True

    @pytest.mark.parametrize(
        "x,expected_reflexive", [([1.0, 2.0], True), ([0.0, 0.0], False)]
    )
    def test_check_reflexivity(self, x, expected_reflexive):
        """Test that check_reflexivity returns correct value."""
        logger = logging.getLogger(__name__)
        triangle_cosine = TriangleCosineSimilarity()

        reflexive = triangle_cosine.check_reflexivity(x)
        assert reflexive == expected_reflexive

    def test_check_symmetry(self):
        """Test that check_symmetry returns True."""
        logger = logging.getLogger(__name__)
        triangle_cosine = TriangleCosineSimilarity()

        x = [1.0, 2.0]
        y = [2.0, 1.0]
        symmetric = triangle_cosine.check_symmetry(x, y)
        assert symmetric is True

    @pytest.mark.parametrize(
        "x,y,expected_identity",
        [([1.0, 2.0], [1.0, 2.0], True), ([1.0, 2.0], [2.0, 1.0], False)],
    )
    def test_check_identity(self, x, y, expected_identity):
        """Test that check_identity returns correct value."""
        logger = logging.getLogger(__name__)
        triangle_cosine = TriangleCosineSimilarity()

        identical = triangle_cosine.check_identity(x, y)
        assert identical == expected_identity
