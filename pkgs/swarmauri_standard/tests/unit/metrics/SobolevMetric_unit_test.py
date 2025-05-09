import pytest
from swarmauri_standard.swarmauri_standard.metrics.SobolevMetric import SobolevMetric
import logging
from unittest.mock import patch

@pytest.mark.unit
class TestSobolevMetric:
    """Unit tests for the SobolevMetric class."""
    
    def test_default_initialization(self):
        """Test initialization of SobolevMetric with default parameters."""
        metric = SobolevMetric()
        assert metric.order == 2
        assert metric.alpha == 1.0

    def test_custom_initialization(self):
        """Test initialization of SobolevMetric with custom parameters."""
        metric = SobolevMetric(order=3, alpha=0.5)
        assert metric.order == 3
        assert metric.alpha == 0.5

    def test_distance_computation(self):
        """Test computation of the Sobolev distance between two functions."""
        metric = SobolevMetric()
        
        # Test with simple functions
        x = lambda t: t
        y = lambda t: t + 1
        
        distance = metric.distance(x, y)
        assert distance >= 0
        
        # Test with identical functions
        identical_x = lambda t: t
        identical_y = lambda t: t
        identical_distance = metric.distance(identical_x, identical_y)
        assert identical_distance == 0

    def test_distances_computation(self):
        """Test computation of multiple distances."""
        metric = SobolevMetric()
        
        x = lambda t: t
        ys = [
            lambda t: t + 1,
            lambda t: t + 2,
            lambda t: t * 2
        ]
        
        distances = metric.distances(x, ys)
        assert isinstance(distances, list)
        assert len(distances) == 3
        
        # Test with None input
        single_distance = metric.distances(x)
        assert isinstance(single_distance, float)

    def test_non_negativity(self):
        """Test the non-negativity property of the metric."""
        metric = SobolevMetric()
        
        x = lambda t: t
        y = lambda t: t + 1
        non_negativity = metric.check_non_negativity(x, y)
        assert non_negativity is True

    def test_identity_property(self):
        """Test the identity property of the metric."""
        metric = SobolevMetric()
        
        x = lambda t: t
        y = lambda t: t
        
        # Test identical functions
        identity_true = metric.check_identity(x, y)
        assert identity_true is True
        
        # Test different functions
        y_different = lambda t: t + 1
        identity_false = metric.check_identity(x, y_different)
        assert identity_false is False

    def test_symmetry_property(self):
        """Test the symmetry property of the metric."""
        metric = SobolevMetric()
        
        x = lambda t: t
        y = lambda t: t + 1
        
        d_xy = metric.distance(x, y)
        d_yx = metric.distance(y, x)
        assert d_xy == d_yx

    def test_triangle_inequality(self):
        """Test the triangle inequality property of the metric."""
        metric = SobolevMetric()
        
        x = lambda t: t
        y = lambda t: t + 1
        z = lambda t: t + 2
        
        d_xz = metric.distance(x, z)
        d_xy = metric.distance(x, y)
        d_yz = metric.distance(y, z)
        
        assert d_xz <= d_xy + d_yz

    def test_string_representation(self):
        """Test string representation of the SobolevMetric instance."""
        metric = SobolevMetric(order=3, alpha=0.5)
        assert str(metric) == "SobolevMetric(order=3, alpha=0.5)"
        assert repr(metric) == "SobolevMetric(order=3, alpha=0.5)"

    @patch(logging.getLogger)
    def test_logging_in_distance_method(self, mock_logger):
        """Test that logging is properly implemented in the distance method."""
        metric = SobolevMetric()
        x = lambda t: t
        y = lambda t: t + 1
        
        metric.distance(x, y)
        
        mock_logger.return_value.debug.assert_called_with(
            "Computing Sobolev distance between functions %s and %s", x, y
        )
        mock_logger.return_value.debug.assert_called_with(
            "Computed Sobolev distance: %.4f", 
            metric.distance(x, y)
        )

@pytest.mark.unit
def test_sobolev_metric_parameterized_distance():
    """Test Sobolev distance with different function types."""
    metric = SobolevMetric()
    
    test_cases = [
        (lambda t: t, lambda t: t + 1, 1.0),
        (lambda t: t**2, lambda t: t**2 + 1, 1.0),
        (lambda t: t**3, lambda t: t**3 + 1, 1.0),
    ]
    
    for x, y, expected_distance in test_cases:
        distance = metric.distance(x, y)
        assert distance >= 0

@pytest.mark.unit
def test_sobolev_metric_non_negativity_parameterized():
    """Test non-negativity with different function types."""
    metric = SobolevMetric()
    
    test_cases = [
        (lambda t: t, lambda t: t),
        (lambda t: t, lambda t: t + 1),
        (lambda t: t**2, lambda t: t**2 + 1),
    ]
    
    for x, y in test_cases:
        non_negative = metric.check_non_negativity(x, y)
        assert non_negative is True