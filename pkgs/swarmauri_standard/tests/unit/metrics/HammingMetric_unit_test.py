import pytest
from swarmauri_standard.metrics import HammingMetric
import logging

@pytest.mark.unit
class TestHammingMetric:
    """Unit tests for the HammingMetric class."""
    
    def test_resource_type(self):
        """Test if the resource type is correctly set."""
        assert HammingMetric.resource == "Metric"
        
    def test_metric_type(self):
        """Test if the metric type is correctly set."""
        assert HammingMetric.type == "HammingMetric"
        
    def test_serialization(self):
        """Test serialization and deserialization of the metric."""
        hamming_metric = HammingMetric()
        test_id = "test_id"
        hamming_metric.model_set_id(test_id)
        serialized = hamming_metric.model_dump_json()
        validated_id = hamming_metric.model_validate_json(serialized)
        assert validated_id == test_id
        
    def test_distance_equal_sequences(self):
        """Test distance calculation for equal sequences."""
        x = [1, 2, 3]
        y = [1, 2, 3]
        distance = HammingMetric().distance(x, y)
        assert distance == 0.0
        
    def test_distance_different_lengths(self):
        """Test distance calculation for sequences of different lengths."""
        x = [1, 2]
        y = [1, 2, 3]
        with pytest.raises(ValueError):
            HammingMetric().distance(x, y)
            
    def test_distance_unequal_sequences(self):
        """Test distance calculation for unequal sequences of the same length."""
        x = [1, 2, 3]
        y = [1, 2, 0]
        distance = HammingMetric().distance(x, y)
        assert distance == 1.0
        
    def test_non_negativity(self):
        """Test the non-negativity property."""
        x = [1, 2, 3]
        y = [1, 2, 3]
        non_negative = HammingMetric().check_non_negativity(x, y)
        assert non_negative is True
        
    def test_identity(self):
        """Test the identity property."""
        x = [1, 2, 3]
        y = [1, 2, 3]
        identity = HammingMetric().check_identity(x, y)
        assert identity is True
        
        x = [1, 2, 3]
        y = [1, 2, 0]
        identity = HammingMetric().check_identity(x, y)
        assert identity is False
        
    def test_symmetry(self):
        """Test the symmetry property."""
        x = [1, 2, 3]
        y = [1, 2, 0]
        symmetric = HammingMetric().check_symmetry(x, y)
        assert symmetric is True
        
    def test_triangle_inequality(self):
        """Test the triangle inequality property."""
        x = [1, 2, 3]
        y = [1, 2, 3]
        z = [1, 2, 3]
        triangle_inequality = HammingMetric().check_triangle_inequality(x, y, z)
        assert triangle_inequality is True
        
        x = [1, 2, 3]
        y = [1, 2, 0]
        z = [1, 2, 3]
        triangle_inequality = HammingMetric().check_triangle_inequality(x, y, z)
        assert triangle_inequality is True
        
    def test_logging(self, caplog):
        """Test if logging is properly configured."""
        with caplog.at_level(logging.DEBUG):
            x = [1, 2, 3]
            y = [1, 2, 0]
            distance = HammingMetric().distance(x, y)
            assert "Calculated Hamming distance: 1" in caplog.text