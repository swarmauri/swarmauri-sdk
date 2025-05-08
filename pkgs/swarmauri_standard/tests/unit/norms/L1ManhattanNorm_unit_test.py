import pytest
import numpy as np
import logging
from typing import Any, List, Tuple, Union
from swarmauri_standard.norms.L1ManhattanNorm import L1ManhattanNorm

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
def l1_norm() -> L1ManhattanNorm:
    """
    Fixture that provides an instance of L1ManhattanNorm for testing.
    
    Returns
    -------
    L1ManhattanNorm
        An instance of the L1ManhattanNorm class
    """
    return L1ManhattanNorm()

@pytest.mark.unit
def test_resource(l1_norm: L1ManhattanNorm) -> None:
    """
    Test that the resource attribute is set correctly.
    
    Parameters
    ----------
    l1_norm : L1ManhattanNorm
        The L1ManhattanNorm instance to test
    """
    assert l1_norm.resource == "norm"

@pytest.mark.unit
def test_type(l1_norm: L1ManhattanNorm) -> None:
    """
    Test that the type attribute is set correctly.
    
    Parameters
    ----------
    l1_norm : L1ManhattanNorm
        The L1ManhattanNorm instance to test
    """
    assert l1_norm.type == "L1ManhattanNorm"

@pytest.mark.unit
def test_name(l1_norm: L1ManhattanNorm) -> None:
    """
    Test that the name method returns the correct value.
    
    Parameters
    ----------
    l1_norm : L1ManhattanNorm
        The L1ManhattanNorm instance to test
    """
    assert l1_norm.name() == "L1ManhattanNorm"

@pytest.mark.unit
@pytest.mark.parametrize("vector, expected", [
    ([1, 1, 1], 3.0),
    ([1, 2, 3], 6.0),
    ([-1, -2, -3], 6.0),
    ([0, 0, 0], 0.0),
    (np.array([1, 2, 3]), 6.0),
    (np.array([[1], [2], [3]]), 6.0),
    ((1, 2, 3), 6.0),
])
def test_compute(l1_norm: L1ManhattanNorm, vector: Union[List, np.ndarray, Tuple], expected: float) -> None:
    """
    Test the compute method with various input vectors.
    
    Parameters
    ----------
    l1_norm : L1ManhattanNorm
        The L1ManhattanNorm instance to test
    vector : Union[List, np.ndarray, Tuple]
        The input vector
    expected : float
        The expected L1 norm value
    """
    result = l1_norm.compute(vector)
    assert isinstance(result, float)
    assert result == pytest.approx(expected)

@pytest.mark.unit
def test_compute_invalid_input(l1_norm: L1ManhattanNorm) -> None:
    """
    Test that compute method raises appropriate exceptions for invalid inputs.
    
    Parameters
    ----------
    l1_norm : L1ManhattanNorm
        The L1ManhattanNorm instance to test
    """
    # Test with non-vector input
    with pytest.raises(ValueError):
        l1_norm.compute(np.ones((2, 2, 2)))  # 3D array
    
    # Test with non-numeric input
    with pytest.raises(TypeError):
        l1_norm.compute(["a", "b", "c"])

@pytest.mark.unit
@pytest.mark.parametrize("vector_x, vector_y, expected", [
    ([1, 1, 1], [1, 1, 1], 0.0),
    ([1, 2, 3], [4, 5, 6], 9.0),
    ([0, 0, 0], [1, 1, 1], 3.0),
    (np.array([1, 2, 3]), np.array([4, 5, 6]), 9.0),
    (np.array([[1], [2], [3]]), np.array([[4], [5], [6]]), 9.0),
    ((1, 2, 3), (4, 5, 6), 9.0),
])
def test_distance(l1_norm: L1ManhattanNorm, vector_x: Union[List, np.ndarray, Tuple], 
                 vector_y: Union[List, np.ndarray, Tuple], expected: float) -> None:
    """
    Test the distance method with various input vectors.
    
    Parameters
    ----------
    l1_norm : L1ManhattanNorm
        The L1ManhattanNorm instance to test
    vector_x : Union[List, np.ndarray, Tuple]
        The first input vector
    vector_y : Union[List, np.ndarray, Tuple]
        The second input vector
    expected : float
        The expected L1 distance value
    """
    result = l1_norm.distance(vector_x, vector_y)
    assert isinstance(result, float)
    assert result == pytest.approx(expected)

