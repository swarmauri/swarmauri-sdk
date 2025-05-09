import pytest
import logging
from unittest.mock import patch
from swarmauri_standard.similarities.TriangleCosineSimilarity import TriangleCosineSimilarity

@pytest.mark.unit
class TestTriangleCosineSimilarity:
    """Unit tests for TriangleCosineSimilarity class."""
    
    @pytest.fixture
    def triangle_cosine_similarity(self):
        """Fixture providing an instance of TriangleCosineSimilarity."""
        return TriangleCosineSimilarity()

    def test_resource(self):
        """Test the resource attribute."""
        assert TriangleCosineSimilarity.resource == "Similarity"

    def test_type(self):
        """Test the type attribute."""
        assert TriangleCosineSimilarity.type == "TriangleCosineSimilarity"

    def test_serialization(self, triangle_cosine_similarity):
        """Test model serialization and validation."""
        model_json = triangle_cosine_similarity.model_dump_json()
        assert TriangleCosineSimilarity.model_validate_json(model_json) == TriangleCosineSimilarity.id

    def test_similarity_identical_vectors(self, triangle_cosine_similarity):
        """Test similarity calculation with identical vectors."""
        x = [1.0, 2.0, 3.0]
        y = [1.0, 2.0, 3.0]
        similarity = triangle_cosine_similarity.similarity(x, y)
        assert pytest.approx(similarity, 1.0)

    def test_similarity_opposite_vectors(self, triangle_cosine_similarity):
        """Test similarity calculation with opposite vectors."""
        x = [1.0, 2.0, 3.0]
        y = [-1.0, -2.0, -3.0]
        similarity = triangle_cosine_similarity.similarity(x, y)
        assert pytest.approx(similarity, -1.0)

    def test_similarity_non_zero_vectors(self, triangle_cosine_similarity):
        """Test similarity calculation with non-zero vectors."""
        x = [1.0, 0.0]
        y = [0.0, 1.0]
        similarity = triangle_cosine_similarity.similarity(x, y)
        assert pytest.approx(similarity, 0.0)

    def test_similarity_zero_vector_raises_error(self, triangle_cosine_similarity):
        """Test that similarity raises ValueError for zero vectors."""
        x = [0.0, 0.0]
        y = [1.0, 2.0]
        with pytest.raises(ValueError):
            triangle_cosine_similarity.similarity(x, y)

    def test_dissimilarity(self, triangle_cosine_similarity):
        """Test dissimilarity calculation."""
        x = [1.0, 2.0, 3.0]
        y = [1.0, 2.0, 3.0]
        dissimilarity = triangle_cosine_similarity.dissimilarity(x, y)
        assert pytest.approx(dissimilarity, 0.0)

    def test_dissimilarity_opposite_vectors(self, triangle_cosine_similarity):
        """Test dissimilarity calculation with opposite vectors."""
        x = [1.0, 2.0, 3.0]
        y = [-1.0, -2.0, -3.0]
        dissimilarity = triangle_cosine_similarity.dissimilarity(x, y)
        assert pytest.approx(dissimilarity, 2.0)

    def test_check_boundedness(self, triangle_cosine_similarity):
        """Test check_boundedness method."""
        assert triangle_cosine_similarity.check_boundedness()

    def test_check_reflexivity(self, triangle_cosine_similarity):
        """Test check_reflexivity method."""
        assert triangle_cosine_similarity.check_reflexivity()

    def test_check_symmetry(self, triangle_cosine_similarity):
        """Test check_symmetry method."""
        assert triangle_cosine_similarity.check_symmetry()

    def test_check_identity(self, triangle_cosine_similarity):
        """Test check_identity method."""
        assert not triangle_cosine_similarity.check_identity()

    @patch('logging.debug')
    def test_logging_similarity(self, mock_logging, triangle_cosine_similarity):
        """Test logging in similarity method."""
        x = [1.0, 2.0, 3.0]
        y = [1.0, 2.0, 3.0]
        triangle_cosine_similarity.similarity(x, y)
        mock_logging.assert_called_with(f"Calculating cosine similarity between vectors {x} and {y}")

    @patch('logging.debug')
    def test_logging_dissimilarity(self, mock_logging, triangle_cosine_similarity):
        """Test logging in dissimilarity method."""
        x = [1.0, 2.0, 3.0]
        y = [1.0, 2.0, 3.0]
        triangle_cosine_similarity.dissimilarity(x, y)
        mock_logging.assert_called_with(f"Calculating dissimilarity between vectors {x} and {y}")