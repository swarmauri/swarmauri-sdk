import pytest
from typing import Union, List
from swarmauri_standard.metrics import DiscreteMetric
import logging

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestDiscreteMetric:

    @pytest.fixture
    def metric(self):
        """Fixture to provide a DiscreteMetric instance for testing"""
        return DiscreteMetric()

    @pytest.mark.parametrize("x,y,expected", [
        (1, 1, 0),
        ("a", "a", 0),
        (None, None, 0),
        (1, 2, 1),
        ("a", "b", 1),
        (1, None, 1)
    ])
    def test_distance(self, x, y, expected, metric):
        """Test the distance method with various input types and values"""
        assert metric.distance(x, y) == expected

    @pytest.mark.parametrize("x,ys,expected", [
        (1, [1, 2, 1], [0, 1, 0]),
        ("a", ["a", "b", "a"], [0, 1, 0]),
        (None, [None, 1, None], [0, 1, 0]),
        (1, [], [])
    ])
    def test_distances(self, x, ys, expected, metric):
        """Test the distances method with various input types and values"""
        assert metric.distances(x, ys) == expected

    @pytest.mark.parametrize("x,y", [
        (1, 1),
        ("a", "a"),
        (None, None),
        (1, 2),
        ("a", "b")
    ])
    def test_check_non_negativity(self, x, y, metric):
        """Test the non-negativity property"""
        assert metric.check_non_negativity(x, y) is True

    @pytest.mark.parametrize("x,y,expected", [
        (1, 1, True),
        ("a", "a", True),
        (None, None, True),
        (1, 2, False),
        ("a", "b", False)
    ])
    def test_check_identity(self, x, y, expected, metric):
        """Test the identity property"""
        result = metric.check_identity(x, y)
        assert result is expected

    @pytest.mark.parametrize("x,y", [
        (1, 2),
        ("a", "b"),
        (1, None),
        (None, 1)
    ])
    def test_check_symmetry(self, x, y, metric):
        """Test the symmetry property"""
        assert metric.check_symmetry(x, y) is True

    @pytest.mark.parametrize("x,y,z,expected", [
        (1, 2, 1, True),
        ("a", "b", "a", True),
        (1, 2, 3, True),
        (1, None, 2, True)
    ])
    def test_check_triangle_inequality(self, x, y, z, expected, metric):
        """Test the triangle inequality property"""
        assert metric.check_triangle_inequality(x, y, z) is expected