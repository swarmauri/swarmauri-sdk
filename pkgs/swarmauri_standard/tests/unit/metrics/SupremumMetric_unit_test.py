import pytest
import numpy as np
from swarmauri_standard.swarmauri_standard.metrics.SupremumMetric import SupremumMetric

@pytest.mark.unit
class TestSupremumMetric:
    """Unit tests for the SupremumMetric class."""
    
    @pytest.fixture
    def valid_vectors(self):
        """Fixture providing valid vector pairs for testing."""
        return [
            ([0, 1, 2], [3, 4, 5]),
            (np.array([1, 2, 3]), np.array([4, 5, 6])),
            ([-1, 0, 1], [1, 0, -1]),
            ([], [])  # Edge case: empty vectors
        ]
    
    @pytest.fixture
    def single_vector(self):
        """Fixture providing a single vector for testing."""
        return [1, 2, 3]
    
    @pytest.fixture
    def different_length_vectors(self):
        """Fixture providing vectors of different lengths."""
        return ([1, 2], [3, 4, 5])
    
    def test_resource(self):
        """Test the resource property."""
        assert SupremumMetric.resource == "metric"
        
    def test_type(self):
        """Test the type property."""
        assert SupremumMetric.type == "SupremumMetric"
        
    @pytest.mark.parametrize("x,y", ["valid_vectors"])
    def test_distance_valid(self, x, y):
        """Test computing valid distances between vectors."""
        metric = SupremumMetric()
        distance = metric.distance(x, y)
        assert distance >= 0
        
    def test_distance_empty_vectors(self, valid_vectors):
        """Test computing distance with empty vectors."""
        x, y = valid_vectors[-1]
        metric = SupremumMetric()
        distance = metric.distance(x, y)
        assert distance == 0
        
    def test_distance_single_element_vectors(self, single_vector):
        """Test computing distance with single-element vectors."""
        x = [5]
        y = [3]
        metric = SupremumMetric()
        distance = metric.distance(x, y)
        assert distance == 2
        
    def test_distance_different_length_vectors(self, different_length_vectors):
        """Test computing distance with vectors of different lengths."""
        x, y = different_length_vectors
        metric = SupremumMetric()
        with pytest.raises(ValueError):
            metric.distance(x, y)
            
    def test_distances_multiple_vectors(self, valid_vectors):
        """Test computing distances with multiple vectors."""
        x = [1, 2, 3]
        ys = [valid_vectors[0][1], valid_vectors[1][1]]
        metric = SupremumMetric()
        results = metric.distances(x, ys)
        assert isinstance(results, list)
        assert len(results) == len(ys)
        
    def test_distances_single_vector(self, single_vector):
        """Test computing distances when ys is None."""
        x = single_vector
        metric = SupremumMetric()
        distance = metric.distances(x)
        assert distance == 0
        
    def test_check_non_negativity_valid(self, valid_vectors):
        """Test non-negativity check with valid vectors."""
        x, y = valid_vectors[0]
        metric = SupremumMetric()
        assert metric.check_non_negativity(x, y) is True
        
    def test_check_non_negativity_empty_vectors(self, valid_vectors):
        """Test non-negativity check with empty vectors."""
        x, y = valid_vectors[-1]
        metric = SupremumMetric()
        assert metric.check_non_negativity(x, y) is True
        
    def test_check_identity_same_vectors(self, valid_vectors):
        """Test identity check with identical vectors."""
        x, y = valid_vectors[0]
        metric = SupremumMetric()
        assert metric.check_identity(x, x) is True
        
    def test_check_identity_different_vectors(self, valid_vectors):
        """Test identity check with different vectors."""
        x, y = valid_vectors[0]
        metric = SupremumMetric()
        assert metric.check_identity(x, y) is False
        
    def test_check_symmetry(self, valid_vectors):
        """Test symmetry property."""
        x, y = valid_vectors[0]
        metric = SupremumMetric()
        assert metric.check_symmetry(x, y) is True
        
    def test_check_triangle_inequality(self, valid_vectors):
        """Test triangle inequality."""
        x, y = valid_vectors[0]
        z = [5, 5, 5]
        metric = SupremumMetric()
        assert metric.check_triangle_inequality(x, y, z) is True