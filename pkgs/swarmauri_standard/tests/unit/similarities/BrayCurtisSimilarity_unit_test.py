import pytest
import numpy as np
from swarmauri_standard.swarmauri_standard.similarities.BrayCurtisSimilarity import (
    BrayCurtisSimilarity,
)


@pytest.mark.unit
class TestBrayCurtisSimilarity:
    """Unit test class for BrayCurtisSimilarity class."""

    def test_similarity_basic_case(self):
        """Test basic functionality of similarity method."""
        bray_curtis = BrayCurtisSimilarity()
        x = np.array([1, 2, 3])
        y = np.array([4, 5, 6])
        expected_similarity = 1 - (np.sum(np.abs(x - y)) / (np.sum(x) + np.sum(y)))
        assert bray_curtis.similarity(x, y) == pytest.approx(expected_similarity)

    def test_similarity_identical_vectors(self):
        """Test similarity when input vectors are identical."""
        bray_curtis = BrayCurtisSimilarity()
        x = np.array([1, 2, 3])
        y = np.array([1, 2, 3])
        assert bray_curtis.similarity(x, y) == 1.0

    def test_similarity_zero_vectors(self):
        """Test similarity when both vectors are zero vectors."""
        bray_curtis = BrayCurtisSimilarity()
        x = np.array([0, 0, 0])
        y = np.array([0, 0, 0])
        assert bray_curtis.similarity(x, y) == 1.0

    def test_similarity_one_zero_vector(self):
        """Test similarity when one vector is zero."""
        bray_curtis = BrayCurtisSimilarity()
        x = np.array([1, 2, 3])
        y = np.array([0, 0, 0])
        assert bray_curtis.similarity(x, y) == 0.0

    def test_similarity_negative_values(self):
        """Test that similarity raises ValueError for negative values."""
        bray_curtis = BrayCurtisSimilarity()
        x = np.array([1, -2, 3])
        y = np.array([4, 5, 6])
        with pytest.raises(ValueError):
            bray_curtis.similarity(x, y)

    def test_similarities_multiple_pairs(self):
        """Test similarities method with multiple pairs."""
        bray_curtis = BrayCurtisSimilarity()
        pairs = [
            (np.array([1, 2]), np.array([4, 5])),
            (np.array([0, 0]), np.array([0, 0])),
            (np.array([3, 3]), np.array([3, 3])),
        ]
        expected = [
            1 - (np.sum(np.abs([1 - 4, 2 - 5])) / (np.sum([1, 2]) + np.sum([4, 5]))),
            1.0,
            1.0,
        ]
        similarities = bray_curtis.similarities(pairs)
        for s, e in zip(similarities, expected):
            assert s == pytest.approx(e)

    def test_dissimilarity_basic_case(self):
        """Test basic functionality of dissimilarity method."""
        bray_curtis = BrayCurtisSimilarity()
        x = np.array([1, 2, 3])
        y = np.array([4, 5, 6])
        expected_dissimilarity = np.sum(np.abs(x - y)) / (np.sum(x) + np.sum(y))
        assert bray_curtis.dissimilarity(x, y) == pytest.approx(expected_dissimilarity)

    def test_dissimilarity_identical_vectors(self):
        """Test dissimilarity when input vectors are identical."""
        bray_curtis = BrayCurtisSimilarity()
        x = np.array([1, 2, 3])
        y = np.array([1, 2, 3])
        assert bray_curtis.dissimilarity(x, y) == 0.0

    def test_dissimilarity_zero_vectors(self):
        """Test dissimilarity when both vectors are zero vectors."""
        bray_curtis = BrayCurtisSimilarity()
        x = np.array([0, 0, 0])
        y = np.array([0, 0, 0])
        assert bray_curtis.dissimilarity(x, y) == 0.0

    def test_dissimilarity_one_zero_vector(self):
        """Test dissimilarity when one vector is zero."""
        bray_curtis = BrayCurtisSimilarity()
        x = np.array([1, 2, 3])
        y = np.array([0, 0, 0])
        assert bray_curtis.dissimilarity(x, y) == 1.0

    def test_dissimilarity_negative_values(self):
        """Test that dissimilarity raises ValueError for negative values."""
        bray_curtis = BrayCurtisSimilarity()
        x = np.array([1, -2, 3])
        y = np.array([4, 5, 6])
        with pytest.raises(ValueError):
            bray_curtis.dissimilarity(x, y)

    def test_dissimilarities_multiple_pairs(self):
        """Test dissimilarities method with multiple pairs."""
        bray_curtis = BrayCurtisSimilarity()
        pairs = [
            (np.array([1, 2]), np.array([4, 5])),
            (np.array([0, 0]), np.array([0, 0])),
            (np.array([3, 3]), np.array([3, 3])),
        ]
        expected = [
            np.sum(np.abs([1 - 4, 2 - 5])) / (np.sum([1, 2]) + np.sum([4, 5])),
            0.0,
            0.0,
        ]
        dissimilarities = bray_curtis.dissimilarities(pairs)
        for d, e in zip(dissimilarities, expected):
            assert d == pytest.approx(e)

    def test_type_attribute(self):
        """Test that type attribute is correctly set."""
        assert BrayCurtisSimilarity.type == "BrayCurtisSimilarity"

    def test_resource_attribute(self):
        """Test that resource attribute is correctly set."""
        assert BrayCurtisSimilarity.resource == "Similarity"
