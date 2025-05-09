import pytest
import math
from swarmauri_standard.similarities.HellingerAffinitySimilarity import HellingerAffinitySimilarity

@pytest.mark.unit
class TestHellingerAffinitySimilarity:
    """Unit tests for the HellingerAffinitySimilarity class."""

    def test_resource_type(self):
        """Test that the resource type is correctly set."""
        similarity = HellingerAffinitySimilarity()
        assert similarity.resource == "SIMILARITY"

    def test_similarity_method(self):
        """Test the similarity calculation method with valid input vectors."""
        similarity = HellingerAffinitySimilarity()
        
        # Test with identical vectors
        x = [0.5, 0.5]
        y = [0.5, 0.5]
        result = similarity.similarity(x, y)
        assert math.isclose(result, 1.0, rel_tol=1e-9, abs_tol=1e-9)

        # Test with different vectors
        x = [0.0, 1.0]
        y = [1.0, 0.0]
        result = similarity.similarity(x, y)
        assert math.isclose(result, 0.0, rel_tol=1e-9, abs_tol=1e-9)

    def test_similarity_validation(self):
        """Test that invalid input vectors raise ValueError."""
        similarity = HellingerAffinitySimilarity()
        
        # Test with negative values
        x = [0.5, -0.5]
        y = [0.5, 0.5]
        with pytest.raises(ValueError):
            similarity.similarity(x, y)

        # Test with vectors that don't sum to 1
        x = [0.6, 0.5]
        y = [0.5, 0.5]
        with pytest.raises(ValueError):
            similarity.similarity(x, y)

    @pytest.mark.parametrize("x,y,expected_similarity", [
        ([0.5, 0.5], [0.5, 0.5], 1.0),
        ([0.0, 1.0], [1.0, 0.0], 0.0),
        ([0.7071, 0.7071], [0.7071, 0.7071], 1.0),
        ([0.3, 0.7], [0.3, 0.7], 1.0),
        ([0.1, 0.9], [0.2, 0.8], 0.4472)
    ])
    def test_parameterized_similarity(self, x, y, expected_similarity):
        """Test the similarity method with parameterized input vectors."""
        similarity = HellingerAffinitySimilarity()
        result = similarity.similarity(x, y)
        assert math.isclose(result, expected_similarity, rel_tol=1e-9, abs_tol=1e-9)

@pytest.fixture
def similarity_fixture():
    """Fixture to provide a HellingerAffinitySimilarity instance."""
    return HellingerAffinitySimilarity()