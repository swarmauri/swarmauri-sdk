"""Unit tests for the TraceSeminorm class."""

import pytest
import numpy as np
import logging

from swarmauri_standard.swarmauri_standard.TraceSeminorm import TraceSeminorm

@pytest.mark.unit
class TestTraceSeminorm:
    """Unit tests for the TraceSeminorm class."""
    
    @pytest.fixture
    def test_matrices(self):
        """Fixture providing test matrices."""
        # Matrix with positive trace
        matrix_positive = np.array([[2, 0], [0, 3]])
        # Matrix with negative trace
        matrix_negative = np.array([[-2, 0], [0, -3]])
        # Matrix with mixed trace
        matrix_mixed = np.array([[1, 0], [0, -2]])
        # Zero matrix
        matrix_zero = np.zeros((2, 2))
        # Non-square matrix
        matrix_non_square = np.array([[1, 2, 3], [4, 5, 6]])
        
        return {
            "positive": matrix_positive,
            "negative": matrix_negative,
            "mixed": matrix_mixed,
            "zero": matrix_zero,
            "non_square": matrix_non_square
        }
    
    @pytest.fixture
    def test_scalars(self):
        """Fixture providing test scalar values."""
        return {
            "positive": 2.0,
            "negative": -3.5,
            "zero": 0.0
        }
    
    def test_class_attributes(self):
        """Test that class attributes are correctly set."""
        assert TraceSeminorm.type == "TraceSeminorm"
        assert TraceSeminorm.resource == "SEMINORM"
    
    @pytest.mark.parametrize("matrix_name", ["positive", "negative", "mixed", "zero"])
    def test_compute(self, test_matrices, matrix_name):
        """Test the compute method with various matrices."""
        matrix = test_matrices[matrix_name]
        seminorm = TraceSeminorm()
        
        # Compute trace seminorm
        trace = np.trace(matrix)
        expected = abs(float(trace))
        
        result = seminorm.compute(matrix)
        
        assert result == expected
        assert isinstance(result, float)
        
    def test_compute_invalid_input(self, test_matrices):
        """Test compute with invalid input types."""
        seminorm = TraceSeminorm()
        
        # Test with None input
        with pytest.raises(ValueError):
            seminorm.compute(None)
            
        # Test with non-matrix input
        with pytest.raises(ValueError):
            seminorm.compute("invalid")
    
    @pytest.mark.parametrize("matrix_name", ["positive", "negative", "mixed", "zero"])
    def test_check_triangle_inequality(self, test_matrices, matrix_name):
        """Test the triangle inequality check."""
        matrix_a = test_matrices[matrix_name]
        matrix_b = test_matrices[matrix_name]
        seminorm = TraceSeminorm()
        
        norm_a = seminorm.compute(matrix_a)
        norm_b = seminorm.compute(matrix_b)
        norm_ab = seminorm.compute(matrix_a + matrix_b)
        
        assert seminorm.check_triangle_inequality(matrix_a, matrix_b) == (norm_ab <= (norm_a + norm_b))
    
    @pytest.mark.parametrize("matrix_name", ["positive", "negative", "mixed", "zero"])
    def test_check_scalar_homogeneity(self, test_matrices, test_scalars, matrix_name):
        """Test scalar homogeneity."""
        matrix = test_matrices[matrix_name]
        scalar = next(iter(test_scalars.values()))  # Get first scalar value
        seminorm = TraceSeminorm()
        
        norm_a = seminorm.compute(matrix)
        norm_scaled = seminorm.compute(scalar * matrix)
        
        assert seminorm.check_scalar_homogeneity(matrix, scalar) == (norm_scaled == abs(scalar) * norm_a)