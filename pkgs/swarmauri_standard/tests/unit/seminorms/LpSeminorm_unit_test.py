import pytest
import logging
from swarmauri_standard.seminorms.LpSeminorm import LpSeminorm

@pytest.mark.unit
class TestLpSeminorm:
    """Unit tests for the LpSeminorm class."""
    
    def test_init_valid(self):
        """Test valid initialization of LpSeminorm."""
        # Valid p values
        p_values = [1.0, 2.0, float('inf')]
        
        for p in p_values:
            lp = LpSeminorm(p)
            assert lp.p == p
            assert isinstance(lp, SeminormBase)

    def test_init_invalid(self):
        """Test invalid initialization of LpSeminorm."""
        # Invalid p values
        p_values = [-1.0, 0.0, -2.0]
        
        for p in p_values:
            with pytest.raises(ValueError):
                LpSeminorm(p)

    @pytest.mark.parametrize("input,expected", [
        ([1.0, 2.0], 1.0),
        ([3.0, 4.0], (3**2 + 4**2)**0.5),
        ("5.0", 5.0),
        ([], 0.0),
        ([0.0, 0.0], 0.0)
    ])
    def test_compute_list(self, input, expected):
        """Test compute method with list input."""
        lp = LpSeminorm(1.0 if len(input) < 2 else 2.0)
        result = lp.compute(input)
        assert result == expected

    def test_compute_str(self):
        """Test compute method with string input."""
        lp = LpSeminorm(1.0)
        result = lp.compute("5.0")
        assert result == 5.0

    def test_compute_callable(self):
        """Test compute method with callable input."""
        lp = LpSeminorm(1.0)
        result = lp.compute(lambda: 5.0)
        assert result == 0.0

    def test_triangle_inequality_vector(self):
        """Test triangle inequality with vector input."""
        v1 = [1.0, 2.0]
        v2 = [2.0, 3.0]
        lp = LpSeminorm(2.0)
        
        seminorm_v1 = lp.compute(v1)
        seminorm_v2 = lp.compute(v2)
        seminorm_v1_plus_v2 = lp.compute([3.0, 5.0])
        
        assert seminorm_v1_plus_v2 <= seminorm_v1 + seminorm_v2

    def test_triangle_inequality_matrix(self):
        """Test triangle inequality with matrix input."""
        m1 = [[1.0, 2.0], [3.0, 4.0]]
        m2 = [[2.0, 3.0], [4.0, 5.0]]
        lp = LpSeminorm(2.0)
        
        seminorm_m1 = lp.compute(m1)
        seminorm_m2 = lp.compute(m2)
        seminorm_m1_plus_m2 = lp.compute([[3.0, 5.0], [7.0, 9.0]])
        
        assert seminorm_m1_plus_m2 <= seminorm_m1 + seminorm_m2

    def test_scalar_homogeneity_vector(self):
        """Test scalar homogeneity with vector input."""
        v = [1.0, 2.0]
        scalar = 2.0
        lp = LpSeminorm(2.0)
        
        seminorm_v = lp.compute(v)
        scaled_v = [2.0, 4.0]
        seminorm_scaled_v = lp.compute(scaled_v)
        
        assert seminorm_scaled_v == scalar * seminorm_v

    def test_scalar_homogeneity_matrix(self):
        """Test scalar homogeneity with matrix input."""
        m = [[1.0, 2.0], [3.0, 4.0]]
        scalar = 2.0
        lp = LpSeminorm(2.0)
        
        seminorm_m = lp.compute(m)
        scaled_m = [[2.0, 4.0], [6.0, 8.0]]
        seminorm_scaled_m = lp.compute(scaled_m)
        
        assert seminorm_scaled_m == scalar * seminorm_m

    def test_str_repr(self):
        """Test string representation of LpSeminorm."""
        lp = LpSeminorm(2.0)
        assert str(lp) == f"LpSeminorm(p={lp.p})"

    def test_repr(self):
        """Test official string representation of LpSeminorm."""
        lp = LpSeminorm(2.0)
        assert lp.__repr__() == lp.__str__()