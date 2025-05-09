import pytest
import logging
from unittest.mock import MagicMock
from swarmauri_standard.seminorms.PartialSumSeminorm import PartialSumSeminorm

@pytest.mark.unit
class TestPartialSumSeminorm:
    """Unit tests for the PartialSumSeminorm class."""
    
    def test_constructor(self):
        """Test the initialization of PartialSumSeminorm."""
        # Test with default end_index (None)
        seminorm = PartialSumSeminorm(start_index=2)
        assert seminorm._start_index == 2
        assert seminorm._end_index is None
        
        # Test with specified end_index
        seminorm = PartialSumSeminorm(start_index=1, end_index=5)
        assert seminorm._start_index == 1
        assert seminorm._end_index == 5

    def test_compute(self):
        """Test the compute method with various input types and conditions."""
        # Test with list input
        seminorm = PartialSumSeminorm(start_index=1, end_index=3)
        vector = [1, 2, 3, 4, 5]
        result = seminorm.compute(vector)
        assert result == 2 + 3 + 4  # Sum of indices 1 to 3 (exclusive)
        
        # Test with tuple input
        vector = (1, 2, 3, 4)
        result = seminorm.compute(vector)
        assert result == 2 + 3 + 4
        
        # Test with IVector mock
        mock_vector = MagicMock(spec=IVector)
        mock_vector.data.return_value = [1, 2, 3, 4, 5]
        result = seminorm.compute(mock_vector)
        assert result == 2 + 3 + 4 + 5  # Since end_index is None, sums to end
        
        # Test with IMatrix mock
        mock_matrix = MagicMock(spec=IMatrix)
        mock_matrix.data.return_value = [[1, 2, 3], [4, 5, 6]]
        seminorm = PartialSumSeminorm(start_index=0, end_index=2)
        result = seminorm.compute(mock_matrix)
        assert result == 1 + 2  # First row, first two elements
        
        # Test with end_index at vector end
        seminorm = PartialSumSeminorm(start_index=2, end_index=None)
        vector = [1, 2, 3, 4]
        result = seminorm.compute(vector)
        assert result == 3 + 4
        
        # Test with invalid start_index
        seminorm = PartialSumSeminorm(start_index=5)
        vector = [1, 2, 3]
        with pytest.raises(ValueError):
            seminorm.compute(vector)
            
        # Test with invalid end_index
        seminorm = PartialSumSeminorm(start_index=1, end_index=5)
        vector = [1, 2, 3]
        with pytest.raises(ValueError):
            seminorm.compute(vector)

    def test_check_triangle_inequality(self):
        """Test the triangle inequality check."""
        seminorm = PartialSumSeminorm(start_index=0, end_index=None)
        
        # Test with vectors where triangle inequality holds
        a = [1, 2, 3]
        b = [4, 5, 6]
        a_plus_b = [5, 7, 9]
        
        seminorm_ab = seminorm.compute(a_plus_b)
        seminorm_a = seminorm.compute(a)
        seminorm_b = seminorm.compute(b)
        
        assert seminorm.check_triangle_inequality(a, b)
        assert seminorm_ab <= seminorm_a + seminorm_b
        
        # Test with IVector mocks
        mock_a = MagicMock(spec=IVector)
        mock_a.data.return_value = [1, 2, 3]
        mock_b = MagicMock(spec=IVector)
        mock_b.data.return_value = [4, 5, 6]
        
        assert seminorm.check_triangle_inequality(mock_a, mock_b)

    def test_check_scalar_homogeneity(self):
        """Test the scalar homogeneity check."""
        seminorm = PartialSumSeminorm(start_index=0, end_index=None)
        vector = [1, 2, 3]
        
        # Test with positive scalar
        scalar = 2
        scaled_vector = [2, 4, 6]
        seminorm_scaled = seminorm.compute(scaled_vector)
        seminorm_original = seminorm.compute(vector)
        
        assert seminorm.check_scalar_homogeneity(vector, scalar)
        assert seminorm_scaled == abs(scalar) * seminorm_original
        
        # Test with negative scalar
        scalar = -2
        scaled_vector = [-2, -4, -6]
        seminorm_scaled = seminorm.compute(scaled_vector)
        assert seminorm.check_scalar_homogeneity(vector, scalar)
        assert seminorm_scaled == abs(scalar) * seminorm_original
        
        # Test with IVector mock
        mock_vector = MagicMock(spec=IVector)
        mock_vector.data.return_value = [1, 2, 3]
        assert seminorm.check_scalar_homogeneity(mock_vector, 2)

    def test_string_representation(self):
        """Test string and representation methods."""
        seminorm = PartialSumSeminorm(start_index=1, end_index=4)
        assert str(seminorm) == "PartialSumSeminorm(start_index=1, end_index=4)"
        assert repr(seminorm) == "PartialSumSeminorm(start_index=1, end_index=4)"

    def test_logging(self, caplog):
        """Test logging in the compute method."""
        caplog.set_level(logging.DEBUG)
        seminorm = PartialSumSeminorm(start_index=0, end_index=2)
        vector = [1, 2, 3]
        seminorm.compute(vector)
        
        assert "Computing partial sum seminorm for input of type list" in caplog.text