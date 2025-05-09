import pytest
import numpy as np
from swarmauri_standard.swarmauri_standard.seminorms.LpSeminorm import LpSeminorm
import logging

@pytest.mark.unit
class TestLpSeminorm:

    """Unit test class for LpSeminorm implementation."""

    @pytest.fixture
    def lp_seminorm(self):
        """Fixture providing a default LpSeminorm instance with p=2."""
        return LpSeminorm(p=2.0)

    @pytest.fixture
    def test_input(self):
        """Fixture providing various test inputs for seminorm computation."""
        return [
            ([1.0, 2.0, 3.0],),  # Valid input
            ([0.0, 0.0],),     # Zero vector
            ([-1.0, 1.0],),     # Negative values
            ([],),               # Empty list
            (['a', 'b'],),       # Invalid input type
        ]

    def test_init(self, lp_seminorm):
        """Test initialization of LpSeminorm with valid p."""
        assert lp_seminorm.p == 2.0
        assert lp_seminorm.resource == "seminorm"

    def test_compute_valid_input(self, lp_seminorm):
        """Test compute method with valid input."""
        input_vec = [1.0, 2.0, 3.0]
        result = lp_seminorm.compute(input_vec)
        expected = np.power(np.sum(np.power(np.abs(input_vec), 2)), 1/2)
        assert np.isclose(result, expected)

    def test_compute_invalid_input(self, test_input):
        """Test compute method with invalid input types."""
        lp_seminorm = LpSeminorm(p=2.0)
        for input_vec in test_input:
            if not isinstance(input_vec[0], (int, float)):
                with pytest.raises(NotImplementedError):
                    lp_seminorm.compute(input_vec[0])

    def test_triangle_inequality(self, lp_seminorm):
        """Test triangle inequality for LpSeminorm."""
        a = [1.0, 2.0]
        b = [3.0, 4.0]
        norm_a = lp_seminorm.compute(a)
        norm_b = lp_seminorm.compute(b)
        norm_ab = lp_seminorm.compute([a[0] + b[0], a[1] + b[1]])
        assert norm_ab <= (norm_a + norm_b)

    def test_scalar_homogeneity(self, lp_seminorm):
        """Test scalar homogeneity property."""
        a = [1.0, 2.0]
        scalar = 2.0
        norm_a = lp_seminorm.compute(a)
        scaled_a = [x * scalar for x in a]
        norm_scaled = lp_seminorm.compute(scaled_a)
        expected = abs(scalar) * norm_a
        assert np.isclose(norm_scaled, expected)

        # Test with negative scalar
        scalar = -1.5
        scaled_a = [x * scalar for x in a]
        norm_scaled = lp_seminorm.compute(scaled_a)
        expected = abs(scalar) * norm_a
        assert np.isclose(norm_scaled, expected)

        # Test with zero scalar
        scalar = 0.0
        scaled_a = [x * scalar for x in a]
        norm_scaled = lp_seminorm.compute(scaled_a)
        expected = abs(scalar) * norm_a
        assert np.isclose(norm_scaled, expected)

    def test_check_triangle_inequality(self, lp_seminorm):
        """Test check_triangle_inequality method."""
        a = [1.0, 2.0]
        b = [3.0, 4.0]
        result = lp_seminorm.check_triangle_inequality(a, b)
        assert isinstance(result, bool)
        assert result is True

    def test_check_scalar_homogeneity(self, lp_seminorm):
        """Test check_scalar_homogeneity method."""
        a = [1.0, 2.0]
        scalar = 2.0
        result = lp_seminorm.check_scalar_homogeneity(a, scalar)
        assert isinstance(result, bool)
        assert result is True