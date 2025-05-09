import pytest
from swarmauri_standard.swarmauri_standard.inner_products.EuclideanInnerProduct import EuclideanInnerProduct
import numpy as np
import logging

@pytest.fixture
def euclidean_inner_product():
    """Fixture providing an instance of EuclideanInnerProduct"""
    return EuclideanInnerProduct()

@pytest.mark.unit
def test_resource(euclidean_inner_product):
    """Test that the resource attribute is correctly set"""
    assert euclidean_inner_product.resource == "Inner_product"

@pytest.mark.unit
def test_type(euclidean_inner_product):
    """Test that the type attribute is correctly set"""
    assert euclidean_inner_product.type == "EuclideanInnerProduct"

@pytest.mark.unit
def test_compute(euclidean_inner_product):
    """Test the compute method with various input vectors"""
    a = [1, 2, 3]
    b = [4, 5, 6]
    expected_result = 1*4 + 2*5 + 3*6  # 4 + 10 + 18 = 32
    assert euclidean_inner_product.compute(a, b) == expected_result

@pytest.mark.unit
def test_compute_numpy_arrays(euclidean_inner_product):
    """Test the compute method with numpy arrays"""
    a = np.array([1, 2, 3])
    b = np.array([4, 5, 6])
    expected_result = 32
    assert euclidean_inner_product.compute(a, b) == expected_result

@pytest.mark.unit
def test_compute_invalid_vectors(euclidean_inner_product):
    """Test the compute method with invalid vectors"""
    a = [1, 2]
    b = [3, 4, 5]
    with pytest.raises(ValueError):
        euclidean_inner_product.compute(a, b)

@pytest.mark.unit
def test_compute_multidimensional(euclidean_inner_product):
    """Test the compute method with multidimensional arrays"""
    a = np.array([[1], [2]])
    b = np.array([[3], [4]])
    with pytest.raises(ValueError):
        euclidean_inner_product.compute(a, b)

@pytest.mark.unit
def test_check_conjugate_symmetry(euclidean_inner_product):
    """Test the conjugate symmetry check"""
    a = [1, 2, 3]
    b = [4, 5, 6]
    assert euclidean_inner_product.check_conjugate_symmetry(a, b) is True

@pytest.mark.unit
def test_check_linearity(euclidean_inner_product):
    """Test the linearity check"""
    a = [1, 2]
    b = [3, 4]
    c = [5, 6]
    
    # Compute <a + c, b>
    a_plus_c = np.array(a) + np.array(c)
    result = euclidean_inner_product.compute(a_plus_c, b)
    
    # Compute <a, b> + <c, b>
    ab = euclidean_inner_product.compute(a, b)
    cb = euclidean_inner_product.compute(c, b)
    expected = ab + cb
    
    assert np.isclose(result, expected)

@pytest.mark.unit
def test_check_positivity(euclidean_inner_product):
    """Test the positivity check"""
    a = [1, 2, 3]
    assert euclidean_inner_product.check_positivity(a) is True

@pytest.mark.unit
def test_check_positivity_zero_vector(euclidean_inner_product):
    """Test the positivity check with zero vector"""
    a = [0, 0, 0]
    assert euclidean_inner_product.check_positivity(a) is False

@pytest.mark.unit
def test_compute_with_negative_values(euclidean_inner_product):
    """Test compute method with negative values"""
    a = [1, -2, 3]
    b = [-4, 5, -6]
    expected_result = (1*(-4)) + ((-2)*5) + (3*(-6))  # -4 -10 -18 = -32
    assert euclidean_inner_product.compute(a, b) == expected_result

@pytest.mark.unit
def test_compute_with_floats(euclidean_inner_product):
    """Test compute method with floating point numbers"""
    a = [1.5, 2.5, 3.5]
    b = [4.5, 5.5, 6.5]
    expected_result = (1.5*4.5) + (2.5*5.5) + (3.5*6.5)
    assert euclidean_inner_product.compute(a, b) == expected_result

@pytest.mark.unit
def test_compute_with_large_numbers(euclidean_inner_product):
    """Test compute method with large numbers"""
    a = [1000, 2000, 3000]
    b = [4000, 5000, 6000]
    expected_result = 1000*4000 + 2000*5000 + 3000*6000
    assert euclidean_inner_product.compute(a, b) == expected_result

@pytest.mark.unit
def test_serialization(euclidean_inner_product):
    """Test serialization/deserialization"""
    obj = euclidean_inner_product
    # Assuming model_dump_json and model_validate_json are implemented
    # This is just a placeholder test
    obj_dump = obj.model_dump_json()
    obj_validate = obj.model_validate_json(obj_dump)
    assert obj.id == obj_validate.id