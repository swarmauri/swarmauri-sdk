import pytest
import logging
from swarmauri_standard.swarmauri_standard.seminorms.PartialSumSeminorm import PartialSumSeminorm

@pytest.mark.unit
class TestPartialSumSeminorm:
    """Unit test class for PartialSumSeminorm class."""
    
    def test_init(self):
        """Test initialization with different start and end values."""
        # Test with default start=0 and end=None
        p = PartialSumSeminorm()
        assert p.start == 0
        assert p.end is None
        
        # Test with custom start and end
        p = PartialSumSeminorm(start=5, end=10)
        assert p.start == 5
        assert p.end == 10
        
        # Test with start=0 and end=0
        p = PartialSumSeminorm(start=0, end=0)
        assert p.start == 0
        assert p.end == 0

    def test_compute(self):
        """Test compute method with various inputs."""
        # Test with default start and end
        p = PartialSumSeminorm()
        input = [1, 2, 3, 4]
        result = p.compute(input)
        assert result == 10
        
        # Test with custom start
        p = PartialSumSeminorm(start=2)
        result = p.compute(input)
        assert result == 3 + 4 == 7
        
        # Test with custom end
        p = PartialSumSeminorm(end=3)
        result = p.compute(input)
        assert result == 1 + 2 + 3 == 6
        
        # Test with start=0 and end equal to length of input
        p = PartialSumSeminorm(start=0, end=len(input))
        result = p.compute(input)
        assert result == 10

    def test_check_triangle_inequality(self):
        """Test triangle inequality check method."""
        p = PartialSumSeminorm()
        a = [1, 2]
        b = [3, 4]
        
        # Compute individual seminorms
        seminorm_a = p.compute(a)
        seminorm_b = p.compute(b)
        seminorm_ab = p.compute([1+3, 2+4])
        
        # Check inequality
        result = p.check_triangle_inequality(a, b)
        assert result == True
        assert seminorm_ab <= seminorm_a + seminorm_b

    def test_check_scalar_homogeneity(self):
        """Test scalar homogeneity check method."""
        p = PartialSumSeminorm()
        a = [1, 2]
        scalar = 2.0
        
        # Compute original and scaled seminorms
        original = p.compute(a)
        scaled = p.compute([x * scalar for x in a])
        
        # Check homogeneity
        result = p.check_scalar_homogeneity(a, scalar)
        assert result == True
        assert scaled == original * scalar
        
        # Test with scalar=0
        scalar = 0.0
        result = p.check_scalar_homogeneity(a, scalar)
        assert result == True
        assert p.compute([x * scalar for x in a]) == 0.0

    def test_edge_cases(self):
        """Test edge cases for compute method."""
        p = PartialSumSeminorm()
        
        # Test with empty list
        input = []
        with pytest.raises(ValueError):
            p.compute(input)
            
        # Test with single element list
        input = [5]
        result = p.compute(input)
        assert result == 5
        
        # Test with start index beyond input length
        input = [1, 2]
        p = PartialSumSeminorm(start=3)
        with pytest.raises(ValueError):
            p.compute(input)