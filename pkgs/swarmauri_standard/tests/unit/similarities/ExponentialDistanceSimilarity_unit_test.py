import pytest
import numpy as np
import logging
from swarmauri_standard.similarities.ExponentialDistanceSimilarity import (
    ExponentialDistanceSimilarity,
)


@pytest.mark.unit
class TestExponentialDistanceSimilarity:
    """Unit tests for the ExponentialDistanceSimilarity class."""

    def test_similarity(self):
        """Test similarity calculation between two elements."""
        similarity = ExponentialDistanceSimilarity()

        # Test identical elements
        x = [1, 2, 3]
        y = [1, 2, 3]
        assert similarity.similarity(x, y) == 1.0

        # Test different elements
        x = [0, 0, 0]
        y = [1, 1, 1]
        assert 0 < similarity.similarity(x, y) < 1

        # Test numpy array inputs
        x = np.array([0, 0, 0])
        y = np.array([1, 1, 1])
        assert 0 < similarity.similarity(x, y) < 1

        # Test custom scale
        similarity_custom_scale = ExponentialDistanceSimilarity(scale=0.5)
        x = [0, 0, 0]
        y = [1, 1, 1]
        assert similarity_custom_scale.similarity(x, y) < similarity.similarity(x, y)

    def test_similarities(self):
        """Test similarity calculation for multiple pairs."""
        similarity = ExponentialDistanceSimilarity()

        # Test with matching lengths
        xs = [[1, 2], [3, 4], [5, 6]]
        ys = [[1, 2], [3, 4], [5, 6]]
        similarities = similarity.similarities(xs, ys)
        assert all(score == 1.0 for score in similarities)

        # Test with different lengths
        xs = [[1, 2], [3, 4]]
        ys = [[1, 2], [3, 4], [5, 6]]
        with pytest.raises(ValueError):
            similarity.similarities(xs, ys)

    def test_dissimilarity(self):
        """Test dissimilarity calculation between two elements."""
        similarity = ExponentialDistanceSimilarity()

        # Test identical elements
        x = [1, 2, 3]
        y = [1, 2, 3]
        assert similarity.dissimilarity(x, y) == 0.0

        # Test different elements
        x = [0, 0, 0]
        y = [1, 1, 1]
        assert 0 < similarity.dissimilarity(x, y) < 1

        # Test numpy array inputs
        x = np.array([0, 0, 0])
        y = np.array([1, 1, 1])
        assert 0 < similarity.dissimilarity(x, y) < 1

        # Test custom scale
        similarity_custom_scale = ExponentialDistanceSimilarity(scale=0.5)
        x = [0, 0, 0]
        y = [1, 1, 1]
        assert similarity_custom_scale.dissimilarity(x, y) > similarity.dissimilarity(
            x, y
        )

    def test_dissimilarities(self):
        """Test dissimilarity calculation for multiple pairs."""
        similarity = ExponentialDistanceSimilarity()

        # Test with matching lengths
        xs = [[1, 2], [3, 4], [5, 6]]
        ys = [[1, 2], [3, 4], [5, 6]]
        dissimilarities = similarity.dissimilarities(xs, ys)
        assert all(score == 0.0 for score in dissimilarities)

        # Test with different lengths
        xs = [[1, 2], [3, 4]]
        ys = [[1, 2], [3, 4], [5, 6]]
        with pytest.raises(ValueError):
            similarity.dissimilarities(xs, ys)

    def test_check_boundedness(self):
        """Test if the similarity measure is bounded."""
        similarity = ExponentialDistanceSimilarity()
        assert similarity.check_boundedness() is True

    def test_check_reflexivity(self):
        """Test if the similarity measure satisfies reflexivity."""
        similarity = ExponentialDistanceSimilarity()
        assert similarity.check_reflexivity() is True

    def test_check_symmetry(self):
        """Test if the similarity measure is symmetric."""
        similarity = ExponentialDistanceSimilarity()
        assert similarity.check_symmetry() is True

    def test_check_identity(self):
        """Test if the similarity measure satisfies identity of discernibles."""
        similarity = ExponentialDistanceSimilarity()
        assert similarity.check_identity() is True

    def test_custom_distance_function(self):
        """Test using a custom distance function."""

        def custom_distance(x, y):
            return np.sum(np.abs(x - y))

        similarity = ExponentialDistanceSimilarity(distance_fn=custom_distance)

        x = [1, 2, 3]
        y = [1, 2, 3]
        assert similarity.similarity(x, y) == 1.0

        x = [0, 0, 0]
        y = [1, 1, 1]
        similarity_score = similarity.similarity(x, y)
        assert 0 < similarity_score < 1

    def test_logging(self, caplog):
        """Test if logging statements are generated."""
        similarity = ExponentialDistanceSimilarity()

        x = [1, 2, 3]
        y = [1, 2, 3]
        similarity.similarity(x, y)

        x = [0, 0, 0]
        y = [1, 1, 1]
        similarity.similarity(x, y)

        with caplog.at_level(logging.DEBUG):
            assert "Similarity between" in caplog.text

    def test_initialization(self):
        """Test initialization with different parameters."""
        # Default initialization
        similarity_default = ExponentialDistanceSimilarity()
        assert similarity_default.scale == 1.0

        # Custom scale initialization
        similarity_custom_scale = ExponentialDistanceSimilarity(scale=0.5)
        assert similarity_custom_scale.scale == 0.5

        # Custom distance function initialization
        def custom_distance(x, y):
            return np.sum(np.abs(x - y))

        similarity_custom_distance = ExponentialDistanceSimilarity(
            distance_fn=custom_distance
        )
        assert similarity_custom_distance.distance_fn is custom_distance
