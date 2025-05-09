import pytest
from swarmauri_standard.metrics.LevenshteinMetric import LevenshteinMetric
import logging


@pytest.mark.unit
class TestLevenshteinMetric:
    """Unit tests for the LevenshteinMetric class."""

    @pytest.mark.parametrize(
        "x,y,expected_distance",
        [
            ("test", "test", 0),
            ("test", "test", 0),
            ("test", "tst", 1),
            ("test", "tes", 1),
            ("test", "testing", 2),
            ("", "", 0),
            ("", "a", 1),
            ("a", "", 1),
        ],
    )
    def test_distance(self, x, y, expected_distance):
        """Test the distance method with various input pairs."""
        metric = LevenshteinMetric()
        assert metric.distance(x, y) == expected_distance
        assert metric.distance(y, x) == expected_distance  # Test symmetry

    @pytest.mark.parametrize(
        "x,y",
        [
            ("test", "test"),
            ("hello", "hello"),
            ("", ""),
            ("a", "a"),
        ],
    )
    def test_non_negativity(self, x, y):
        """Test the non-negativity property."""
        metric = LevenshteinMetric()
        distance = metric.distance(x, y)
        assert distance >= 0

    @pytest.mark.parametrize(
        "x,y",
        [
            ("test", "test"),
            ("hello", "hello"),
            ("", ""),
            ("a", "a"),
        ],
    )
    def test_identity(self, x, y):
        """Test the identity property."""
        metric = LevenshteinMetric()
        if x == y:
            assert metric.distance(x, y) == 0
        else:
            assert metric.distance(x, y) > 0

    @pytest.mark.parametrize(
        "x,y,z",
        [
            ("test", "test", "test"),
            ("hello", "hello", "hello"),
            ("a", "b", "c"),
            ("kitten", "sitting", "kitten"),
        ],
    )
    def test_triangle_inequality(self, x, y, z):
        """Test the triangle inequality property."""
        metric = LevenshteinMetric()
        d_xz = metric.distance(x, z)
        d_xy = metric.distance(x, y)
        d_yz = metric.distance(y, z)
        assert d_xz <= d_xy + d_yz

    def test_type_attribute(self):
        """Test the type attribute."""
        assert LevenshteinMetric.type == "LevenshteinMetric"

    def test_logging(self, caplog):
        """Test if logging is properly implemented."""
        metric = LevenshteinMetric()
        with caplog.at_level(logging.DEBUG):
            metric.distance("test", "test")
            assert "Calculating Levenshtein distance" in caplog.text
