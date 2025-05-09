import pytest
import logging
from swarmauri_standard.swarmauri_standard.norms.L2EuclideanNorm import L2EuclideanNorm

logger = logging.getLogger(__name__)

@pytest.mark.unit
class TestL2EuclideanNorm:
    """Unit tests for L2EuclideanNorm class implementation."""
    
    @pytest.fixture
    def setup_l2_norm(self):
        """Fixture to provide a L2EuclideanNorm instance for testing."""
        return L2EuclideanNorm()

    def test_resource_property(self, setup_l2_norm):
        """Test the resource property of the L2EuclideanNorm class."""
        assert setup_l2_norm.resource == "norm"
        logger.info("Resource property test completed successfully")

    def test_type_property(self, setup_l2_norm):
        """Test the type property of the L2EuclideanNorm class."""
        assert setup_l2_norm.type == "L2EuclideanNorm"
        logger.info("Type property test completed successfully")

    @pytest.mark.parametrize("input_vector,expected_norm", [
        ([3, 4], 5.0),
        ([0, 0], 0.0),
        ("1 2 3", (1**2 + 2**2 + 3**2)**0.5),
        (lambda: [5, 12], 13.0)
    ])
    def test_compute_method(self, setup_l2_norm, input_vector, expected_norm):
        """Test the compute method with various input types and expected norms."""
        computed_norm = setup_l2_norm.compute(input_vector)
        assert abs(computed_norm - expected_norm) < 1e-9
        logger.info(f"Compute method test with input {input_vector} completed successfully")

    def test_compute_method_invalid_input(self, setup_l2_norm):
        """Test the compute method with invalid input."""
        with pytest.raises(ValueError):
            setup_l2_norm.compute("invalid_input")
        logger.info("Invalid input test for compute method completed successfully")

    def test_check_non_negativity(self, setup_l2_norm):
        """Test the non-negativity property of the L2 norm."""
        # Test with positive vector
        assert setup_l2_norm.compute([1, 2]) >= 0
        
        # Test with negative vector
        assert setup_l2_norm.compute([-1, -2]) >= 0
        
        # Test with zero vector
        assert setup_l2_norm.compute([0, 0]) == 0
        
        logger.info("Non-negativity property test completed successfully")

    def test_check_triangle_inequality(self, setup_l2_norm):
        """Test the triangle inequality property of the L2 norm."""
        x = [1, 2]
        y = [2, 3]
        
        norm_x = setup_l2_norm.compute(x)
        norm_y = setup_l2_norm.compute(y)
        norm_sum = setup_l2_norm.compute([3, 5])
        
        assert norm_sum <= norm_x + norm_y
        logger.info("Triangle inequality property test completed successfully")

    @pytest.mark.parametrize("scale_factor", [2, -1, 0.5])
    def test_check_absolute_homogeneity(self, setup_l2_norm, scale_factor):
        """Test the absolute homogeneity property of the L2 norm."""
        x = [1, 2]
        scaled_x = [scale_factor * num for num in x]
        
        scaled_norm = setup_l2_norm.compute(scaled_x)
        original_norm = setup_l2_norm.compute(x)
        
        assert abs(scaled_norm - abs(scale_factor) * original_norm) < 1e-9
        logger.info(f"Absolute homogeneity property test with scale factor {scale_factor} completed successfully")

    def test_check_definiteness(self, setup_l2_norm):
        """Test the definiteness property of the L2 norm."""
        # Test with zero vector
        assert setup_l2_norm.compute([0, 0]) == 0
        
        # Test with non-zero vector
        assert setup_l2_norm.compute([1, 1]) > 0
        
        logger.info("Definiteness property test completed successfully")

    def test_model_serialization(self, setup_l2_norm):
        """Test model serialization and validation."""
        model_json = setup_l2_norm.model_dump_json()
        assert setup_l2_norm.model_validate_json(model_json) == setup_l2_norm.id
        logger.info("Model serialization and validation test completed successfully")