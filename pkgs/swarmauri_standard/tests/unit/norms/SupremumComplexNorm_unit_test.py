import pytest
import numpy as np
from swarmauri_standard.swarmauri_standard.norms.SupremumComplexNorm import SupremumComplexNorm

@pytest.mark.unit
class TestSupremumComplexNorm:
    """Unit tests for SupremumComplexNorm class."""

    @pytest.fixture
    def norm(self):
        """Fixture to provide a default instance of SupremumComplexNorm."""
        return SupremumComplexNorm()

    def test_initializationDefaults(self, norm):
        """Test initialization with default parameters."""
        assert norm.a == 0.0
        assert norm.b == 1.0
        assert norm.num_points == 1000

    def test_initializationCustom(self):
        """Test initialization with custom parameters."""
        a = 2.0
        b = 5.0
        num_points = 500
        norm = SupremumComplexNorm(a=a, b=b, num_points=num_points)
        assert norm.a == a
        assert norm.b == b
        assert norm.num_points == num_points

    @pytest.mark.parametrize("func,expected_norm", [
        (lambda t: t, 1.0),  # Identity function
        (lambda t: np.abs(t - 0.5), 0.5),  # Maximum at t=0 or t=1
        (lambda t: np.sin(2 * np.pi * t), 1.0),  # Maximum of sine function
    ])
    def test_computeCallable(self, norm, func, expected_norm):
        """Test compute method with callable functions."""
        norm = SupremumComplexNorm(a=0.0, b=1.0, num_points=100)
        computed_norm = norm.compute(func)
        assert np.isclose(computed_norm, expected_norm, atol=1e-2)

    @pytest.mark.parametrize("sequence,expected_norm", [
        ([1.0, 2.0, 3.0], 3.0),
        ([-1.0, -2.0, -3.0], 3.0),
        ([1.0 - 2.0j, 2.0 - 3.0j], 2.236),  # sqrt(2^2 + 3^2)
    ])
    def test_computeSequence(self, norm, sequence, expected_norm):
        """Test compute method with sequence input."""
        computed_norm = norm.compute(sequence)
        assert np.isclose(computed_norm, expected_norm, atol=1e-2)

    def test_computeZeroFunction(self, norm):
        """Test compute method with zero function."""
        zero_func = lambda t: 0.0
        computed_norm = norm.compute(zero_func)
        assert computed_norm == 0.0

    def test_computeInvalidInput(self, norm):
        """Test compute method with invalid input type."""
        with pytest.raises(ValueError):
            norm.compute("invalid_input")

    def test_aEqualsB(self, norm):
        """Test compute method when a equals b."""
        norm = SupremumComplexNorm(a=0.5, b=0.5, num_points=1)
        value = 10.0
        norm_func = lambda t: value
        computed_norm = norm.compute(norm_func)
        assert computed_norm == value

    def test_strRepresentation(self, norm):
        """Test string representation of the norm."""
        expected_str = f"SupremumComplexNorm(a={norm.a}, b={norm.b}, num_points={norm.num_points})"
        assert str(norm) == expected_str

    def test_reprRepresentation(self, norm):
        """Test representation of the norm."""
        expected_repr = f"SupremumComplexNorm(a={norm.a}, b={norm.b}, num_points={norm.num_points})"
        assert repr(norm) == expected_repr