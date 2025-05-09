import pytest
import logging
from swarmauri_standard.norms.SobolevNorm import SobolevNorm

@pytest.mark.unit
class TestSobolevNorm:
    """Unit tests for the SobolevNorm class implementation."""
    
    @pytest.fixture
    def sobolev_norm(self):
        """Fixture to provide a default SobolevNorm instance."""
        return SobolevNorm()

    def test_type_property(self):
        """Test the type property of the SobolevNorm class."""
        assert SobolevNorm.type == "SobolevNorm"
        
    def test_name_property(self):
        """Test the name property of the SobolevNorm class."""
        assert SobolevNorm().name == "SobolevNorm"

    def test_compute_method_with_function(self, sobolev_norm):
        """Test the compute method with a function input."""
        import numpy as np
        
        # Define a test function and its derivatives
        def f(x):
            return x**2
            
        # Compute Sobolev norm with order 1
        order = 1
        sobolev_norm.order = order
        
        # Compute L2 norm of function and its first derivative
        l2_func = np.linalg.norm([f(x) for x in np.linspace(-1, 1, 100)])
        f_derivative = lambda x: 2*x
        l2_derivative = np.linalg.norm([f_derivative(x) for x in np.linspace(-1, 1, 100)])
        
        expected_norm = (l2_func**2 + l2_derivative**2)**0.5
        computed_norm = sobolev_norm.compute(f)
        
        assert np.allclose(expected_norm, computed_norm, rtol=1e-2)

    def test_compute_method_with_list(self, sobolev_norm):
        """Test the compute method with a list input."""
        import numpy as np
        
        # Define a test list
        x = [1.0, 1.0, 1.0]
        
        # Compute L2 norm
        expected_norm = np.linalg.norm(x)
        
        # Compute Sobolev norm with order 0
        sobolev_norm.order = 0
        computed_norm = sobolev_norm.compute(x)
        
        assert np.allclose(expected_norm, computed_norm)

    def test_compute_method_with_higher_order(self, sobolev_norm):
        """Test the compute method with higher order derivatives."""
        import numpy as np
        
        # Define a test function with known derivatives
        def f(x):
            return x**3
            
        # Compute Sobolev norm with order 2
        order = 2
        sobolev_norm.order = order
        
        # Compute L2 norms of function and its derivatives
        l2_func = np.linalg.norm([f(x) for x in np.linspace(-1, 1, 100)])
        f_first = lambda x: 3*x**2
        l2_first = np.linalg.norm([f_first(x) for x in np.linspace(-1, 1, 100)])
        f_second = lambda x: 6*x
        l2_second = np.linalg.norm([f_second(x) for x in np.linspace(-1, 1, 100)])
        
        expected_norm = (l2_func**2 + l2_first**2 + l2_second**2)**0.5
        computed_norm = sobolev_norm.compute(f)
        
        assert np.allclose(expected_norm, computed_norm, rtol=1e-2)

    def test_invalid_input(self, sobolev_norm):
        """Test that invalid input raises an appropriate error."""
        with pytest.raises(TypeError):
            sobolev_norm.compute("invalid_input")

logger = logging.getLogger(__name__)