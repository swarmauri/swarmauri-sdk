import pytest
import logging
from swarmauri_standard.swarmauri_standard.seminorms.TraceSeminorm import TraceSeminorm
import numpy as np

logger = logging.getLogger(__name__)

@pytest.mark.unit
class TestTraceSeminorm:
    """Unit tests for the TraceSeminorm class."""
    
    def test_compute(self):
        """Test the compute method with various inputs."""
        # Test with a 2x2 matrix
        matrix = np.array([[1, 2], [3, 4]])
        seminorm = TraceSeminorm().compute(matrix)
        assert seminorm == 10.0
        
        # Test with a 3x3 matrix
        matrix = np.array([[1, 0, 0], [0, 2, 0], [0, 0, 3]])
        seminorm = TraceSeminorm().compute(matrix)
        assert seminorm == 6.0
        
        # Test with a callable that returns a matrix
        def matrix_callable():
            return np.array([[5, 6], [7, 8]])
        seminorm = TraceSeminorm().compute(matrix_callable)
        assert seminorm == 21.0
        
        # Test with invalid input
        with pytest.raises(ValueError):
            TraceSeminorm().compute("invalid input")

    def test_check_triangle_inequality(self):
        """Test the triangle inequality check."""
        # Create test matrices
        matrix_a = np.array([[1, 2], [3, 4]])
        matrix_b = np.array([[5, 6], [7, 8]])
        
        # Compute seminorms
        seminorm = TraceSeminorm()
        seminorm_a = seminorm.compute(matrix_a)
        seminorm_b = seminorm.compute(matrix_b)
        seminorm_ab = seminorm.compute(matrix_a + matrix_b)
        
        # Check triangle inequality
        holds = seminorm.check_triangle_inequality(matrix_a, matrix_b)
        assert holds
        assert seminorm_ab <= (seminorm_a + seminorm_b)

    def test_check_scalar_homogeneity(self):
        """Test scalar homogeneity."""
        # Create test matrix
        matrix = np.array([[1, 2], [3, 4]])
        scalar = 2.5
        
        # Compute original seminorm
        seminorm = TraceSeminorm()
        original_seminorm = seminorm.compute(matrix)
        
        # Compute scaled matrix and its seminorm
        scaled_matrix = scalar * matrix
        scaled_seminorm = seminorm.compute(scaled_matrix)
        
        # Check homogeneity
        holds = seminorm.check_scalar_homogeneity(matrix, scalar)
        assert holds
        assert np.isclose(scaled_seminorm, scalar * original_seminorm)

    def test_logging(self, caplog):
        """Test if logging messages are generated."""
        with caplog.at_level(logging.DEBUG):
            seminorm = TraceSeminorm()
            seminorm.compute(np.array([[1, 2], [3, 4]]))
            
            assert "Computing trace seminorm" in caplog.text
            assert "Computed trace seminorm" in caplog.text