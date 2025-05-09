import pytest
from swarmauri_standard.swarmauri_standard.metrics.HammingMetric import HammingMetric
import logging

logger = logging.getLogger(__name__)

@pytest.mark.unit
class TestHammingMetric:
    """Unit tests for HammingMetric class."""
    
    @pytest.fixture
    def hamming_metric(self):
        """Fixture to provide a HammingMetric instance for testing."""
        return HammingMetric()

    @pytest.mark.unit
    def test_distance_equal_sequences(self, hamming_metric):
        """Test distance method with identical sequences."""
        x = "test"
        y = "test"
        assert hamming_metric.distance(x, y) == 0.0

    @pytest.mark.unit
    def test_distance_different_sequences(self, hamming_metric):
        """Test distance method with different sequences."""
        x = "test"
        y = "best"
        assert hamming_metric.distance(x, y) == 1.0

    @pytest.mark.unit
    def test_distance_different_length_sequences(self, hamming_metric):
        """Test distance method with sequences of different lengths."""
        x = "test"
        y = "tes"
        with pytest.raises(ValueError):
            hamming_metric.distance(x, y)

    @pytest.mark.unit
    def test_distance_with_list_input(self, hamming_metric):
        """Test distance method with list inputs."""
        x = ["a", "b", "c"]
        y = ["a", "b", "d"]
        assert hamming_metric.distance(x, y) == 1.0

    @pytest.mark.unit
    def test_distance_with_bytes_input(self, hamming_metric):
        """Test distance method with bytes inputs."""
        x = b"test"
        y = b"best"
        assert hamming_metric.distance(x, y) == 1.0

    @pytest.mark.unit
    def test_distances_multiple_sequences(self, hamming_metric):
        """Test distances method with multiple sequences."""
        x = "test"
        ys = ["test", "best", "test1"]
        results = hamming_metric.distances(x, ys)
        assert len(results) == 3
        assert results[0] == 0.0
        assert results[1] == 1.0
        assert results[2] == 1.0

    @pytest.mark.unit
    def test_check_non_negativity(self, hamming_metric):
        """Test non-negativity property."""
        x = "test"
        y = "best"
        assert hamming_metric.check_non_negativity(x, y) == True

    @pytest.mark.unit
    def test_check_identity_true(self, hamming_metric):
        """Test identity property with identical sequences."""
        x = "test"
        y = "test"
        assert hamming_metric.check_identity(x, y) == True

    @pytest.mark.unit
    def test_check_identity_false(self, hamming_metric):
        """Test identity property with different sequences."""
        x = "test"
        y = "best"
        assert hamming_metric.check_identity(x, y) == False

    @pytest.mark.unit
    def test_check_symmetry(self, hamming_metric):
        """Test symmetry property."""
        x = "test"
        y = "best"
        assert hamming_metric.check_symmetry(x, y) == True

    @pytest.mark.unit
    def test_check_triangle_inequality(self, hamming_metric):
        """Test triangle inequality property."""
        x = "test"
        y = "best"
        z = "testz"
        assert hamming_metric.check_triangle_inequality(x, y, z) == True