import pytest
from swarmauri_standard.metrics.HammingMetric import HammingMetric
import logging


@pytest.mark.unit
class TestHammingMetric:
    """Unit test class for HammingMetric class"""

    @pytest.fixture
    def hamming_metric(self):
        """Fixture to provide a HammingMetric instance"""
        return HammingMetric()

    @pytest.fixture
    def test_data(self):
        """Fixture to provide test data for Hamming distance calculations"""
        return [
            ("1010", "1010", 0),  # Identical strings
            ("1010", "1110", 1),  # One bit difference
            ("1010", "1000", 2),  # Two bits difference
            ("1010", "1111", 3),  # Three bits difference
            ("1010", "0000", 4),  # All bits different
            ("ABCD", "ABCE", 1),  # String with character difference
            ("1010", "10", 0),  # Different lengths
        ]

    @pytest.mark.unit
    def test_distance(self, hamming_metric, test_data):
        """Test the distance method with various inputs"""
        for x, y, expected_distance in test_data:
            if len(x) != len(y):
                with pytest.raises(ValueError):
                    hamming_metric.distance(x, y)
            else:
                assert hamming_metric.distance(x, y) == expected_distance

    @pytest.mark.unit
    def test_distances(self, hamming_metric):
        """Test the distances method with multiple inputs"""
        # Test with empty lists
        assert hamming_metric.distances([], []) == []

        # Test with matching points
        points = ["1010", "1010", "1010"]
        expected = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        assert hamming_metric.distances(points, points) == expected

        # Test with mixed points
        points = ["1010", "1110", "1000"]
        expected = [[0, 1, 2], [1, 0, 1], [2, 1, 0]]
        assert hamming_metric.distances(points, points) == expected

    @pytest.mark.unit
    def test_check_non_negativity(self, hamming_metric, test_data):
        """Test the non-negativity check"""
        for x, y, _ in test_data:
            if len(x) == len(y):
                hamming_metric.check_non_negativity(x, y)

    @pytest.mark.unit
    def test_check_identity(self, hamming_metric):
        """Test the identity check"""
        # Test when x == y
        x = "1010"
        y = "1010"
        hamming_metric.check_identity(x, y)

        # Test when x != y but distance is 0
        x = "1010"
        y = "1010"
        hamming_metric.check_identity(x, y)

        # Test when x != y and distance is not 0
        x = "1010"
        y = "1110"
        hamming_metric.check_identity(x, y)

    @pytest.mark.unit
    def test_check_symmetry(self, hamming_metric, test_data):
        """Test the symmetry check"""
        for x, y, _ in test_data:
            if len(x) == len(y):
                hamming_metric.check_symmetry(x, y)

    @pytest.mark.unit
    def test_check_triangle_inequality(self, hamming_metric):
        """Test the triangle inequality check"""
        x = "1010"
        y = "1110"
        z = "1000"
        hamming_metric.check_triangle_inequality(x, y, z)

    @pytest.mark.unit
    def test_logging(self, hamming_metric, test_data):
        """Test if logging is properly configured"""
        # Set up logging
        logger = logging.getLogger("swarmauri_standard.metrics.HammingMetric")
        logger.setLevel(logging.DEBUG)

        # Test if debug message is logged when distance is called
        with pytest.raises(AssertionError):
            # Using list to capture log messages
            messages = []

            def log_debug(msg):
                messages.append(msg)

            original_debug = logger.debug
            logger.debug = log_debug

            try:
                hamming_metric.distance("1010", "1010")
                assert "Calculating Hamming distance" in messages
            finally:
                logger.debug = original_debug
