import pytest
from swarmauri_standard.swarmauri_standard.similarities.OverlapCoefficientSimilarity import OverlapCoefficientSimilarity
import logging

@pytest.mark.unit
class TestOverlapCoefficientSimilarity:
    """Unit tests for OverlapCoefficientSimilarity class."""

    @pytest.mark.parametrize("a,b,expected_similarity", [
        (set(), set(), 0.0),
        (set(), {1, 2, 3}, 0.0),
        ({1, 2}, {1, 2}, 1.0),
        ({1, 2}, {2, 3}, 0.5),
        ({1, 2, 3}, {1, 2}, 1.0),  # a is larger than b
        ({1, 2, 3, 4}, {2, 3, 4, 5}, 3/4),
    ])
    def test_similarity(self, a, b, expected_similarity):
        """Test the similarity calculation between two sets."""
        similarity = OverlapCoefficientSimilarity().similarity(a, b)
        assert similarity == expected_similarity

    @pytest.mark.parametrize("a,b,expected_exception", [
        (None, {1, 2}, ValueError),
        ({1, 2}, None, ValueError),
        ("not a set", {1, 2}, ValueError),
        ({1, 2}, "not a set", ValueError),
    ])
    def test_similarity_invalid_input(self, a, b, expected_exception):
        """Test that invalid input raises the correct exception."""
        with pytest.raises(expected_exception):
            OverlapCoefficientSimilarity().similarity(a, b)

    def test_similarities(self):
        """Test the similarities method with multiple sets."""
        a = {1, 2, 3}
        b_list = [{1, 2}, {2, 3}, {3, 4}]
        expected = (
            OverlapCoefficientSimilarity().similarity(a, b_list[0]),
            OverlapCoefficientSimilarity().similarity(a, b_list[1]),
            OverlapCoefficientSimilarity().similarity(a, b_list[2])
        )
        
        similarities = OverlapCoefficientSimilarity().similarities(a, b_list)
        assert len(similarities) == len(b_list)
        assert similarities == expected

    def test_dissimilarity(self):
        """Test the dissimilarity calculation."""
        a = {1, 2}
        b = {2, 3}
        similarity = OverlapCoefficientSimilarity().similarity(a, b)
        dissimilarity = OverlapCoefficientSimilarity().dissimilarity(a, b)
        assert dissimilarity == 1.0 - similarity

    def test_dissimilarities(self):
        """Test the dissimilarities method with multiple sets."""
        a = {1, 2, 3}
        b_list = [{1, 2}, {2, 3}, {3, 4}]
        similarities = OverlapCoefficientSimilarity().similarities(a, b_list)
        dissimilarities = OverlapCoefficientSimilarity().dissimilarities(a, b_list)
        assert len(dissimilarities) == len(b_list)
        assert all(1.0 - s for s in similarities)

    def test_check_boundedness(self):
        """Test that the measure is bounded."""
        a = {1, 2}
        b = {2, 3}
        assert OverlapCoefficientSimilarity().check_boundedness(a, b) is True

    def test_check_reflexivity(self):
        """Test reflexivity of the measure."""
        a = {1, 2}
        assert OverlapCoefficientSimilarity().check_reflexivity(a) is True

    @pytest.mark.parametrize("a,b", [
        ({1, 2}, {2, 3}),
        ({1, 2, 3}, {3, 4, 5}),
        ({1, 2}, {1, 2}),
    ])
    def test_check_symmetry(self, a, b):
        """Test the symmetry of the measure."""
        similarity_ab = OverlapCoefficientSimilarity().similarity(a, b)
        similarity_ba = OverlapCoefficientSimilarity().similarity(b, a)
        assert similarity_ab == similarity_ba

    @pytest.mark.parametrize("a,b,expected", [
        ({1, 2}, {1, 2}, True),
        ({1, 2}, {2, 3}, False),
        ({1, 2, 3}, {1, 2, 3}, True),
    ])
    def test_check_identity(self, a, b, expected):
        """Test the identity check of the measure."""
        assert OverlapCoefficientSimilarity().check_identity(a, b) == expected