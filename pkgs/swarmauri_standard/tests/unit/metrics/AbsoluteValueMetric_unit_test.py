import pytest
from swarmauri_standard.metrics.AbsoluteValueMetric import AbsoluteValueMetric
import logging

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestAbsoluteValueMetric:
    """
    Unit tests for the AbsoluteValueMetric class.

    Inherits From:
        object: Base class for unit tests

    Attributes:
        None

    Methods:
        test_distance: Test the distance method with various inputs
        test_distances: Test the distances method with multiple inputs
        test_non_negativity: Test the non-negativity property
        test_identity: Test the identity property
        test_symmetry: Test the symmetry property
        test_triangle_inequality: Test the triangle inequality property
    """

    @pytest.mark.parametrize(
        "x,y,expected_distance",
        [
            (5, 3, 2.0),
            (3.5, 5.5, 2.0),
            ("10", "20", 10.0),
            (lambda: 15, lambda: 20, 5.0),
        ],
    )
    def test_distance(self, x, y, expected_distance):
        """
        Test the distance method with various input types.

        Args:
            x: First point (int, float, str, or callable)
            y: Second point (int, float, str, or callable)
            expected_distance: Expected distance value
        """
        logger.debug(f"Testing distance between {x} and {y}")
        metric = AbsoluteValueMetric()
        assert metric.distance(x, y) == expected_distance
        logger.debug("Distance test passed")

    def test_distances(self):
        """
        Test the distances method with multiple points.
        """
        logger.debug("Testing multiple distances")
        x = 10.0
        ys = [5.0, 15.0, "20.0", lambda: 12.0]
        expected_distances = [5.0, 5.0, 10.0, 2.0]

        metric = AbsoluteValueMetric()
        distances = metric.distances(x, ys)

        assert len(distances) == len(ys)
        assert all(isinstance(d, float) for d in distances)
        assert distances == expected_distances
        logger.debug("Distances test passed")

    @pytest.mark.parametrize(
        "x,y", [(5, 5), (3.5, 3.5), ("10", "10"), (lambda: 15, lambda: 15)]
    )
    def test_non_negativity(self, x, y):
        """
        Test the non-negativity property of the metric.

        Args:
            x: First point (int, float, str, or callable)
            y: Second point (int, float, str, or callable)
        """
        logger.debug("Testing non-negativity property")
        metric = AbsoluteValueMetric()
        assert metric.check_non_negativity(x, y)
        logger.debug("Non-negativity test passed")

    @pytest.mark.parametrize(
        "x,y", [(5, 5), (3.5, 3.5), ("10", "10"), (lambda: 15, lambda: 15)]
    )
    def test_identity(self, x, y):
        """
        Test the identity property of the metric.

        Args:
            x: First point (int, float, str, or callable)
            y: Second point (int, float, str, or callable)
        """
        logger.debug("Testing identity property")
        metric = AbsoluteValueMetric()
        assert metric.check_identity(x, y)
        logger.debug("Identity test passed")

    @pytest.mark.parametrize(
        "x,y", [(5, 3), (3.5, 5.5), ("10", "20"), (lambda: 15, lambda: 20)]
    )
    def test_symmetry(self, x, y):
        """
        Test the symmetry property of the metric.

        Args:
            x: First point (int, float, str, or callable)
            y: Second point (int, float, str, or callable)
        """
        logger.debug("Testing symmetry property")
        metric = AbsoluteValueMetric()
        assert metric.check_symmetry(x, y)
        logger.debug("Symmetry test passed")

    def test_triangle_inequality(self):
        """
        Test the triangle inequality property of the metric.
        """
        logger.debug("Testing triangle inequality property")
        metric = AbsoluteValueMetric()

        # Test with numbers
        x = 1.0
        y = 2.0
        z = 3.0
        assert metric.check_triangle_inequality(x, y, z)

        # Test with strings
        x = "1"
        y = "2"
        z = "3"
        assert metric.check_triangle_inequality(x, y, z)

        # Test with callables
        x = lambda: 1.0
        y = lambda: 2.0
        z = lambda: 3.0
        assert metric.check_triangle_inequality(x, y, z)

        logger.debug("Triangle inequality test passed")

    def test_invalid_input(self):
        """
        Test invalid input handling.
        """
        logger.debug("Testing invalid input handling")
        metric = AbsoluteValueMetric()

        with pytest.raises(ValueError):
            metric.distance("invalid", 5)

        with pytest.raises(ValueError):
            metric.distance(5, "invalid")

        with pytest.raises(ValueError):
            metric.distances(5, ["invalid"])

        logger.debug("Invalid input test passed")
