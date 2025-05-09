import pytest
from swarmauri_standard.swarmauri_standard.metrics.LpMetric import LpMetric
import logging


@pytest.mark.unit
class TestLpMetric:
    """Unit tests for the LpMetric class."""

    def test_resource_attribute(self):
        """Test that the resource attribute is correctly set."""
        assert LpMetric.resource == "Metric"

    def test_type_attribute(self):
        """Test that the type attribute is correctly set."""
        assert LpMetric.type == "LpMetric"

    def test_initialization(self):
        """Test that an LpMetric instance initializes correctly."""
        p = 2.0
        lp_metric = LpMetric(p=p)
        assert lp_metric.p == p
        assert isinstance(lp_metric.norm, GeneralLpNorm)

    def test_invalid_p_value(self):
        """Test that invalid p values raise a ValueError."""
        with pytest.raises(ValueError):
            LpMetric(p=1)

        with pytest.raises(ValueError):
            LpMetric(p=-2)

    def test_distance_scalar(self):
        """Test distance calculation between scalar values."""
        lp_metric = LpMetric(p=2)
        assert lp_metric.distance(1, 1) == 0
        assert lp_metric.distance(2, 1) == 1.0
        assert lp_metric.distance(3.5, 1.5) == 2.0

    def test_distance_vector(self):
        """Test distance calculation between vector values."""
        lp_metric = LpMetric(p=2)
        x = [1, 2, 3]
        y = [4, 5, 6]
        expected = (3**2 + 3**2 + 3**2) ** 0.5
        assert lp_metric.distance(x, y) == expected

    def test_distance_different_lengths(self):
        """Test that vectors of different lengths raise ValueError."""
        lp_metric = LpMetric(p=2)
        x = [1, 2]
        y = [3, 4, 5]
        with pytest.raises(ValueError):
            lp_metric.distance(x, y)

    def test_non_negativity(self):
        """Test the non-negativity property."""
        lp_metric = LpMetric(p=2)
        assert lp_metric.check_non_negativity(1, 1)
        assert lp_metric.check_non_negativity(1, 2)

    def test_identity(self):
        """Test the identity property."""
        lp_metric = LpMetric(p=2)
        assert lp_metric.check_identity(1, 1)
        assert not lp_metric.check_identity(1, 2)

    def test_symmetry(self):
        """Test the symmetry property."""
        lp_metric = LpMetric(p=2)
        x = 1
        y = 2
        assert lp_metric.check_symmetry(x, y)

    def test_triangle_inequality(self):
        """Test the triangle inequality property."""
        lp_metric = LpMetric(p=2)
        x = 1
        y = 2
        z = 3
        assert lp_metric.check_triangle_inequality(x, y, z)

    @pytest.mark.parametrize(
        "p,x,y,expected",
        [
            (2, 1, 1, 0),
            (2, 2, 1, 1.0),
            (1.5, 3, 1, 2.0),
        ],
    )
    def test_parameterized_distance(self, p, x, y, expected):
        """Test parameterized distance calculations."""
        lp_metric = LpMetric(p=p)
        assert lp_metric.distance(x, y) == expected

    @pytest.mark.parametrize(
        "x,y",
        [
            (1, 1),
            (2, 3),
            (3.5, 1.5),
        ],
    )
    def test_parameterized_non_negativity(self, x, y):
        """Test parameterized non-negativity."""
        lp_metric = LpMetric(p=2)
        assert lp_metric.check_non_negativity(x, y)

    @pytest.mark.parametrize(
        "x,y",
        [
            (1, 1),
            (2, 2),
            (3.5, 3.5),
        ],
    )
    def test_parameterized_identity(self, x, y):
        """Test parameterized identity."""
        lp_metric = LpMetric(p=2)
        assert lp_metric.check_identity(x, y)
