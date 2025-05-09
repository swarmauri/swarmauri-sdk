import pytest
import logging
from swarmauri_standard.swarmauri_standard.metrics.HammingMetric import HammingMetric


@pytest.mark.unit
class TestHammingMetric:
    """Unit test class for HammingMetric class."""

    def test_distance_basic(self):
        """Test basic functionality of the distance method."""
        hamming = HammingMetric()
        x = "abc"
        y = "abc"
        assert hamming.distance(x, y) == 0.0

        x = "abc"
        y = "abd"
        assert hamming.distance(x, y) == 1.0

        x = b"abc"
        y = b"abd"
        assert hamming.distance(x, y) == 1.0

    def test_distance_value_error(self):
        """Test that ValueError is raised for sequences of different lengths."""
        hamming = HammingMetric()
        x = "abc"
        y = "abcd"
        with pytest.raises(ValueError):
            hamming.distance(x, y)

    def test_distances_single(self):
        """Test distances method with single sequence."""
        hamming = HammingMetric()
        x = "abc"
        y = "abd"
        result = hamming.distances(x, y)
        assert result == 1.0

    def test_distances_list(self):
        """Test distances method with list of sequences."""
        hamming = HammingMetric()
        x = "abc"
        y_list = ["abd", "abe"]
        result = hamming.distances(x, y_list)
        assert isinstance(result, list)
        assert all(isinstance(item, float) for item in result)

    def test_check_non_negativity(self):
        """Test the non-negativity check method."""
        hamming = HammingMetric()
        x = "abc"
        y = "abd"
        assert hamming.check_non_negativity(x, y) is True

    def test_check_identity(self):
        """Test the identity check method."""
        hamming = HammingMetric()
        x = "abc"
        y = "abc"
        assert hamming.check_identity(x, y) is True

        x = "abc"
        y = "abd"
        assert hamming.check_identity(x, y) is False

        x = "abc"
        y = "abcd"
        with pytest.raises(ValueError):
            hamming.check_identity(x, y)

    def test_check_symmetry(self):
        """Test the symmetry check method."""
        hamming = HammingMetric()
        x = "abc"
        y = "abd"
        assert hamming.check_symmetry(x, y) is True

        x = "abc"
        y = "cba"
        assert hamming.check_symmetry(x, y) is True

    def test_check_triangle_inequality(self):
        """Test the triangle inequality check method."""
        hamming = HammingMetric()
        x = "abc"
        y = "abd"
        z = "abe"
        assert hamming.check_triangle_inequality(x, y, z) is True

    def test_edge_cases(self):
        """Test various edge cases."""
        hamming = HammingMetric()

        # Empty strings
        x = ""
        y = ""
        assert hamming.distance(x, y) == 0.0

        # Single character
        x = "a"
        y = "b"
        assert hamming.distance(x, y) == 1.0

        # Different types (str vs bytes)
        x = "a"
        y = b"a"
        with pytest.raises(TypeError):
            hamming.distance(x, y)

    def test_logging(self, caplog):
        """Test that logging is properly implemented."""
        hamming = HammingMetric()
        x = "abc"
        y = "abd"
        hamming.distance(x, y)

        assert "Calculated Hamming distance: 1" in caplog.text
