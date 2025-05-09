import pytest
import numpy as np
import logging

from swarmauri_standard.swarmauri_standard.metrics.SobolevMetric import SobolevMetric


@pytest.mark.unit
class TestSobolevMetric:
    """Unit tests for the SobolevMetric class implementation."""

    def test_init(self):
        """Test initialization of SobolevMetric with specified parameters."""
        order = 3
        metric = SobolevMetric(order=order)
        assert metric.order == order
        assert metric.resource == "Metric"

    def test_distance_callable_inputs(self):
        """Test distance calculation with callable functions."""

        # Define test functions
        def f(x):
            return x

        def g(x):
            return x + 1

        metric = SobolevMetric()
        distance = metric.distance(f, g)
        assert distance >= 0

    def test_distance_array_inputs(self):
        """Test distance calculation with array inputs."""
        # Create test arrays
        x = np.array([1.0, 2.0, 3.0])
        y = np.array([1.0, 2.0, 3.0])

        metric = SobolevMetric()
        distance = metric.distance(x, y)
        assert distance == 0.0

    def test_distance_string_inputs(self):
        """Test that string inputs raise ValueError."""
        metric = SobolevMetric()
        with pytest.raises(ValueError):
            metric.distance("invalid", "invalid")

    def test_compute_derivatives(self):
        """Test numerical derivative computation."""

        # Define a test function
        def f(x):
            return x**2

        points = np.array([0.0, 1.0])
        metric = SobolevMetric(order=2)
        derivs = metric._compute_derivatives(f, points, 2)

        # Check function values
        assert np.allclose(derivs[0], [0.0, 1.0], rtol=1e-3)

        # Check first derivative values
        assert np.allclose(derivs[1], [2 * 0.0, 2 * 1.0], rtol=1e-3)

        # Check second derivative values
        assert np.allclose(derivs[2], [2.0, 2.0], rtol=1e-3)

    def test_distances(self):
        """Test computing distances to multiple points."""
        metric = SobolevMetric()

        def f(x):
            return x

        def g(x):
            return x + 1

        def h(x):
            return x**2

        distances = metric.distances(f, [f, g, h])
        assert isinstance(distances, list)
        assert len(distances) == 3

    def test_check_non_negativity(self):
        """Test non-negativity property."""

        def f(x):
            return x

        def g(x):
            return x + 1

        metric = SobolevMetric()
        metric.check_non_negativity(f, g)

    def test_check_identity(self):
        """Test identity of indiscernibles."""

        def f(x):
            return x

        metric = SobolevMetric()
        metric.check_identity(f, f)

    def test_check_symmetry(self):
        """Test symmetry property."""

        def f(x):
            return x

        def g(x):
            return x + 1

        metric = SobolevMetric()
        metric.check_symmetry(f, g)

    def test_check_triangle_inequality(self):
        """Test triangle inequality."""

        def f(x):
            return x

        def g(x):
            return x + 1

        def h(x):
            return x + 2

        metric = SobolevMetric()
        metric.check_triangle_inequality(f, g, h)


def test_sobolev_metric_logger():
    """Test that logging is properly configured."""
    logger = logging.getLogger(__name__)
    assert logger.name == __name__
