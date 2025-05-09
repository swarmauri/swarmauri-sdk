import pytest
from swarmauri_standard.swarmauri_standard.norms.LInfNorm import LInfNorm
import logging


@pytest.mark.unit
class TestLInfNorm:
    """Unit tests for the LInfNorm class."""

    def test_resource(self):
        """Test the resource property."""
        assert LInfNorm.resource == "Norm"

    def test_type(self):
        """Test the type property."""
        assert LInfNorm.type == "LInfNorm"

    @pytest.mark.parametrize(
        "x,expected",
        [
            (lambda: 5, 5.0),
            ([1, 2, 3, 4], 4.0),
            (10, 10.0),
            (-10, 10.0),
            ([-5, -3, -8], 8.0),
            ([0, 0, 0], 0.0),
        ],
    )
    def test_compute(self, x, expected):
        """Test the compute method with various inputs."""
        norm = LInfNorm()
        assert norm.compute(x) == expected

    @pytest.mark.parametrize("x", [0, 5, -5, [1, 2, 3], [0, 0, 0], lambda: 0])
    def test_check_non_negativity(self, x):
        """Test the check_non_negativity method."""
        norm = LInfNorm()
        assert norm.check_non_negativity(x) is True

    @pytest.mark.parametrize(
        "x,y", [(1, 2), (2, 1), (-3, 4), ([1, 2], [3, 4]), (lambda: 5, lambda: 7)]
    )
    def test_check_triangle_inequality(self, x, y):
        """Test the check_triangle_inequality method."""
        norm = LInfNorm()
        assert norm.check_triangle_inequality(x, y) is True

    @pytest.mark.parametrize(
        "x,scalar", [(5, 2), (-4, 0.5), ([1, 2, 3], -1), (lambda: 10, 3.5)]
    )
    def test_check_absolute_homogeneity(self, x, scalar):
        """Test the check_absolute_homogeneity method."""
        norm = LInfNorm()
        assert norm.check_absolute_homogeneity(x, scalar) is True

    @pytest.mark.parametrize("x", [0, 0.0, [0, 0, 0], lambda: 0])
    def test_check_definiteness_true(self, x):
        """Test the check_definiteness method for x=0 case."""
        norm = LInfNorm()
        assert norm.check_definiteness(x) is True

    @pytest.mark.parametrize("x", [1, -1, [1, 0], [0, 1], lambda: 5])
    def test_check_definiteness_false(self, x):
        """Test the check_definiteness method for non-zero x."""
        norm = LInfNorm()
        assert norm.check_definiteness(x) is False

    def test_initialization_logging(caplog):
        """Test if initialization logs correctly."""
        norm = LInfNorm()
        with caplog.at_level(logging.DEBUG):
            assert "LInfNorm instance initialized" in caplog.text
