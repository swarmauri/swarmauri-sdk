import pytest
import logging
from swarmauri_standard.swarmauri_standard.norms.SobolevNorm import SobolevNorm

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestSobolevNorm:
    """Unit test class for SobolevNorm implementation."""
    
    def test_initialization(self):
        """Test initialization with different parameters."""
        # Test default initialization
        sobolev = SobolevNorm()
        assert sobolev.order == 2
        assert sobolev.alpha == 1.0
        
        # Test custom initialization
        sobolev = SobolevNorm(order=3, alpha=0.5)
        assert sobolev.order == 3
        assert sobolev.alpha == 0.5
        
        # Test edge cases
        with pytest.raises(ValueError):
            SobolevNorm(order=0)
        with pytest.raises(ValueError):
            SobolevNorm(order=-1)

    def test_compute(self):
        """Test the compute method with various inputs."""
        # Test with a simple function
        def func(x):
            return x**2
        
        sobolev = SobolevNorm(order=2)
        norm = sobolev.compute(func)
        assert norm >= 0
        
        # Test with a more complex function
        def complex_func(x):
            return x**3 + 2*x
            
        norm = sobolev.compute(complex_func)
        assert norm >= 0
        
        # Test invalid input
        with pytest.raises(ValueError):
            sobolev.compute("invalid")

    def test_serialization(self):
        """Test serialization and validation."""
        sobolev = SobolevNorm(order=3, alpha=0.7)
        dumped = sobolev.model_dump_json()
        validated = SobolevNorm.model_validate_json(dumped)
        
        assert validated.order == sobolev.order
        assert validated.alpha == sobolev.alpha

    def test_type_and_resource(self):
        """Test type and resource properties."""
        assert SobolevNorm.type == "SobolevNorm"
        assert SobolevNorm.resource == "Norm"

    def test_triangle_inequality(self):
        """Test the triangle inequality."""
        def func1(x):
            return x
            
        def func2(x):
            return x**2
            
        sobolev = SobolevNorm(order=1)
        norm_x = sobolev.compute(func1)
        norm_y = sobolev.compute(func2)
        norm_x_plus_y = sobolev.compute(lambda x: x + x**2)
        
        assert norm_x_plus_y <= norm_x + norm_y

    def test_absolute_homogeneity(self):
        """Test absolute homogeneity."""
        def func(x):
            return x
            
        sobolev = SobolevNorm(order=1)
        a = 2.5
        norm_scaled = sobolev.compute(lambda x: a * func(x))
        norm_original = sobolev.compute(func)
        
        assert norm_scaled == pytest.approx(abs(a) * norm_original)

    def test_definiteness(self):
        """Test definiteness."""
        def zero_func(x):
            return 0
            
        def non_zero_func(x):
            return x
            
        sobolev = SobolevNorm()
        
        # Test zero function
        norm = sobolev.compute(zero_func)
        assert norm == 0
        
        # Test non-zero function
        norm = sobolev.compute(non_zero_func)
        assert norm > 0

    def test_derivative_computation(self):
        """Test derivative computation."""
        def func(x):
            return x**3 + 2*x
            
        sobolev = SobolevNorm()
        
        # Test first derivative
        first_deriv = sobolev._compute_derivative(func, 1)
        assert first_deriv(2) == pytest.approx(3*(2**2) + 2)
        
        # Test second derivative
        second_deriv = sobolev._compute_derivative(func, 2)
        assert second_deriv(2) == pytest.approx(6*2)

    def test_l2_norm_computation(self):
        """Test L2 norm computation."""
        # Test with IVector
        class TestVector:
            def l2_norm(self):
                return 5.0
            
        vector = TestVector()
        norm = SobolevNorm._compute_l2_norm(vector)
        assert norm == 5.0
        
        # Test with sequence
        sequence = [1, 2, 3]
        norm = SobolevNorm._compute_l2_norm(sequence)
        assert norm == pytest.approx((1**2 + 2**2 + 3**2)**0.5)

    def test_string_representation(self):
        """Test string representation."""
        sobolev = SobolevNorm(order=3, alpha=0.5)
        assert str(sobolev) == "SobolevNorm(order=3, alpha=0.5)"
        assert repr(sobolev) == "SobolevNorm(order=3, alpha=0.5)"