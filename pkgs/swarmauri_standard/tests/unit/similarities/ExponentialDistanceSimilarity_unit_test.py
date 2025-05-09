import pytest
from swarmauri_standard.swarmauri_standard.ExponentialDistanceSimilarity import ExponentialDistanceSimilarity
import math
import logging

@pytest.mark.unit
class TestExponentialDistanceSimilarity:
    """Unit tests for ExponentialDistanceSimilarity class."""
    
    @pytest.fixture
    def exponential_distance_similarity(self):
        """Fixture providing a default ExponentialDistanceSimilarity instance."""
        def distance_func(x: float, y: float) -> float:
            return abs(x - y)
        return ExponentialDistanceSimilarity(distance_func)
    
    def test_constructor(self):
        """Test that the constructor initializes the object correctly."""
        def distance_func(x: float, y: float) -> float:
            return abs(x - y)
        eds = ExponentialDistanceSimilarity(distance_func)
        
        # Test if the distance function was set correctly
        assert eds.distance_function is not None
        # Test if the logger was initialized
        assert eds.logger is not None
    
    def test_similarity(self, exponential_distance_similarity):
        """Test the similarity calculation."""
        # Test with identical inputs
        similarity = exponential_distance_similarity.similarity(5, 5)
        assert similarity == 1.0
        
        # Test with different inputs
        similarity = exponential_distance_similarity.similarity(5, 10)
        assert similarity == math.exp(-5)
        
        # Test with negative inputs
        similarity = exponential_distance_similarity.similarity(-5, 5)
        assert similarity == math.exp(-10)
        
        # Test with non-integer inputs
        similarity = exponential_distance_similarity.similarity(5.5, 6.5)
        assert similarity == math.exp(-1.0)
        
    def test_similarities(self, exponential_distance_similarity):
        """Test the similarities method with multiple pairs."""
        pairs = [(1, 2), (3, 4), (5, 5)]
        results = exponential_distance_similarity.similarities(pairs)
        
        # Verify the results match expected values
        expected = [math.exp(-1), math.exp(-1), 1.0]
        assert results == expected
    
    def test_dissimilarity(self, exponential_distance_similarity):
        """Test the dissimilarity calculation."""
        # Test with identical inputs
        dissimilarity = exponential_distance_similarity.dissimilarity(5, 5)
        assert dissimilarity == 0.0
        
        # Test with different inputs
        dissimilarity = exponential_distance_similarity.dissimilarity(5, 10)
        assert dissimilarity == 1.0 - math.exp(-5)
        
        # Test with negative inputs
        dissimilarity = exponential_distance_similarity.dissimilarity(-5, 5)
        assert dissimilarity == 1.0 - math.exp(-10)
        
        # Test with non-integer inputs
        dissimilarity = exponential_distance_similarity.dissimilarity(5.5, 6.5)
        assert dissimilarity == 1.0 - math.exp(-1.0)
    
    def test_dissimilarities(self, exponential_distance_similarity):
        """Test the dissimilarities method with multiple pairs."""
        pairs = [(1, 2), (3, 4), (5, 5)]
        results = exponential_distance_similarity.dissimilarities(pairs)
        
        # Verify the results match expected values
        expected = [1.0 - math.exp(-1), 1.0 - math.exp(-1), 0.0]
        assert results == expected
    
    def test_model_serialization(self, exponential_distance_similarity):
        """Test that model serialization works correctly."""
        # Dump the model to JSON
        model_json = exponential_distance_similarity.model_dump_json()
        # Validate the JSON
        assert exponential_distance_similarity.model_validate_json(model_json)
    
    def test_logging(self, exponential_distance_similarity, caplog):
        """Test that logging messages are generated correctly."""
        # Test similarity calculation
        exponential_distance_similarity.similarity(5, 10)
        # Verify debug message was logged
        assert "Calculating similarity between 5 and 10" in caplog.text
        assert "Similarity: " in caplog.text
        
        # Test dissimilarity calculation
        exponential_distance_similarity.dissimilarity(5, 10)
        # Verify debug message was logged
        assert "Calculating dissimilarity between 5 and 10" in caplog.text
        assert "Dissimilarity: " in caplog.text
    
    def test_error_handling(self):
        """Test that invalid inputs raise appropriate errors."""
        # Test None distance function
        with pytest.raises(ValueError):
            ExponentialDistanceSimilarity(None)
        
        # Test non-callable distance function
        with pytest.raises(TypeError):
            ExponentialDistanceSimilarity("not a function")
        
        # Test invalid input types
        eds = ExponentialDistanceSimilarity(lambda x, y: abs(x - y))
        with pytest.raises(TypeError):
            eds.similarity("string", 5)