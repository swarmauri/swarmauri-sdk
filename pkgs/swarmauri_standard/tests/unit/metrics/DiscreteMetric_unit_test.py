import pytest
from swarmauri_standard.swarmauri_standard.metrics.DiscreteMetric import DiscreteMetric
import logging

@pytest.mark.unit
class TestDiscreteMetric:
    """Unit tests for the DiscreteMetric class."""

    @pytest.mark.parametrize("x,y,expected", [
        (1, 1, 0.0),
        (1, 2, 1.0),
        (5.5, 5.5, 0.0),
        ("test", "test", 0.0),
        (True, True, 0.0),
        (1, "1", 1.0),
        (True, False, 1.0)
    ])
    def test_distance(self, x, y, expected):
        """Test the distance method with various input types."""
        metric = DiscreteMetric()
        assert metric.distance(x, y) == expected

    @pytest.mark.parametrize("x,y_list,expected", [
        (1, [1, 2, 3], [0.0, 1.0, 1.0]),
        ("test", ["test", "test2", "test"], [0.0, 1.0, 0.0]),
        (True, [True, False, True], [0.0, 1.0, 0.0])
    ])
    def test_distances(self, x, y_list, expected):
        """Test the distances method with various input types."""
        metric = DiscreteMetric()
        assert metric.distances(x, y_list) == expected

    @pytest.mark.parametrize("x,y", [
        (1, 1),
        ("test", "test"),
        (5.5, 5.5),
        (True, True)
    ])
    def test_check_non_negativity(self, x, y):
        """Test the non-negativity axiom."""
        metric = DiscreteMetric()
        assert metric.check_non_negativity(x, y) == True

    @pytest.mark.parametrize("x,y,expected", [
        (1, 1, True),
        (1, 2, False),
        ("test", "test", True),
        ("test", "test2", False),
        (True, True, True),
        (True, False, False)
    ])
    def test_check_identity(self, x, y, expected):
        """Test the identity of indiscernibles axiom."""
        metric = DiscreteMetric()
        assert metric.check_identity(x, y) == expected

    @pytest.mark.parametrize("x,y", [
        (1, 1),
        (1, 2),
        ("test", "test2"),
        (True, False)
    ])
    def test_check_symmetry(self, x, y):
        """Test the symmetry axiom."""
        metric = DiscreteMetric()
        assert metric.check_symmetry(x, y) == True

    @pytest.mark.parametrize("x,y,z,expected", [
        (1, 2, 3, True),
        (1, 1, 1, True),
        ("a", "b", "c", True),
        (True, False, True, True)
    ])
    def test_check_triangle_inequality(self, x, y, z, expected):
        """Test the triangle inequality axiom."""
        metric = DiscreteMetric()
        assert metric.check_triangle_inequality(x, y, z) == expected