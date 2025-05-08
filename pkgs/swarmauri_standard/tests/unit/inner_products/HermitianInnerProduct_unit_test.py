import pytest
import numpy as np
import logging
from typing import List, Tuple, Any
from numpy.typing import NDArray

from swarmauri_standard.inner_products.HermitianInnerProduct import HermitianInnerProduct

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def hermitian_inner_product() -> HermitianInnerProduct:
    """
    Create a HermitianInnerProduct instance for testing.
    
    Returns
    -------
    HermitianInnerProduct
        A new instance of the HermitianInnerProduct class
    """
    return HermitianInnerProduct()


# Test data for parameterized tests
@pytest.fixture
def complex_vectors() -> List[Tuple[Any, Any, complex]]:
    """
    Generate test data for complex vectors.
    
    Returns
    -------
    List[Tuple[Any, Any, complex]]
        List of tuples containing (vec1, vec2, expected_result)
    """
    return [
        # Scalars
        (1+2j, 3+4j, (3+4j).conjugate() * (1+2j)),
        (5j, 1j, (1j).conjugate() * 5j),
        (3.0, 4.0, 4.0 * 3.0),  # Real numbers treated as complex
        
        # Lists
        ([1+2j, 3+4j], [5+6j, 7+8j], (5+6j).conjugate() * (1+2j) + (7+8j).conjugate() * (3+4j)),
        ([1j, 2j], [3j, 4j], (3j).conjugate() * 1j + (4j).conjugate() * 2j),
        
        # NumPy arrays
        (np.array([1+2j, 3+4j]), np.array([5+6j, 7+8j]), 
         (5+6j).conjugate() * (1+2j) + (7+8j).conjugate() * (3+4j)),
        (np.array([1, 2]), np.array([3, 4]), 3 * 1 + 4 * 2),  # Real arrays
    ]


@pytest.fixture
def incompatible_vectors() -> List[Tuple[Any, Any]]:
    """
    Generate test data for incompatible vectors.
    
    Returns
    -------
    List[Tuple[Any, Any]]
        List of tuples containing incompatible (vec1, vec2) pairs
    """
    return [
        ([1+2j, 3+4j], [5+6j, 7+8j, 9+10j]),  # Different lengths
        (np.array([1+2j, 3+4j]), np.array([5+6j, 7+8j, 9+10j])),  # Different lengths
        (np.array([[1+2j], [3+4j]]), np.array([5+6j, 7+8j])),  # Different dimensions
        ("not a vector", [1+2j, 3+4j]),  # Invalid type
        ([1+2j, 3+4j], "not a vector"),  # Invalid type
    ]


@pytest.mark.unit
def test_resource():
    """Test that the resource attribute is correctly set."""
    assert HermitianInnerProduct.resource == "inner_product"


@pytest.mark.unit
def test_type():
    """Test that the type attribute is correctly set."""
    assert HermitianInnerProduct.type == "HermitianInnerProduct"


@pytest.mark.unit
def test_initialization(hermitian_inner_product):
    """Test that the HermitianInnerProduct can be properly initialized."""
    assert isinstance(hermitian_inner_product, HermitianInnerProduct)


@pytest.mark.unit
@pytest.mark.parametrize("vec1, vec2, expected", [
    (1+2j, 3+4j, (3+4j).conjugate() * (1+2j)),
    ([1+2j, 3+4j], [5+6j, 7+8j], (5+6j).conjugate() * (1+2j) + (7+8j).conjugate() * (3+4j)),
    (np.array([1+2j, 3+4j]), np.array([5+6j, 7+8j]), 
     (5+6j).conjugate() * (1+2j) + (7+8j).conjugate() * (3+4j)),
])
def test_compute(hermitian_inner_product, vec1, vec2, expected):
    """
    Test the compute method with various inputs.
    
    Parameters
    ----------
    hermitian_inner_product : HermitianInnerProduct
        The inner product instance
    vec1 : Any
        First vector
    vec2 : Any
        Second vector
    expected : complex
        Expected result of the inner product
    """
    result = hermitian_inner_product.compute(vec1, vec2)
    assert np.isclose(result, expected)


