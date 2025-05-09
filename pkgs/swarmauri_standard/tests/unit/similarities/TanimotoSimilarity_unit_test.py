import pytest
from swarmauri_standard.similarities.TanimotoSimilarity import TanimotoSimilarity
import numpy as np
import logging

@pytest.mark.unit
class TestTanimotoSimilarity:
    """Unit tests for TanimotoSimilarity class."""
    
    @pytest.fixture
    def tanimoto(self):
        """Fixture to provide a TanimotoSimilarity instance."""
        return TanimotoSimilarity()

    def test_similarity(self, tanimoto):
        """Test calculation of Tanimoto similarity between two vectors."""
        # Test vectors
        x = np.array([1, 2, 3])
        y = np.array([4, 5, 6])
        
        # Expected similarity calculation
        dot_product = np.dot(x, y)
        mag_x = np.dot(x, x)
        mag_y = np.dot(y, y)
        expected = dot_product / (mag_x + mag_y - dot_product)
        
        # Get actual similarity
        actual = tanimoto.similarity(x, y)
        
        # Assert the results are equal with some tolerance
        assert np.isclose(actual, expected, rtol=1e-9)

    def test_similarities(self, tanimoto):
        """Test calculation of similarities with multiple vectors."""
        x = np.array([1, 1])
        y1 = np.array([1, 1])
        y2 = np.array([0, 0])
        ys = [y1, y2]
        
        # Expected results
        expected = [1.0, 0.0]
        
        # Get actual results
        actual = tanimoto.similarities(x, ys)
        
        # Assert the results are equal
        assert np.allclose(actual, expected, rtol=1e-9)

    def test_dissimilarity(self, tanimoto):
        """Test calculation of dissimilarity between two vectors."""
        x = np.array([1, 2])
        y = np.array([3, 4])
        
        # Calculate similarity
        similarity = tanimoto.similarity(x, y)
        
        # Calculate dissimilarity
        expected = 1.0 - similarity
        
        # Get actual dissimilarity
        actual = tanimoto.dissimilarity(x, y)
        
        # Assert the results are equal
        assert np.isclose(actual, expected, rtol=1e-9)

    def test_dissimilarities(self, tanimoto):
        """Test calculation of dissimilarities with multiple vectors."""
        x = np.array([1, 1])
        y1 = np.array([1, 1])
        y2 = np.array([0, 0])
        ys = [y1, y2]
        
        # Expected results
        expected = [0.0, 1.0]
        
        # Get actual results
        actual = tanimoto.dissimilarities(x, ys)
        
        # Assert the results are equal
        assert np.allclose(actual, expected, rtol=1e-9)

    def test_check_boundedness(self, tanimoto):
        """Test if the similarity measure is bounded."""
        bounded = tanimoto.check_boundedness(np.array([1, 2]), np.array([3, 4]))
        assert bounded is True

    def test_check_reflexivity(self, tanimoto):
        """Test if the similarity measure is reflexive."""
        x = np.array([1, 2])
        reflexive = tanimoto.check_reflexivity(x)
        assert reflexive is True

    def test_check_symmetry(self, tanimoto):
        """Test if the similarity measure is symmetric."""
        x = np.array([1, 2])
        y = np.array([3, 4])
        symmetric = tanimoto.check_symmetry(x, y)
        assert symmetric is True

    def test_check_identity(self, tanimoto):
        """Test if identical vectors have maximum similarity."""
        x = np.array([1, 2])
        y = np.array([1, 2])
        identical = tanimoto.check_identity(x, y)
        assert identical is True

    def test_invalid_input(self, tanimoto):
        """Test handling of invalid input vectors."""
        x = "invalid"
        y = "invalid"
        with pytest.raises(TypeError):
            tanimoto.similarity(x, y)

    def test_zero_magnitude(self, tanimoto):
        """Test handling of zero magnitude vectors."""
        x = np.array([0, 0])
        y = np.array([1, 2])
        with pytest.raises(ValueError):
            tanimoto.similarity(x, y)