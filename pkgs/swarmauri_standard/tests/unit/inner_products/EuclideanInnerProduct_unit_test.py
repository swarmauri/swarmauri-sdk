import pytest
import numpy as np
import logging
from typing import Any, List, Tuple, Union
from numpy.typing import NDArray

from swarmauri_standard.inner_products.EuclideanInnerProduct import EuclideanInnerProduct


# Setup logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def euclidean_inner_product() -> EuclideanInnerProduct:
    """
    Fixture that provides an instance of EuclideanInnerProduct.
    
    Returns
    -------
    EuclideanInnerProduct
        An instance of the EuclideanInnerProduct class
    """
    return EuclideanInnerProduct()


@pytest.mark.unit
def test_instance_creation():
    """Test that EuclideanInnerProduct can be instantiated."""
    inner_product = EuclideanInnerProduct()
    assert inner_product is not None
    assert isinstance(inner_product, EuclideanInnerProduct)


@pytest.mark.unit
def test_resource_attribute():
    """Test that the resource attribute is correctly set."""
    inner_product = EuclideanInnerProduct()
    assert inner_product.resource == "inner_product"


@pytest.mark.unit
def test_type_attribute():
    """Test that the type attribute is correctly set."""
    inner_product = EuclideanInnerProduct()
    assert inner_product.type == "EuclideanInnerProduct"


@pytest.mark.unit
@pytest.mark.parametrize("vec1, vec2, expected", [
    ([1, 2, 3], [4, 5, 6], 32.0),
    ([0, 0, 0], [1, 2, 3], 0.0),
    ([-1, -2, -3], [-4, -5, -6], 32.0),
    ([1.5, 2.5], [3.5, 4.5], 16.5),
])
def test_compute_with_lists(euclidean_inner_product: EuclideanInnerProduct, 
                           vec1: List[float], 
                           vec2: List[float], 
                           expected: float):
    """
    Test computation of Euclidean inner product with list inputs.
    
    Parameters
    ----------
    euclidean_inner_product : EuclideanInnerProduct
        The inner product instance
    vec1 : List[float]
        First vector
    vec2 : List[float]
        Second vector
    expected : float
        Expected result
    """
    result = euclidean_inner_product.compute(vec1, vec2)
    assert result == pytest.approx(expected)


@pytest.mark.unit
@pytest.mark.parametrize("vec1, vec2, expected", [
    ((1, 2, 3), (4, 5, 6), 32.0),
    ((0, 0, 0), (1, 2, 3), 0.0),
    ((-1, -2, -3), (-4, -5, -6), 32.0),
    ((1.5, 2.5), (3.5, 4.5), 16.5),
])
def test_compute_with_tuples(euclidean_inner_product: EuclideanInnerProduct, 
                            vec1: Tuple[float, ...], 
                            vec2: Tuple[float, ...], 
                            expected: float):
    """
    Test computation of Euclidean inner product with tuple inputs.
    
    Parameters
    ----------
    euclidean_inner_product : EuclideanInnerProduct
        The inner product instance
    vec1 : Tuple[float, ...]
        First vector
    vec2 : Tuple[float, ...]
        Second vector
    expected : float
        Expected result
    """
    result = euclidean_inner_product.compute(vec1, vec2)
    assert result == pytest.approx(expected)


@pytest.mark.unit
@pytest.mark.parametrize("vec1, vec2, expected", [
    (np.array([1, 2, 3]), np.array([4, 5, 6]), 32.0),
    (np.array([0, 0, 0]), np.array([1, 2, 3]), 0.0),
    (np.array([-1, -2, -3]), np.array([-4, -5, -6]), 32.0),
    (np.array([1.5, 2.5]), np.array([3.5, 4.5]), 16.5),
])
def test_compute_with_numpy_arrays(euclidean_inner_product: EuclideanInnerProduct, 
                                  vec1: NDArray[np.float_], 
                                  vec2: NDArray[np.float_], 
                                  expected: float):
    """
    Test computation of Euclidean inner product with numpy array inputs.
    
    Parameters
    ----------
    euclidean_inner_product : EuclideanInnerProduct
        The inner product instance
    vec1 : NDArray[np.float_]
        First vector
    vec2 : NDArray[np.float_]
        Second vector
    expected : float
        Expected result
    """
    result = euclidean_inner_product.compute(vec1, vec2)
    assert result == pytest.approx(expected)