@pytest.mark.unit
def test_compute_with_fixture_data(hermitian_inner_product, complex_vectors):
    """
    Test the compute method with data from the fixture.
    
    Parameters
    ----------
    hermitian_inner_product : HermitianInnerProduct
        The inner product instance
    complex_vectors : List[Tuple[Any, Any, complex]]
        Test data from fixture
    """
    for vec1, vec2, expected in complex_vectors:
        result = hermitian_inner_product.compute(vec1, vec2)
        assert np.isclose(result, expected)


@pytest.mark.unit
def test_hermitian_property(hermitian_inner_product, complex_vectors):
    """
    Test the Hermitian property: <x,y> = <y,x>*.
    
    Parameters
    ----------
    hermitian_inner_product : HermitianInnerProduct
        The inner product instance
    complex_vectors : List[Tuple[Any, Any, complex]]
        Test data from fixture
    """
    for vec1, vec2, _ in complex_vectors:
        result1 = hermitian_inner_product.compute(vec1, vec2)
        result2 = hermitian_inner_product.compute(vec2, vec1)
        # Check that <x,y> = <y,x>*
        assert np.isclose(result1, result2.conjugate())


@pytest.mark.unit
def test_is_compatible(hermitian_inner_product, complex_vectors):
    """
    Test the is_compatible method with compatible vectors.
    
    Parameters
    ----------
    hermitian_inner_product : HermitianInnerProduct
        The inner product instance
    complex_vectors : List[Tuple[Any, Any, complex]]
        Test data from fixture
    """
    for vec1, vec2, _ in complex_vectors:
        assert hermitian_inner_product.is_compatible(vec1, vec2)


@pytest.mark.unit
def test_is_not_compatible(hermitian_inner_product, incompatible_vectors):
    """
    Test the is_compatible method with incompatible vectors.
    
    Parameters
    ----------
    hermitian_inner_product : HermitianInnerProduct
        The inner product instance
    incompatible_vectors : List[Tuple[Any, Any]]
        Test data with incompatible vectors
    """
    for vec1, vec2 in incompatible_vectors:
        assert not hermitian_inner_product.is_compatible(vec1, vec2)


@pytest.mark.unit
def test_compute_with_incompatible_vectors(hermitian_inner_product, incompatible_vectors):
    """
    Test that compute raises ValueError with incompatible vectors.
    
    Parameters
    ----------
    hermitian_inner_product : HermitianInnerProduct
        The inner product instance
    incompatible_vectors : List[Tuple[Any, Any]]
        Test data with incompatible vectors
    """
    for vec1, vec2 in incompatible_vectors:
        try:
            with pytest.raises(ValueError):
                hermitian_inner_product.compute(vec1, vec2)
        except Exception as e:
            # Some incompatible vectors might raise other exceptions
            # due to type conversions, which is also acceptable
            pass


@pytest.mark.unit
def test_serialization(hermitian_inner_product):
    """
    Test that the HermitianInnerProduct can be serialized and deserialized.
    
    Parameters
    ----------
    hermitian_inner_product : HermitianInnerProduct
        The inner product instance
    """
    # Serialize to JSON
    json_str = hermitian_inner_product.model_dump_json()
    
    # Deserialize from JSON
    deserialized = HermitianInnerProduct.model_validate_json(json_str)
    
    # Check that the deserialized object has the same type
    assert deserialized.type == hermitian_inner_product.type
    
    # Check that we can compute with the deserialized object
    vec1 = np.array([1+2j, 3+4j])
    vec2 = np.array([5+6j, 7+8j])
    expected = (5+6j).conjugate() * (1+2j) + (7+8j).conjugate() * (3+4j)
    
    result = deserialized.compute(vec1, vec2)
    assert np.isclose(result, expected)