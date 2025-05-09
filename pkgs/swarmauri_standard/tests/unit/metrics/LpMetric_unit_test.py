import pytest
from swarmauri_standard.metrics.LpMetric import LpMetric
import logging

@pytest.fixture
def lp_metricFixture(p: float = 2.0):
    """Fixture to create LpMetric instances with specified p value."""
    return LpMetric(p=p)

@pytest.mark.unit
class TestLpMetric:
    """Unit tests for the LpMetric class implementation."""
    
    def test_resource(self):
        """Test that the resource attribute is correctly set."""
        assert LpMetric.resource == "Metric"
        
    def test_type(self):
        """Test that the type attribute is correctly set."""
        assert LpMetric.type == "LpMetric"
        
    def test_p_value(self, lp_metricFixture):
        """Test that the p value is correctly set during initialization."""
        assert lp_metricFixture.p == lp_metricFixture._p
        
    @pytest.mark.parametrize("p", [2.0, 3.0, 1.5])
    def test_valid_p_values(self, p):
        """Test that valid p values are accepted."""
        metric = LpMetric(p=p)
        assert metric.p == p
        
    @pytest.mark.parametrize("invalid_p", ["string", -2, 1, 0])
    def test_invalid_p_values(self, invalid_p):
        """Test that invalid p values raise ValueError."""
        with pytest.raises(ValueError):
            LpMetric(p=invalid_p)
            
    def test_distance_vector(self, lp_metricFixture):
        """Test distance computation for vector inputs."""
        x = [1, 2, 3]
        y = [4, 5, 6]
        distance = lp_metricFixture.distance(x, y)
        assert distance >= 0
        
    def test_distance_matrix(self, lp_metricFixture):
        """Test distance computation for matrix inputs."""
        x = [[1, 2], [3, 4]]
        y = [[5, 6], [7, 8]]
        distance = lp_metricFixture.distance(x, y)
        assert distance >= 0
        
    def test_distance_callable(self, lp_metricFixture):
        """Test distance computation for callable inputs."""
        x = lambda: [1, 2, 3]
        y = lambda: [4, 5, 6]
        distance = lp_metricFixture.distance(x, y)
        assert distance >= 0
        
    def test_identity_property(self, lp_metricFixture):
        """Test the identity property: d(x, y) = 0 iff x == y."""
        x = [1, 2, 3]
        y = [1, 2, 3]
        assert lp_metricFixture.check_identity(x, y)
        
        x_diff = [1, 2, 3]
        y_diff = [4, 5, 6]
        with pytest.raises(AssertionError):
            lp_metricFixture.check_identity(x_diff, y_diff)
            
    def test_symmetry_property(self, lp_metricFixture):
        """Test the symmetry property: d(x, y) = d(y, x)."""
        x = [1, 2, 3]
        y = [4, 5, 6]
        d_xy = lp_metricFixture.distance(x, y)
        d_yx = lp_metricFixture.distance(y, x)
        assert d_xy == d_yx
        
    def test_triangle_inequality(self, lp_metricFixture):
        """Test the triangle inequality: d(x, z) <= d(x, y) + d(y, z)."""
        x = [1, 1]
        y = [2, 2]
        z = [3, 3]
        d_xz = lp_metricFixture.distance(x, z)
        d_xy = lp_metricFixture.distance(x, y)
        d_yz = lp_metricFixture.distance(y, z)
        assert d_xz <= d_xy + d_yz
        
    def test_invalid_input_handling(self, lp_metricFixture):
        """Test that invalid input types raise ValueError."""
        with pytest.raises(ValueError):
            lp_metricFixture.distance([1, 2], "invalid")
            
    def test_serialization(self, lp_metricFixture):
        """Test serialization and deserialization."""
        lp_metric_json = lp_metricFixture.model_dump_json()
        deserialized = LpMetric.model_validate_json(lp_metric_json)
        assert lp_metricFixture.id == deserialized.id