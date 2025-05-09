import pytest
from swarmauri_standard.swarmauri_standard.similarities.DiceSimilarity import DiceSimilarity
import logging

@pytest.fixture
def dice_similarity():
    """Fixture providing a fresh instance of DiceSimilarity for each test."""
    return DiceSimilarity()

@pytest.mark.unit
class TestDiceSimilarity:
    """Unit tests for the DiceSimilarity class implementation."""

    def test_class_attributes(self, dice_similarity):
        """Test that class attributes are correctly initialized."""
        assert dice_similarity.resource == "similarity"

    def test_similarity_with_identical_sets(self, dice_similarity):
        """Test similarity calculation with identical sets."""
        a = {1, 2, 3}
        b = {1, 2, 3}
        assert dice_similarity.similarity(a, b) == 1.0

    def test_similarity_with_disjoint_sets(self, dice_similarity):
        """Test similarity calculation with disjoint sets."""
        a = {1, 2, 3}
        b = {4, 5, 6}
        assert dice_similarity.similarity(a, b) == 0.0

    def test_similarity_with_empty_sets(self, dice_similarity):
        """Test similarity calculation with empty sets."""
        a = set()
        b = set()
        assert dice_similarity.similarity(a, b) == 1.0

    def test_similarity_with_lists(self, dice_similarity):
        """Test similarity calculation with lists instead of sets."""
        a = [1, 2, 3]
        b = [1, 2, 3]
        assert dice_similarity.similarity(a, b) == 1.0

    def test_similarities_with_multiple_elements(self, dice_similarity):
        """Test similarities calculation with multiple elements."""
        a = {1, 2, 3}
        b_list = [{1, 2, 3}, set(), {4, 5, 6}]
        expected = (1.0, 1.0, 0.0)
        assert dice_similarity.similarities(a, b_list) == expected

    def test_dissimilarity(self, dice_similarity):
        """Test dissimilarity calculation."""
        a = {1, 2, 3}
        b = {4, 5, 6}
        assert dice_similarity.dissimilarity(a, b) == 1.0

    def test_dissimilarities(self, dice_similarity):
        """Test dissimilarities calculation."""
        a = {1, 2, 3}
        b_list = [{1, 2, 3}, set(), {4, 5, 6}]
        expected = (0.0, 0.0, 1.0)
        assert dice_similarity.dissimilarities(a, b_list) == expected

    def test_check_boundedness(self, dice_similarity):
        """Test that the measure is bounded between 0 and 1."""
        a = {1, 2, 3}
        b = {4, 5, 6}
        assert dice_similarity.check_boundedness(a, b) is True

    def test_check_reflexivity(self, dice_similarity):
        """Test reflexivity of the similarity measure."""
        a = {1, 2, 3}
        assert dice_similarity.check_reflexivity(a) is True

    def test_check_symmetry(self, dice_similarity):
        """Test symmetry of the similarity measure."""
        a = {1, 2, 3}
        b = {3, 2, 1}
        assert dice_similarity.check_symmetry(a, b) is True

    def test_check_identity(self, dice_similarity):
        """Test identity property of the similarity measure."""
        a = {1, 2, 3}
        b = {1, 2, 3}
        assert dice_similarity.check_identity(a, b) is True

    def test_check_identity_with_different_sets(self, dice_similarity):
        """Test identity property with different sets."""
        a = {1, 2, 3}
        b = {4, 5, 6}
        assert dice_similarity.check_identity(a, b) is False

    def test_similarity_raises_value_error_on_none(self, dice_similarity):
        """Test that similarity raises ValueError with None inputs."""
        a = None
        b = {1, 2, 3}
        with pytest.raises(ValueError):
            dice_similarity.similarity(a, b)

    def test_similarity_with_empty_iterables(self, dice_similarity):
        """Test similarity calculation with empty iterables."""
        a = set()
        b = set()
        assert dice_similarity.similarity(a, b) == 1.0

    def test_similarity_with_partial_overlap(self, dice_similarity):
        """Test similarity calculation with partially overlapping sets."""
        a = {1, 2, 3}
        b = {2, 3, 4}
        expected = 2 * 2 / (3 + 3)  # 4/6 = 2/3
        assert dice_similarity.similarity(a, b) == expected

    def test_similarity_with_tuple_inputs(self, dice_similarity):
        """Test similarity calculation with tuple inputs."""
        a = (1, 2, 3)
        b = (1, 2, 3)
        assert dice_similarity.similarity(a, b) == 1.0