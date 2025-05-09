import pytest
from swarmauri_standard.swarmauri_standard.metrics.LevenshteinMetric import (
    LevenshteinMetric,
)
from typing import Union, List, Literal


@pytest.mark.unit
class TestLevenshteinMetric:
    """
    Unit tests for the LevenshteinMetric class.

    This test suite validates the functionality of the LevenshteinMetric class,
    ensuring accurate distance calculations and adherence to metric properties.
    """

    @pytest.mark.unit
    def test_class_attributes(self):
        """
        Test that class attributes are correctly set.
        """
        assert LevenshteinMetric.resource == "Metric"
        assert LevenshteinMetric.type == "LevenshteinMetric"

    @pytest.mark.unit
    def test_distance_basic(self):
        """
        Test basic Levenshtein distance calculation.
        """
        metric = LevenshteinMetric()
        # Example from Wikipedia
        assert metric.distance("kitten", "sitting") == 3
        # Test with lists of characters
        assert metric.distance(list("kitten"), list("sitting")) == 3

    @pytest.mark.unit
    def test_empty_strings(self):
        """
        Test distance calculation with empty strings.
        """
        metric = LevenshteinMetric()
        assert metric.distance("", "") == 0.0
        assert metric.distance("", "test") == 4.0
        assert metric.distance("test", "") == 4.0

    @pytest.mark.unit
    def test_distances_multiple(self):
        """
        Test calculation of distances for multiple strings.
        """
        metric = LevenshteinMetric()
        reference = "test"
        strings = ["test", "tast", "best", "rest"]
        expected = [0.0, 1.0, 1.0, 1.0]
        assert metric.distances(reference, strings) == expected

    @pytest.mark.unit
    def test_check_non_negativity(self):
        """
        Test the non-negativity property of the metric.
        """
        metric = LevenshteinMetric()
        distances = [
            metric.distance("a", "a"),
            metric.distance("a", "b"),
            metric.distance("abc", "def"),
        ]
        assert all(d >= 0 for d in distances)

    @pytest.mark.unit
    def test_check_identity(self):
        """
        Test the identity property of the metric.
        """
        metric = LevenshteinMetric()
        # Test identical strings
        assert metric.check_identity("test", "test") is True
        # Test different strings
        assert metric.check_identity("test", "best") is True

    @pytest.mark.unit
    def test_check_symmetry(self):
        """
        Test the symmetry property of the metric.
        """
        metric = LevenshteinMetric()
        assert metric.check_symmetry("kitten", "sitting") is True
        assert metric.check_symmetry("a", "b") is True

    @pytest.mark.unit
    def test_check_triangle_inequality(self):
        """
        Test the triangle inequality property of the metric.
        """
        metric = LevenshteinMetric()
        # Test with three arbitrary strings
        d_xz = metric.distance("cat", "dog")
        d_xy = metric.distance("cat", "cot")
        d_yz = metric.distance("cot", "dog")
        assert metric.check_triangle_inequality("cat", "cot", "dog") is True
