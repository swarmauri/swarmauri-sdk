import pytest
from swarmauri_standard.norms.L1ManhattanNorm import L1ManhattanNorm
import logging


@pytest.mark.unit
class TestL1ManhattanNorm:
    """Unit test class for the L1ManhattanNorm class."""

    @pytest.fixture
    def l1_norm(self):
        """Fixture to provide an instance of L1ManhattanNorm for testing."""
        return L1ManhattanNorm()

    def test_compute(self, l1_norm):
        """
        Tests the compute method of the L1ManhattanNorm class.

        Tests various input types and values to ensure correct L1 norm calculation.
        """
        # Test with list of numbers
        assert l1_norm.compute([1, 2, 3]) == 6
        # Test with tuple of numbers
        assert l1_norm.compute((3, 4)) == 7
        # Test with string representation of numbers
        assert l1_norm.compute("123") == 6  # Sum of 1+2+3
        # Test with non-iterable input
        with pytest.raises(ValueError):
            l1_norm.compute(123)

    def test_non_negativity(self, l1_norm):
        """
        Tests the non-negativity property of the L1 norm.

        Ensures that the norm is always non-negative for various inputs.
        """
        # Test with positive values
        assert l1_norm.check_non_negativity([1, 2, 3]) == True
        # Test with negative values
        assert l1_norm.check_non_negativity([-1, -2, -3]) == True
        # Test with mixed values
        assert l1_norm.check_non_negativity([-1, 2, -3]) == True

    def test_triangle_inequality(self, l1_norm):
        """
        Tests the triangle inequality property of the L1 norm.

        Verifies that ||x + y|| <= ||x|| + ||y|| for various vectors.
        """
        x = [1, 2]
        y = [3, 4]
        assert l1_norm.check_triangle_inequality(x, y) == True

    def test_absolute_homogeneity(self, l1_norm):
        """
        Tests the absolute homogeneity property of the L1 norm.

        Verifies that ||c * x|| = |c| * ||x|| for various scalars.
        """
        x = [1, 2]
        # Test with positive scalar
        assert l1_norm.check_absolute_homogeneity(x, 2) == True
        # Test with negative scalar
        assert l1_norm.check_absolute_homogeneity(x, -2) == True
        # Test with zero scalar
        assert l1_norm.check_absolute_homogeneity(x, 0) == True

    def test_definiteness(self, l1_norm):
        """
        Tests the definiteness property of the L1 norm.

        Ensures that norm(x) = 0 if and only if x = 0.
        """
        # Test with zero vector
        assert l1_norm.check_definiteness([0, 0]) == True
        # Test with non-zero vector
        assert l1_norm.check_definiteness([1, 0]) == False

    def test_resource_type(self, l1_norm):
        """
        Tests the resource type property of the L1ManhattanNorm class.
        """
        assert l1_norm.resource == "Norm"

    def test_type(self, l1_norm):
        """
        Tests the type property of the L1ManhattanNorm class.
        """
        assert l1_norm.type == "L1ManhattanNorm"

    def test_logging(self, l1_norm):
        """
        Tests if the logger is properly initialized.
        """
        assert isinstance(l1_norm.logger, logging.Logger)
        assert l1_norm.logger.name == __name__