@pytest.mark.unit
@pytest.mark.parametrize("vec1, vec2", [
    ([1, 2, 3], [4, 5]),  # Different dimensions
    ([1, 2, 3], "string"),  # Incompatible type
    ([1, 2, float('nan')], [4, 5, 6]),  # Contains NaN
    ([1, 2, float('inf')], [4, 5, 6]),  # Contains infinity
])
def test_compute_with_incompatible_vectors(euclidean_inner_product: EuclideanInnerProduct, 
                                         vec1: Any, 
                                         vec2: Any):
    """
    Test that compute method raises errors for incompatible vectors.
    
    Parameters
    ----------
    euclidean_inner_product : EuclideanInnerProduct
        The inner product instance
    vec1 : Any
        First vector
    vec2 : Any
        Second vector
    """
    with pytest.raises((ValueError, TypeError)):
        euclidean_inner_product.compute(vec1, vec2)


@pytest.mark.unit
@pytest.mark.parametrize("vec1, vec2, expected", [
    ([1, 2, 3], [4, 5, 6], True),
    (np.array([1, 2, 3]), np.array([4, 5, 6]), True),
    ((1, 2, 3), (4, 5, 6), True),
    ([1, 2, 3], [4, 5], False),  # Different dimensions
    ([1, 2, 3], "string", False),  # Incompatible type
    ([1, 2, float('nan')], [4, 5, 6], False),  # Contains NaN
    ([1, 2, float('inf')], [4, 5, 6], False),  # Contains infinity
    (np.array([[1, 2], [3, 4]]), np.array([[5, 6], [7, 8]]), False),  # Not 1D
])
def test_is_compatible(euclidean_inner_product: EuclideanInnerProduct, 
                     vec1: Any, 
                     vec2: Any, 
                     expected: bool):
    """
    Test the is_compatible method for checking vector compatibility.
    
    Parameters
    ----------
    euclidean_inner_product : EuclideanInnerProduct
        The inner product instance
    vec1 : Any
        First vector
    vec2 : Any
        Second vector
    expected : bool
        Expected result of compatibility check
    """
    result = euclidean_inner_product.is_compatible(vec1, vec2)
    assert result == expected


@pytest.mark.unit
def test_mixed_type_computation(euclidean_inner_product: EuclideanInnerProduct):
    """Test computation with mixed input types."""
    list_vec = [1, 2, 3]
    tuple_vec = (4, 5, 6)
    numpy_vec = np.array([7, 8, 9])
    
    # Test list with tuple
    result1 = euclidean_inner_product.compute(list_vec, tuple_vec)
    assert result1 == pytest.approx(32.0)
    
    # Test list with numpy array
    result2 = euclidean_inner_product.compute(list_vec, numpy_vec)
    assert result2 == pytest.approx(50.0)
    
    # Test tuple with numpy array
    result3 = euclidean_inner_product.compute(tuple_vec, numpy_vec)
    assert result3 == pytest.approx(122.0)


@pytest.mark.unit
def test_serialization():
    """Test serialization and deserialization of EuclideanInnerProduct."""
    euclidean_inner_product = EuclideanInnerProduct()
    serialized = euclidean_inner_product.model_dump_json()
    deserialized = EuclideanInnerProduct.model_validate_json(serialized)
    
    assert deserialized.type == euclidean_inner_product.type
    assert deserialized.resource == euclidean_inner_product.resource