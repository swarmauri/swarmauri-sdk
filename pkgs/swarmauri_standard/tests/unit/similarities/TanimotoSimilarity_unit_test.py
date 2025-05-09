import pytest
import logging
from swarmauri_standard.swarmauri_standard.similarities.TanimotoSimilarity import TanimotoSimilarity

@pytest.fixture
def tanimoto_similarity():
    """Fixture to provide a TanimotoSimilarity instance for testing."""
    return TanimotoSimilarity()

@pytest.mark.unit
class TestTanimotoSimilarity:
    """
    Unit tests for the TanimotoSimilarity class.
    
    This class contains tests for the TanimotoSimilarity implementation, ensuring 
    the correctness of similarity calculations for various input scenarios.
    """
    
    def test_class_attributes(self, tanimoto_similarity):
        """
        Test that class attributes are correctly set.
        """
        assert tanimoto_similarity.type == "TanimotoSimilarity"
        assert tanimoto_similarity.resource == "Similarity"

    @pytest.mark.parametrize("x,y,expected_similarity", [
        ([1.0, 0.0], [1.0, 0.0], 1.0),
        ([1.0, 2.0], [1.0, 2.0], 1.0),
        ([1.0, 0.0], [0.0, 1.0], 0.0),
        ([1.0, 1.0], [1.0, 1.0], 1.0),
        ([0.5, 0.5], [0.5, 0.5], 1.0),
        ([1.0, 0.0, 1.0], [1.0, 1.0, 0.0], 0.0),
    ])
    def test_similarity(self, tanimoto_similarity, x, y, expected_similarity):
        """
        Test the similarity method with various input vectors.
        """
        similarity = tanimoto_similarity.similarity(x, y)
        assert pytest.approx(similarity, expected_similarity)

    @pytest.mark.parametrize("pairs,expected_similarities", [
        ([([1.0, 0.0], [1.0, 0.0]), ([1.0, 1.0], [1.0, 1.0])], [1.0, 1.0]),
        ([([1.0, 0.0], [0.0, 1.0]), ([1.0, 1.0], [0.0, 0.0])], [0.0, 0.0]),
    ])
    def test_similarities(self, tanimoto_similarity, pairs, expected_similarities):
        """
        Test the similarities method with multiple pairs of vectors.
        """
        similarities = tanimoto_similarity.similarities(pairs)
        for calculated, expected in zip(similarities, expected_similarities):
            assert pytest.approx(calculated, expected)

    @pytest.mark.parametrize("x,y,expected_dissimilarity", [
        ([1.0, 0.0], [1.0, 0.0], 0.0),
        ([1.0, 2.0], [1.0, 2.0], 0.0),
        ([1.0, 0.0], [0.0, 1.0], 1.0),
        ([1.0, 1.0], [1.0, 1.0], 0.0),
        ([0.5, 0.5], [0.5, 0.5], 0.0),
        ([1.0, 0.0, 1.0], [1.0, 1.0, 0.0], 1.0),
    ])
    def test_dissimilarity(self, tanimoto_similarity, x, y, expected_dissimilarity):
        """
        Test the dissimilarity method with various input vectors.
        """
        dissimilarity = tanimoto_similarity.dissimilarity(x, y)
        assert pytest.approx(dissimilarity, expected_dissimilarity)

    @pytest.mark.parametrize("pairs,expected_dissimilarities", [
        ([([1.0, 0.0], [1.0, 0.0]), ([1.0, 1.0], [1.0, 1.0])], [0.0, 0.0]),
        ([([1.0, 0.0], [0.0, 1.0]), ([1.0, 1.0], [0.0, 0.0])], [1.0, 1.0]),
    ])
    def test_dissimilarities(self, tanimoto_similarity, pairs, expected_dissimilarities):
        """
        Test the dissimilarities method with multiple pairs of vectors.
        """
        dissimilarities = tanimoto_similarity.dissimilarities(pairs)
        for calculated, expected in zip(dissimilarities, expected_dissimilarities):
            assert pytest.approx(calculated, expected)

    @pytest.mark.parametrize("x,y", [
        ([], [1.0]),
        ([1.0], []),
        ([1.0, 2.0], [1.0]),
        ([1.0], [1.0, 2.0]),
    ])
    def test_similarity_raises_value_error(self, tanimoto_similarity, x, y):
        """
        Test that similarity raises ValueError for invalid inputs.
        """
        with pytest.raises(ValueError):
            tanimoto_similarity.similarity(x, y)

    @pytest.mark.parametrize("pairs", [
        ([],),
        ([([1.0, 2.0], [1.0])],),
    ])
    def test_similarities_raises_value_error(self, tanimoto_similarity, pairs):
        """
        Test that similarities raises ValueError for invalid input pairs.
        """
        with pytest.raises(ValueError):
            tanimoto_similarity.similarities(pairs)

# Configure logging for the test module
logger = logging.getLogger(__name__)