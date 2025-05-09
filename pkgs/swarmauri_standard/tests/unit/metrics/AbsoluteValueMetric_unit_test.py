import pytest
import logging
from swarmauri_standard.metrics.AbsoluteValueMetric import AbsoluteValueMetric


@pytest.fixture
def absolute_value_metric():
    """Fixture to provide an instance of AbsoluteValueMetric for testing."""
    return AbsoluteValueMetric()


@pytest.mark.unit
class TestAbsoluteValueMetric:
    """Unit test class for the AbsoluteValueMetric class."""

    def test_distance_happy_path(self, absolute_value_metric):
        """Test the distance method with valid positive inputs."""
        x, y = 5.0, 3.0
        expected = 2.0
        assert absolute_value_metric.distance(x, y) == expected

    def test_distance_negative_input(self, absolute_value_metric):
        """Test the distance method with negative inputs."""
        x, y = -3.0, -5.0
        expected = 2.0
        assert absolute_value_metric.distance(x, y) == expected

    def test_distance_zero_input(self, absolute_value_metric):
        """Test the distance method with zero inputs."""
        x, y = 0.0, 0.0
        expected = 0.0
        assert absolute_value_metric.distance(x, y) == expected

    def test_distance_invalid_input(self, absolute_value_metric):
        """Test the distance method with invalid non-numeric inputs."""
        x, y = "a", 5
        with pytest.raises(TypeError):
            absolute_value_metric.distance(x, y)

    @pytest.mark.parametrize(
        "xs,ys,expected",
        [
            ([1, 2, 3], [4, 5, 6], [[3, 3, 3], [3, 3, 3], [3, 3, 3]]),
            ([0.5, 1.5], [2.5, 3.5], [[2.0, 2.0], [2.0, 2.0]]),
        ],
    )
    def test_distances_happy_path(self, absolute_value_metric, xs, ys, expected):
        """Test the distances method with valid input lists."""
        result = absolute_value_metric.distances(xs, ys)
        assert result == expected

    def test_distances_empty_lists(self, absolute_value_metric):
        """Test the distances method with empty input lists."""
        xs, ys = [], []
        result = absolute_value_metric.distances(xs, ys)
        assert result == []

    def test_distances_invalid_input(self, absolute_value_metric):
        """Test the distances method with invalid non-numeric inputs."""
        xs, ys = ["a"], [5]
        with pytest.raises(TypeError):
            absolute_value_metric.distances(xs, ys)

    def test_check_non_negativity_happy_path(self, absolute_value_metric):
        """Test non-negativity check with valid positive distance."""
        x, y = 3, 5
        absolute_value_metric.check_non_negativity(x, y)

    def test_check_non_negativity_zero_distance(self, absolute_value_metric):
        """Test non-negativity check when x equals y."""
        x, y = 5, 5
        absolute_value_metric.check_non_negativity(x, y)

    @pytest.mark.parametrize("x,y", [(5, 3), (-3, -5), (0, 0)])
    def test_check_non_negativity_multiple_cases(self, absolute_value_metric, x, y):
        """Test non-negativity check with multiple input cases."""
        absolute_value_metric.check_non_negativity(x, y)

    @pytest.mark.parametrize("x,y", [(5, 5), (-3, -3), (0, 0)])
    def test_check_identity_happy_path(self, absolute_value_metric, x, y):
        """Test identity check when x equals y."""
        absolute_value_metric.check_identity(x, y)

    @pytest.mark.parametrize("x,y", [(5, 3), (-3, -5), (0, 1)])
    def test_check_identity_different_values(self, absolute_value_metric, x, y):
        """Test identity check when x and y are different."""
        absolute_value_metric.check_identity(x, y)

    @pytest.mark.parametrize(
        "x,y", [(5, 3), (3, 5), (-3, -5), (-5, -3), (0, 1), (1, 0)]
    )
    def test_check_symmetry_happy_path(self, absolute_value_metric, x, y):
        """Test symmetry check with multiple input cases."""
        absolute_value_metric.check_symmetry(x, y)

    @pytest.mark.parametrize(
        "x,y,z,expected", [(1, 2, 3, True), (0, 5, 3, True), (-3, -1, 2, True)]
    )
    def test_check_triangle_inequality_happy_path(
        self, absolute_value_metric, x, y, z, expected
    ):
        """Test triangle inequality check with valid cases."""
        absolute_value_metric.check_triangle_inequality(x, y, z)

    @pytest.mark.parametrize("x,y,z", [(1, 2, 5), (-5, -3, -1), (0, 1, 2)])
    def test_check_triangle_inequality_multiple_cases(
        self, absolute_value_metric, x, y, z
    ):
        """Test triangle inequality with multiple input cases."""
        absolute_value_metric.check_triangle_inequality(x, y, z)
