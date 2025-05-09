import pytest
from swarmauri_standard.norms.GeneralLpNorm import GeneralLpNorm
import numpy as np
import logging

@pytest.mark.unit
class TestGeneralLpNorm:
    """Unit tests for GeneralLpNorm class."""
    
    @pytest.fixture
    def general_lpnorm(self):
        """Fixture to provide a GeneralLpNorm instance with default p=2.0."""
        return GeneralLpNorm(p=2.0)
    
    def test_resource(self, general_lpnorm):
        """Test resource type."""
        assert general_lpnorm.resource == "Norm"
    
    def test_type(self, general_lpnorm):
        """Test type attribute."""
        assert general_lpnorm.type == "GeneralLpNorm"
    
    def test_serialization(self, general_lpnorm):
        """Test model serialization and validation."""
        model_json = general_lpnorm.model_dump_json()
        assert GeneralLpNorm.model_validate_json(model_json) == model_json
    
    @pytest.mark.parametrize("p", [0.5, -1.0, 1.0])
    def test_invalid_p_values(self, p):
        """Test if invalid p values raise ValueError."""
        with pytest.raises(ValueError):
            GeneralLpNorm(p=p)
    
    @pytest.mark.parametrize("x,expected_output", [
        ([1, 2, 3], 3.7417),
        (np.array([4, 5, 6]), 8.246)
    ])
    def test_compute(self, x, expected_output):
        """Test compute method with different inputs."""
        generallpnorm = GeneralLpNorm(p=2.0)
        result = generallpnorm.compute(x)
        assert isinstance(result, float)
        assert round(result, 4) == round(expected_output, 4)
    
    def test_compute_edge_case(self):
        """Test compute with all zeros."""
        generallpnorm = GeneralLpNorm(p=2.0)
        result = generallpnorm.compute([0, 0, 0])
        assert result == 0.0
    
    def test_check_non_negativity(self, general_lpnorm):
        """Test non-negativity check."""
        # Test with positive values
        is_non_negative = general_lpnorm.check_non_negativity([1, 2, 3])
        assert is_non_negative is True
        
        # Test with zeros
        is_non_negative = general_lpnorm.check_non_negativity([0, 0, 0])
        assert is_non_negative is True
    
    def test_check_triangle_inequality(self, general_lpnorm):
        """Test triangle inequality check."""
        x = [1, 2, 3]
        y = [4, 5, 6]
        is_triangle_valid = general_lpnorm.check_triangle_inequality(x, y)
        assert is_triangle_valid is True
    
    def test_check_absolute_homogeneity(self, general_lpnorm):
        """Test absolute homogeneity check."""
        x = [1, 2, 3]
        scalar = 2.0
        is_homogeneous = general_lpnorm.check_absolute_homogeneity(x, scalar)
        assert is_homogeneous is True

# Initialize logger
logger = logging.getLogger(__name__)