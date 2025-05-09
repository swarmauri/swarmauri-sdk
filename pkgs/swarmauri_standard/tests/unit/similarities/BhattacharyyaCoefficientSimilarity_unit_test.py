import pytest
import logging
from typing import Sequence, Tuple, Union
from swarmauri_standard.similarities.BhattacharyyaCoefficientSimilarity import BhattacharyyaCoefficientSimilarity

logger = logging.getLogger(__name__)

@pytest.mark.unit
class TestBhattacharyyaCoefficientSimilarity:
    """Unit tests for BhattacharyyaCoefficientSimilarity class."""
    
    @pytest.mark.unit
    def test_resource(self):
        """Test the resource property."""
        assert BhattacharyyaCoefficientSimilarity.resource == "SIMILARITY"

    @pytest.mark.unit
    def test_type(self):
        """Test the type property."""
        assert BhattacharyyaCoefficientSimilarity.type == "BhattacharyyaCoefficientSimilarity"

    @pytest.mark.unit
    def test_similarity_valid_distribution(self):
        """Test similarity calculation with valid distributions."""
        bhattacharyya = BhattacharyyaCoefficientSimilarity()
        
        x = [1.0, 0.0]
        y = [0.0, 1.0]
        
        # The Bhattacharyya coefficient for these distributions is 0.0
        similarity = bhattacharyya.similarity(x, y)
        assert 0.0 <= similarity <= 1.0

    @pytest.mark.unit
    def test_similarity_normalized_distributions(self):
        """Test similarity calculation with already normalized distributions."""
        bhattacharyya = BhattacharyyaCoefficientSimilarity()
        
        x = [0.5, 0.5]
        y = [0.5, 0.5]
        
        # The Bhattacharyya coefficient for these distributions is 1.0
        similarity = bhattacharyya.similarity(x, y)
        assert similarity == 1.0

    @pytest.mark.unit
    def test_similarity_unnormalized_distributions(self):
        """Test similarity calculation with unnormalized distributions."""
        bhattacharyya = BhattacharyyaCoefficientSimilarity()
        
        x = [2, 3]
        y = [1, 2]
        
        similarity = bhattacharyya.similarity(x, y)
        assert 0.0 <= similarity <= 1.0

    @pytest.mark.unit
    def test_similarities_multiple_pairs(self):
        """Test similarities calculation with multiple pairs."""
        bhattacharyya = BhattacharyyaCoefficientSimilarity()
        
        pairs = [
            ([1.0, 0.0], [0.0, 1.0]),
            ([0.5, 0.5], [0.5, 0.5]),
            ([2, 3], [1, 2])
        ]
        
        similarities = bhattacharyya.similarities(pairs)
        assert len(similarities) == 3
        assert all(0.0 <= s <= 1.0 for s in similarities)

    @pytest.mark.unit
    def test_similarity_empty_distribution(self):
        """Test similarity calculation with empty distributions."""
        bhattacharyya = BhattacharyyaCoefficientSimilarity()
        
        x = []
        y = []
        
        with pytest.raises(ValueError):
            bhattacharyya.similarity(x, y)

    @pytest.mark.unit
    def test_similarity_different_lengths(self):
        """Test similarity calculation with distributions of different lengths."""
        bhattacharyya = BhattacharyyaCoefficientSimilarity()
        
        x = [1.0]
        y = [1.0, 0.0]
        
        with pytest.raises(ValueError):
            bhattacharyya.similarity(x, y)

    @pytest.mark.unit
    def test_similarity_zero_sum(self):
        """Test similarity calculation with distributions that sum to zero."""
        bhattacharyya = BhattacharyyaCoefficientSimilarity()
        
        x = [0.0, 0.0]
        y = [0.0, 0.0]
        
        with pytest.raises(ValueError):
            bhattacharyya.similarity(x, y)

    @pytest.mark.unit
    @pytest.parametrize("x,y,expected", [
        ([1.0, 0.0], [0.0, 1.0], 0.0),
        ([0.5, 0.5], [0.5, 0.5], 1.0),
        ([2, 3], [1, 2], 0.816496580927726)
    ])
    def test_similarity_parameterized(self, x, y, expected):
        """Test similarity calculation with specific values."""
        bhattacharyya = BhattacharyyaCoefficientSimilarity()
        similarity = bhattacharyya.similarity(x, y)
        assert abs(similarity - expected) < 1e-9