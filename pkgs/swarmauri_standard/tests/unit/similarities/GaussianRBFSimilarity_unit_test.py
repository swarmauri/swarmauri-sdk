import pytest
import numpy as np
from swarmauri_standard.similarities import GaussianRBFSimilarity
from swarmauri_standard.tests.unit.test_base import BaseTestCase


@pytest.mark.unit
class TestGaussianRBFSimilarity(BaseTestCase):
    """Unit tests for GaussianRBFSimilarity class implementation."""

    @pytest.fixture
    def gaussian_rbf_similarity(self):
        """Fixture to provide a GaussianRBFSimilarity instance."""
        return GaussianRBFSimilarity()

    @pytest.mark.unit
    def test_resource(self, gaussian_rbf_similarity):
        """Test the resource property."""
        assert gaussian_rbf_similarity.resource == "Similarity"

    @pytest.mark.unit
    def test_type(self, gaussian_rbf_similarity):
        """Test the type property."""
        assert gaussian_rbf_similarity.type == "GaussianRBFSimilarity"

    @pytest.mark.unit
    def test_serialization(self, gaussian_rbf_similarity):
        """Test serialization/deserialization process."""
        model_dump = gaussian_rbf_similarity.model_dump_json()
        model_id = gaussian_rbf_similarity.id
        assert gaussian_rbf_similarity.model_validate_json(model_dump) == model_id

    @pytest.mark.unit
    def test_similarity(self, gaussian_rbf_similarity):
        """Test similarity calculation between vectors."""
        # Test with identical vectors
        x = np.array([1, 2, 3])
        y = np.array([1, 2, 3])
        similarity = gaussian_rbf_similarity.similarity(x, y)
        assert similarity == 1.0

        # Test with different vectors
        x = np.array([1, 2, 3])
        y = np.array([4, 5, 6])
        similarity = gaussian_rbf_similarity.similarity(x, y)
        assert 0 <= similarity < 1

        # Test with zero vectors
        x = np.array([0, 0, 0])
        y = np.array([0, 0, 0])
        similarity = gaussian_rbf_similarity.similarity(x, y)
        assert similarity == 1.0

    @pytest.mark.unit
    def test_similarities(self, gaussian_rbf_similarity):
        """Test batch similarity calculation."""
        pairs = [
            (np.array([1, 2]), np.array([1, 2])),
            (np.array([3, 4]), np.array([5, 6])),
        ]
        results = gaussian_rbf_similarity.similarities(pairs)
        assert len(results) == 2
        assert all(0 <= res <= 1 for res in results)

    @pytest.mark.unit
    def test_dissimilarity(self, gaussian_rbf_similarity):
        """Test dissimilarity calculation between vectors."""
        x = np.array([1, 2, 3])
        y = np.array([4, 5, 6])
        dissimilarity = gaussian_rbf_similarity.dissimilarity(x, y)
        assert 0 <= dissimilarity < 1

    @pytest.mark.unit
    def test_dissimilarities(self, gaussian_rbf_similarity):
        """Test batch dissimilarity calculation."""
        pairs = [
            (np.array([1, 2]), np.array([1, 2])),
            (np.array([3, 4]), np.array([5, 6])),
        ]
        results = gaussian_rbf_similarity.dissimilarities(pairs)
        assert len(results) == 2
        assert all(0 <= res <= 1 for res in results)

    @pytest.mark.unit
    @pytest.mark.parametrize("invalid_gamma", [0, -1, -0.5])
    def test_invalid_gamma(self, invalid_gamma):
        """Test initialization with invalid gamma values."""
        with pytest.raises(ValueError):
            GaussianRBFSimilarity(gamma=invalid_gamma)

    @pytest.mark.unit
    def test_invalid_input(self, gaussian_rbf_similarity):
        """Test handling of invalid input types."""
        with pytest.raises(Exception):
            gaussian_rbf_similarity.similarity("invalid", "input")