@pytest.mark.unit
def test_distance_invalid_input(l1_norm: L1ManhattanNorm) -> None:
    """
    Test that distance method raises appropriate exceptions for invalid inputs.
    
    Parameters
    ----------
    l1_norm : L1ManhattanNorm
        The L1ManhattanNorm instance to test
    """
    # Test with incompatible dimensions
    with pytest.raises(ValueError):
        l1_norm.distance([1, 2, 3], [1, 2])
    
    # Test with non-vector inputs
    with pytest.raises(ValueError):
        l1_norm.distance(np.ones((2, 2)), [1, 2, 3, 4])
    
    # Test with non-numeric inputs
    with pytest.raises(TypeError):
        l1_norm.distance(["a", "b"], [1, 2])

@pytest.mark.unit
@pytest.mark.parametrize("vector, expected", [
    ([3, 3, 3], [1/3, 1/3, 1/3]),
    ([1, 2, 3], [1/6, 2/6, 3/6]),
    ([-1, -2, -3], [-1/6, -2/6, -3/6]),
    (np.array([1, 2, 3]), np.array([1/6, 2/6, 3/6])),
    ((1, 2, 3), (1/6, 2/6, 3/6)),
])
def test_normalize(l1_norm: L1ManhattanNorm, vector: Union[List, np.ndarray, Tuple], 
                  expected: Union[List, np.ndarray, Tuple]) -> None:
    """
    Test the normalize method with various input vectors.
    
    Parameters
    ----------
    l1_norm : L1ManhattanNorm
        The L1ManhattanNorm instance to test
    vector : Union[List, np.ndarray, Tuple]
        The input vector to normalize
    expected : Union[List, np.ndarray, Tuple]
        The expected normalized vector
    """
    result = l1_norm.normalize(vector)
    
    # Convert result to numpy array for comparison
    if not isinstance(result, np.ndarray):
        result_array = np.array(result)
    else:
        result_array = result
    
    # Convert expected to numpy array for comparison
    if not isinstance(expected, np.ndarray):
        expected_array = np.array(expected)
    else:
        expected_array = expected
    
    # Check that the result has unit L1 norm
    assert l1_norm.compute(result) == pytest.approx(1.0)
    
    # Check that the normalized vector matches the expected result
    assert np.allclose(result_array, expected_array)
    
    # Check that the return type matches the input type
    assert type(result) == type(vector) or (isinstance(result, np.ndarray) and isinstance(vector, (list, tuple)))

@pytest.mark.unit
def test_normalize_zero_vector(l1_norm: L1ManhattanNorm) -> None:
    """
    Test that normalize method raises an exception for a zero vector.
    
    Parameters
    ----------
    l1_norm : L1ManhattanNorm
        The L1ManhattanNorm instance to test
    """
    with pytest.raises(ValueError, match="Cannot normalize a zero vector"):
        l1_norm.normalize([0, 0, 0])

@pytest.mark.unit
@pytest.mark.parametrize("vector, expected", [
    ([1/3, 1/3, 1/3], True),
    ([1/6, 2/6, 3/6], True),
    ([0.1, 0.2, 0.7], True),
    ([1, 2, 3], False),
    ([0, 0, 0], False),
])
def test_is_normalized(l1_norm: L1ManhattanNorm, vector: Union[List, np.ndarray, Tuple], expected: bool) -> None:
    """
    Test the is_normalized method with various input vectors.
    
    Parameters
    ----------
    l1_norm : L1ManhattanNorm
        The L1ManhattanNorm instance to test
    vector : Union[List, np.ndarray, Tuple]
        The input vector to check
    expected : bool
        Whether the vector is expected to be normalized
    """
    result = l1_norm.is_normalized(vector)
    assert result == expected

@pytest.mark.unit
def test_is_normalized_tolerance(l1_norm: L1ManhattanNorm) -> None:
    """
    Test the is_normalized method with different tolerance values.
    
    Parameters
    ----------
    l1_norm : L1ManhattanNorm
        The L1ManhattanNorm instance to test
    """
    # Vector with L1 norm slightly different from 1.0
    vector = [0.33, 0.33, 0.33]  # Sum is 0.99
    
    # Should be False with small tolerance
    assert not l1_norm.is_normalized(vector, tolerance=1e-10)
    
    # Should be True with larger tolerance
    assert l1_norm.is_normalized(vector, tolerance=0.01)

@pytest.mark.unit
def test_serialization(l1_norm: L1ManhattanNorm) -> None:
    """
    Test serialization and deserialization of the L1ManhattanNorm class.
    
    Parameters
    ----------
    l1_norm : L1ManhattanNorm
        The L1ManhattanNorm instance to test
    """
    # Serialize to JSON
    json_str = l1_norm.model_dump_json()
    
    # Deserialize from JSON
    deserialized = L1ManhattanNorm.model_validate_json(json_str)
    
    # Check that the deserialized object has the same attributes
    assert deserialized.type == l1_norm.type
    assert deserialized.resource == l1_norm.resource