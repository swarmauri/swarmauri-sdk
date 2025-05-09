import pytest
from swarmauri_standard.inner_products.HermitianInnerProduct import HermitianInnerProduct
import numpy as np

@pytest.mark.unit
def test_compute():
    """Test the compute method of HermitianInnerProduct class."""
    # Create an instance of HermitianInnerProduct
    hermitianip = HermitianInnerProduct()
    
    # Test with valid complex vectors
    a = np.array([1 + 2j, 3 + 4j])
    b = np.array([5 + 6j, 7 + 8j])
    result = hermitianip.compute(a, b)
    
    # Compute expected result using numpy
    expected = np.sum(np.conj(a) * b)
    assert result == expected

    # Test with empty vectors
    a_empty = np.array([], dtype=np.complex_)
    b_empty = np.array([], dtype=np.complex_)
    empty_result = hermitianip.compute(a_empty, b_empty)
    assert empty_result == 0.0

@pytest.mark.unit
def test_check_conjugate_symmetry():
    """Test the conjugate symmetry property."""
    hermitianip = HermitianInnerProduct()
    
    # Create test vectors
    a = np.array([1 + 2j, 3 + 4j])
    b = np.array([5 + 6j, 7 + 8j])
    
    # Compute inner products
    ip_ab = hermitianip.compute(a, b)
    ip_ba = hermitianip.compute(b, a)
    
    # Check if ip_ba is the conjugate of ip_ab
    assert ip_ba == np.conj(ip_ab)

@pytest.mark.unit
def test_check_linearity_first_argument():
    """Test linearity in the first argument."""
    hermitianip = HermitianInnerProduct()
    
    # Create test vectors
    a = np.array([1 + 2j, 3 + 4j])
    b = np.array([5 + 6j, 7 + 8j])
    c = np.array([0 + 1j, 2 + 3j])
    
    # Compute individual inner products
    ip_a_c = hermitianip.compute(a, c)
    ip_b_c = hermitianip.compute(b, c)
    
    # Compute combined inner product
    combined = a + b
    ip_combined_c = hermitianip.compute(combined, c)
    
    # Check linearity: ⟨a + b, c⟩ = ⟨a, c⟩ + ⟨b, c⟩
    assert np.isclose(ip_combined_c, ip_a_c + ip_b_c)
    
    # Test scalar multiplication
    scalar = 2 + 1j
    scaled_a = scalar * a
    ip_scaled_a_c = hermitianip.compute(scaled_a, c)
    assert np.isclose(ip_scaled_a_c, scalar * ip_a_c)

@pytest.mark.unit
def test_check_positivity():
    """Test the positivity property."""
    hermitianip = HermitianInnerProduct()
    
    # Create a non-zero vector
    a = np.array([1 + 2j, 3 + 4j])
    ip = hermitianip.compute(a, a)
    
    # The inner product of a with itself should be positive
    assert ip > 0

@pytest.mark.unit
def test_type_property():
    """Test the type property of HermitianInnerProduct."""
    hermitianip = HermitianInnerProduct()
    assert hermitianip.type == "HermitianInnerProduct"

@pytest.mark.unit
def test_resource_property():
    """Test the resource property of HermitianInnerProduct."""
    hermitianip = HermitianInnerProduct()
    assert hermitianip.resource == "Inner_product"