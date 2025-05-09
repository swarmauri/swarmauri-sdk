import pytest
import numpy as np
from swarmauri_standard.swarmauri_standard.metrics.SupremumMetric import SupremumMetric


@pytest.mark.unit
class TestSupremumMetric:
    """Unit tests for the SupremumMetric class."""

    def test_resource_type(self):
        """Test if the resource type is correctly set."""
        assert SupremumMetric.resource == "metric"

    def test_distance_array_inputs(self, array_data):
        """Test distance calculation with array inputs."""
        x, y = array_data
        distance = SupremumMetric().distance(x, y)
        assert distance >= 0
        assert isinstance(distance, float)

    def test_distance_callable_inputs(self, callable_data):
        """Test distance calculation with callable inputs."""
        x, y = callable_data
        distance = SupremumMetric().distance(x, y)
        assert distance >= 0
        assert isinstance(distance, float)

    def test_distance_string_inputs(self, string_data):
        """Test distance calculation with string inputs."""
        x, y = string_data
        distance = SupremumMetric().distance(x, y)
        assert distance >= 0
        assert isinstance(distance, float)

    def test_distances(self, mixed_data):
        """Test calculation of multiple distances."""
        x, ys = mixed_data
        distances = SupremumMetric().distances(x, ys)
        assert isinstance(distances, list)
        assert all(isinstance(d, float) for d in distances)

    def test_non_negativity(self, scalar_values):
        """Test the non-negativity property."""
        x, y = scalar_values
        metric = SupremumMetric()
        distance = metric.distance(x, y)
        assert distance >= 0

    def test_identity_property(self, scalar_values):
        """Test the identity of indiscernibles property."""
        x, y = scalar_values
        metric = SupremumMetric()

        # Test when x == y
        if x == y:
            distance = metric.distance(x, y)
            assert distance == 0
        else:
            # Test when x != y
            distance = metric.distance(x, y)
            assert distance > 0

    def test_symmetry_property(self, scalar_values):
        """Test the symmetry property."""
        x, y = scalar_values
        metric = SupremumMetric()
        distance_xy = metric.distance(x, y)
        distance_yx = metric.distance(y, x)
        assert np.isclose(distance_xy, distance_yx)

    def test_triangle_inequality(self, vector_values):
        """Test the triangle inequality property."""
        x, y, z = vector_values
        metric = SupremumMetric()
        distance_xz = metric.distance(x, z)
        distance_xy = metric.distance(x, y)
        distance_yz = metric.distance(y, z)
        assert distance_xz <= (distance_xy + distance_yz)


@pytest.fixture
def array_data():
    """Fixture providing test array data."""
    x = np.array([1, 2, 3])
    y = np.array([4, 5, 6])
    return x, y


@pytest.fixture
def callable_data():
    """Fixture providing test callable data."""

    def x_func(t):
        return t**2

    def y_func(t):
        return t**3

    return x_func, y_func


@pytest.fixture
def string_data():
    """Fixture providing test string data."""
    return "test_string_x", "test_string_y"


@pytest.fixture
def mixed_data():
    """Fixture providing mixed data types for distance calculations."""
    x = np.array([1, 2, 3])
    ys = [np.array([4, 5, 6]), lambda t: t**2, "test_string"]
    return x, ys


@pytest.fixture
def scalar_values():
    """Fixture providing scalar values for metric property tests."""
    return 5.0, 5.0


@pytest.fixture
def vector_values():
    """Fixture providing vector values for triangle inequality test."""
    x = np.array([1.0, 2.0])
    y = np.array([3.0, 4.0])
    z = np.array([5.0, 6.0])
    return x, y, z
