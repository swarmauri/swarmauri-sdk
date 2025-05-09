import pytest
from swarmauri_standard.swarmauri_standard.similarities.ExponentialDistanceSimilarity import ExponentialDistanceSimilarity
import logging

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestExponentialDistanceSimilarity:
    """
    Unit tests for ExponentialDistanceSimilarity class.

    This class provides unit tests for the ExponentialDistanceSimilarity implementation.
    It tests basic functionality, edge cases, and various input types.
    """
    
    def test_type_attribute(self):
        """
        Test that the type attribute is correctly set.
        """
        assert ExponentialDistanceSimilarity.type == "ExponentialDistanceSimilarity"

    def test_resource_attribute(self):
        """
        Test that the resource attribute is correctly set.
        """
        assert ExponentialDistanceSimilarity.resource == "Similarity"

    def test_init_with_parameters(self):
        """
        Test that the class initializes correctly with given parameters.
        """
        distance_fn = lambda x, y: 0  # Simple distance function for testing
        gamma = 2.5
        
        instance = ExponentialDistanceSimilarity(distance_fn, gamma)
        
        assert instance.distance_fn == distance_fn
        assert instance.gamma == gamma

    @pytest.mark.parametrize("x,y,expected_similarity", [
        (1, 2, 1.0 / (1.0 + (1.0 / 1.0))),
        ([1.0, 2.0], [3.0, 4.0], 1.0 / (1.0 + (5.0 / 1.0))),
        (1, 1, 1.0)  # Should return 1.0 when inputs are identical
    ])
    def test_similarity(self, x, y, expected_similarity):
        """
        Test the similarity calculation with various inputs.
        """
        instance = ExponentialDistanceSimilarity()
        
        similarity = instance.similarity(x, y)
        
        # Using approximate equality since floating point operations can have precision issues
        assert abs(similarity - expected_similarity) < 1e-9

    def test_similarity_invalid_input(self):
        """
        Test that similarity raises ValueError for invalid input types.
        """
        instance = ExponentialDistanceSimilarity()
        
        with pytest.raises(ValueError):
            instance.similarity("invalid_type", "invalid_type")

    def test_dissimilarity(self):
        """
        Test the dissimilarity calculation.
        """
        instance = ExponentialDistanceSimilarity()
        
        similarity = instance.similarity(1, 2)
        dissimilarity = instance.dissimilarity(1, 2)
        
        assert dissimilarity == 1.0 - similarity

    def test_check_boundedness(self):
        """
        Test that check_boundedness returns True.
        """
        instance = ExponentialDistanceSimilarity()
        
        assert instance.check_boundedness(1, 2)

    def test_check_reflexivity(self):
        """
        Test reflexivity with various input types.
        """
        instance = ExponentialDistanceSimilarity()
        
        # Test with numbers
        assert instance.check_reflexivity(1)
        
        # Test with strings
        assert instance.check_reflexivity("test")
        
        # Test with vectors
        assert instance.check_reflexivity([1.0, 2.0])

    def test_check_symmetry(self):
        """
        Test symmetry between different input pairs.
        """
        instance = ExponentialDistanceSimilarity()
        
        # Test with numbers
        assert instance.check_symmetry(1, 2)
        
        # Test with vectors
        assert instance.check_symmetry([1.0, 2.0], [3.0, 4.0])

    def test_check_identity(self):
        """
        Test identity check with identical and different inputs.
        """
        instance = ExponentialDistanceSimilarity()
        
        # Test with identical inputs
        assert instance.check_identity(1, 1)
        
        # Test with different inputs
        assert not instance.check_identity(1, 2)