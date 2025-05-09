import pytest
import logging
from unittest.mock import MagicMock
from typing import Sequence, Callable
from swarmauri_standard.norms.SupremumComplexNorm import SupremumComplexNorm


@pytest.mark.unit
class TestSupremumComplexNorm:
    """
    Unit tests for the SupremumComplexNorm class implementation.
    """

    def test_compute_callable(self):
        """
        Test compute method with a callable input.
        """
        norm = SupremumComplexNorm()
        # Mock a simple function that returns a constant complex number
        mock_func = MagicMock(return_value=3 + 4j)

        # Since we're mocking, we don't need to evaluate over interval
        # Just test the compute method's logic
        result = norm.compute(mock_func)
        assert result == 5.0  # Magnitude of 3+4j

    def test_compute_sequence(self):
        """
        Test compute method with a sequence input.
        """
        norm = SupremumComplexNorm()
        # Test with a sequence of complex numbers
        complex_sequence = [1 + 2j, 3 + 4j, 5 + 6j]
        expected = max(abs(c) for c in complex_sequence)
        result = norm.compute(complex_sequence)
        assert result == expected

    def test_check_non_negativity(self):
        """
        Test the non-negativity property check.
        """
        norm = SupremumComplexNorm()
        # Test with zero vector
        zero_vector = [0j, 0j]
        assert norm.check_non_negativity(zero_vector) == True

        # Test with non-zero vector
        non_zero = [1j, 2j]
        assert norm.check_non_negativity(non_zero) == True

    def test_check_triangle_inequality(self):
        """
        Test triangle inequality property.
        """
        norm = SupremumComplexNorm()
        # Test with simple vectors
        x = [1j, 2j]
        y = [3j, 4j]
        x_plus_y = [4j, 6j]

        norm_x = norm.compute(x)
        norm_y = norm.compute(y)
        norm_xy = norm.compute(x_plus_y)

        assert norm.check_triangle_inequality(x, y)

    def test_check_absolute_homogeneity(self):
        """
        Test absolute homogeneity property.
        """
        norm = SupremumComplexNorm()
        # Test with alpha = 2.0
        x = [1j, 2j]
        alpha = 2.0
        norm_x = norm.compute(x)
        norm_alpha_x = norm.compute([alpha * val for val in x])

        assert norm.check_absolute_homogeneity(x, alpha)

        # Test with alpha = -1.0
        alpha = -1.0
        norm_alpha_x = norm.compute([alpha * val for val in x])
        assert norm.check_absolute_homogeneity(x, alpha)

        # Test with alpha = 0.0
        alpha = 0.0
        norm_alpha_x = norm.compute([alpha * val for val in x])
        assert norm.check_absolute_homogeneity(x, alpha)

    def test_check_definiteness(self):
        """
        Test definiteness property.
        """
        norm = SupremumComplexNorm()
        # Test with zero vector
        zero_vector = [0j, 0j]
        assert norm.check_definiteness(zero_vector) == True

        # Test with non-zero vector
        non_zero = [1j, 2j]
        assert norm.check_definiteness(non_zero) == True


logger = logging.getLogger(__name__)
