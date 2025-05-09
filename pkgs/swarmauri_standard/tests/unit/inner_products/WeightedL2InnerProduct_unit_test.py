import pytest
import numpy as np
import logging
from swarmauri_standard.inner_products import WeightedL2InnerProduct
from swarmauri_core.vectors import IVector

logger = logging.getLogger(__name__)

@pytest.mark.unit
class TestWeightedL2InnerProduct:
    """Unit tests for WeightedL2InnerProduct class."""
    
    def setup_class(self):
        """Setup class-level resources."""
        self.test_weight_function = lambda x: x**2 + 1  # Positive weight function
        self.weighted_l2 = WeightedL2InnerProduct(self.test_weight_function)

    def test_init_with_valid_weight_function(self):
        """Test initialization with a valid weight function."""
        # Arrange
        weight_func = lambda x: x**2 + 1  # Positive function
        
        # Act
        weighted_l2 = WeightedL2InnerProduct(weight_func)
        
        # Assert
        assert weighted_l2.weight_function is not None
        assert callable(weighted_l2.weight_function)
        
    def test_init_with_invalid_weight_function(self):
        """Test initialization with a weight function that can be zero or negative."""
        # Arrange
        weight_func = lambda x: x**2 - 1  # Can be zero or negative
        
        # Act and Assert
        with pytest.raises(ValueError):
            WeightedL2InnerProduct(weight_func)

    def test_compute_with_numpy_arrays(self):
        """Test compute method with numpy arrays."""
        # Arrange
        a = np.array([1, 2])
        b = np.array([3, 4])
        expected = np.dot(a * np.sqrt(self.test_weight_function(a)), 
                         b * np.sqrt(self.test_weight_function(b)))
        
        # Act
        result = self.weighted_l2.compute(a, b)
        
        # Assert
        assert np.allclose(result, expected, atol=1e-6)

    def test_compute_with_ivectors(self):
        """Test compute method with IVector instances."""
        # Arrange
        a = IVector(np.array([1, 2]))
        b = IVector(np.array([3, 4]))
        expected = np.dot(a.vector * np.sqrt(self.test_weight_function(a.vector)), 
                         b.vector * np.sqrt(self.test_weight_function(b.vector)))
        
        # Act
        result = self.weighted_l2.compute(a, b)
        
        # Assert
        assert np.allclose(result, expected, atol=1e-6)

    def test_compute_with_callables(self):
        """Test compute method with callable functions."""
        # Arrange
        a = lambda x: x
        b = lambda x: x**2
        sample_x = np.linspace(0, 1, 100)
        a_values = a(sample_x)
        b_values = b(sample_x)
        expected = np.dot(a_values * np.sqrt(self.test_weight_function(sample_x)), 
                         b_values * np.sqrt(self.test_weight_function(sample_x)))
        
        # Act
        result = self.weighted_l2.compute(a, b)
        
        # Assert
        assert np.allclose(result, expected, atol=1e-6)

    def test_serialization(self):
        """Test serialization and deserialization."""
        # Act
        instance = WeightedL2InnerProduct(self.test_weight_function)
        dumped_json = instance.model_dump_json()
        validated = instance.model_validate_json(dumped_json)
        
        # Assert
        assert instance.id == validated.id

    def test_str_representation(self):
        """Test string representation."""
        # Act
        str_repr = str(self.weighted_l2)
        
        # Assert
        assert str_repr.startswith("WeightedL2InnerProduct")
        assert "weight_function" in str_repr

@pytest.fixture
def numpy_arrays():
    """Fixture providing numpy arrays for testing."""
    a = np.array([1, 2])
    b = np.array([3, 4])
    return a, b

@pytest.fixture
def ivectors():
    """Fixture providing IVector instances for testing."""
    a = IVector(np.array([1, 2]))
    b = IVector(np.array([3, 4]))
    return a, b

@pytest.mark.unit
class TestWeightedL2InnerProductParameterized:
    """Parameterized unit tests for WeightedL2InnerProduct class."""
    
    @pytest.mark.parametrize("a,b,expected", [
        (np.array([1, 2]), np.array([3, 4]), 20.0),
        (IVector(np.array([1, 2])), IVector(np.array([3, 4])), 20.0),
        (lambda x: x, lambda x: x**2, 20.0)
    ])
    def test_compute_parameterized(self, a, b, expected):
        """Test compute method with different input types."""
        # Act
        result = self.weighted_l2.compute(a, b)
        
        # Assert
        assert np.allclose(result, expected, atol=1e-6)