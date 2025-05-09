import pytest
import numpy as np
from swarmauri_standard.swarmauri_standard.inner_products.HermitianInnerProduct import HermitianInnerProduct

@pytest.mark.unit
class TestHermitianInnerProduct:
    """Unit test class for HermitianInnerProduct class."""
    
    def test_compute(self, vector_fixture, scalar_fixture):
        """Test the compute method of HermitianInnerProduct.
        
        This test verifies that the Hermitian inner product is computed correctly
        and satisfies the conjugate symmetry property.
        """
        a, b, c = vector_fixture, vector_fixture, scalar_fixture
        
        # Compute inner products
        inner_product_ab = HermitianInnerProduct().compute(a, b)
        inner_product_ba = HermitianInnerProduct().compute(b, a)
        
        # Check conjugate symmetry
        assert np.isclose(inner_product_ab, np.conj(inner_product_ba)), \
            "Conjugate symmetry not satisfied"
            
    def test_linearity(self, vector_fixture, scalar_fixture):
        """Test the linearity property of the inner product in the first argument."""
        a, b, c = vector_fixture, vector_fixture, scalar_fixture
        
        hipp = HermitianInnerProduct()
        
        # Compute <c*a + b, a>
        left_side = hipp.compute(c * a + b, a)
        
        # Compute c*<a, a> + <b, a>
        right_side = c * hipp.compute(a, a) + hipp.compute(b, a)
        
        assert np.isclose(left_side, right_side), \
            "Linearity in the first argument not satisfied"
            
    def test_positivity(self, vector_fixture):
        """Test the positivity property of the inner product."""
        a = vector_fixture
        hipp = HermitianInnerProduct()
        inner_product = hipp.compute(a, a)
        
        # The inner product of a with itself should be positive
        assert inner_product > 0, \
            "Inner product is not positive definite"
            
    def test_resource(self):
        """Test that the resource attribute is correctly set."""
        assert HermitianInnerProduct.resource == "Inner_product", \
            "Resource attribute not set correctly"
            
    def test_type(self):
        """Test that the type attribute is correctly set."""
        assert HermitianInnerProduct.type == "HermitianInnerProduct", \
            "Type attribute not set correctly"

@pytest.fixture
def vector_fixture():
    """Fixture to generate random complex vectors."""
    return np.random.rand(5) + 1j * np.random.rand(5)

@pytest.fixture
def scalar_fixture():
    """Fixture to generate random complex scalars."""
    return np.random.rand() + 1j * np.random.rand()