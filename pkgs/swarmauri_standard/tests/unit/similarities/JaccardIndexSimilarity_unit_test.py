import pytest
from swarmauri_standard.similarities.JaccardIndexSimilarity import JaccardIndexSimilarity

@pytest.mark.unit
class TestJaccardIndexSimilarity:
    """Unit tests for JaccardIndexSimilarity class."""

    @pytest.fixture(scope="class")
    def fixture_jaccard_index_similarity(self):
        """Fixture to provide a JaccardIndexSimilarity instance for testing."""
        return JaccardIndexSimilarity()

    def test_constructor(self, fixture_jaccard_index_similarity):
        """Test that the JaccardIndexSimilarity instance is properly initialized."""
        assert isinstance(fixture_jaccard_index_similarity, JaccardIndexSimilarity)

    def test_resource(self, fixture_jaccard_index_similarity):
        """Test the resource property."""
        assert fixture_jaccard_index_similarity.resource == "JACCARD_INDEX_SIMILARITY"

    def test_type(self, fixture_jaccard_index_similarity):
        """Test the type property."""
        assert fixture_jaccard_index_similarity.type == "JaccardIndexSimilarity"

    def test_similarity_empty_sets(self, fixture_jaccard_index_similarity):
        """Test similarity calculation with empty sets."""
        similarity = fixture_jaccard_index_similarity.similarity(set(), set())
        assert similarity == 0.0

    def test_similarity_non_empty_sets(self, fixture_jaccard_index_similarity):
        """Test similarity calculation with non-empty sets."""
        x = {1, 2, 3}
        y = {2, 3, 4}
        similarity = fixture_jaccard_index_similarity.similarity(x, y)
        assert similarity == 2/5  # Intersection size 2, union size 5

    def test_similarity_lists(self, fixture_jaccard_index_similarity):
        """Test similarity calculation with lists."""
        x = [1, 2, 3]
        y = [2, 3, 4]
        similarity = fixture_jaccard_index_similarity.similarity(x, y)
        assert similarity == 2/5

    def test_similarity_tuples(self, fixture_jaccard_index_similarity):
        """Test similarity calculation with tuples."""
        x = (1, 2, 3)
        y = (2, 3, 4)
        similarity = fixture_jaccard_index_similarity.similarity(x, y)
        assert similarity == 2/5

    def test_similarity_invalid_inputs(self, fixture_jaccard_index_similarity):
        """Test similarity with invalid input types."""
        with pytest.raises(ValueError):
            fixture_jaccard_index_similarity.similarity(123, [1,2,3])

    def test_similarities_multiple_pairs(self, fixture_jaccard_index_similarity):
        """Test multiple similarities calculation."""
        xs = [{1, 2}, {3, 4}]
        ys = [{2, 3}, {4, 5}]
        expected = [2/4, 2/4]  # Each pair has intersection size 1, union size 3
        similarities = fixture_jaccard_index_similarity.similarities(xs, ys)
        assert similarities == pytest.approx(expected)

    def test_dissimilarity(self, fixture_jaccard_index_similarity):
        """Test dissimilarity calculation."""
        x = {1, 2, 3}
        y = {2, 3, 4}
        similarity = 2/5
        dissimilarity = fixture_jaccard_index_similarity.dissimilarity(x, y)
        assert dissimilarity == 1.0 - similarity

    def test_dissimilarities_multiple_pairs(self, fixture_jaccard_index_similarity):
        """Test multiple dissimilarities calculation."""
        xs = [{1, 2}, {3, 4}]
        ys = [{2, 3}, {4, 5}]
        expected = [1.0 - (1/3), 1.0 - (1/3)]
        dissimilarities = fixture_jaccard_index_similarity.dissimilarities(xs, ys)
        assert dissimilarities == pytest.approx(expected)

    def test_check_boundedness(self, fixture_jaccard_index_similarity):
        """Test if the measure is bounded."""
        assert fixture_jaccard_index_similarity.check_boundedness() is True

    def test_check_reflexivity(self, fixture_jaccard_index_similarity):
        """Test if the measure satisfies reflexivity."""
        assert fixture_jaccard_index_similarity.check_reflexivity() is True

    def test_check_symmetry(self, fixture_jaccard_index_similarity):
        """Test if the measure is symmetric."""
        assert fixture_jaccard_index_similarity.check_symmetry() is True

    def test_check_identity(self, fixture_jaccard_index_similarity):
        """Test if the measure satisfies identity of discernibles."""
        assert fixture_jaccard_index_similarity.check_identity() is True