import pytest
import numpy as np
import logging
from swarmauri_standard.inner_products.TraceFormWeightedInnerProduct import TraceFormWeightedInnerProduct

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestTraceFormWeightedInnerProduct:
    """
    A test class for the TraceFormWeightedInnerProduct implementation.
    """
    
    @pytest.fixture
    def weight_matrix(self):
        """
        Provides a sample weight matrix for testing.
        """
        return np.array([[0.5, 0.0], [0.0, 1.0]])
    
    @pytest.fixture
    def instance(self, weight_matrix):
        """
        Provides a configured instance of TraceFormWeightedInnerProduct for testing.
        """
        return TraceFormWeightedInnerProduct(weight_matrix)
    
    @pytest.mark.unit
    def test_init(self, weight_matrix):
        """
        Tests the initialization of TraceFormWeightedInnerProduct.
        """
        # Test with valid weight matrix
        instance = TraceFormWeightedInnerProduct(weight_matrix)
        assert instance.weight is not None
        assert isinstance(instance.weight, np.ndarray)
        
        # Test with invalid weight
        with pytest.raises(ValueError):
            TraceFormWeightedInnerProduct("invalid_weight")
        
        # Test with valid but different shape
        different_weight = np.array([[1.0]])
        instance = TraceFormWeightedInnerProduct(different_weight)
        assert instance.weight.shape == (1, 1)
        
    @pytest.mark.unit
    def test_compute(self, instance):
        """
        Tests the compute method with various input types and shapes.
        """
        # Test with numpy arrays
        a = np.array([[1, 2], [3, 4]])
        b = np.array([[5, 6], [7, 8]])
        result = instance.compute(a, b)
        assert isinstance(result, float)
        
        # Test with callable matrices
        a_callable = lambda: np.array([[1, 2], [3, 4]])
        b_callable = lambda: np.array([[5, 6], [7, 8]])
        result_callable = instance.compute(a_callable, b_callable)
        assert isinstance(result_callable, float)
        
        # Test with 3D arrays
        a_3d = np.random.rand(2, 2, 2)
        b_3d = np.random.rand(2, 2, 2)
        result_3d = instance.compute(a_3d, b_3d)
        assert isinstance(result_3d, float)
        
        # Test invalid dimensions
        a_incompatible = np.array([[1, 2]])
        b_incompatible = np.array([[3], [4]])
        with pytest.raises(ValueError):
            instance.compute(a_incompatible, b_incompatible)
            
    @pytest.mark.unit
    def test_compute_invalid_dimensions(self, instance):
        """
        Tests the compute method with incompatible matrix dimensions.
        """
        a = np.array([[1, 2]])
        b = np.array([[3], [4]])
        with pytest.raises(ValueError):
            instance.compute(a, b)
            
    @pytest.mark.unit
    def test_serialization(self, instance):
        """
        Tests the serialization and validation methods.
        """
        # Serialize the instance
        serialized = instance.model_dump_json()
        assert isinstance(serialized, dict)
        
        # Validate the serialized model
        is_valid = instance.model_validate_json(serialized)
        assert is_valid
        
    @pytest.mark.unit
    def test_getters(self, instance):
        """
        Tests the type and resource properties.
        """
        assert instance.type == "TraceFormWeightedInnerProduct"
        assert instance.resource == "Inner_product"