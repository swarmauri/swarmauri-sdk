import logging
import pytest
import numpy as np
from typing import Optional

from swarmauri_standard.inner_products.TraceFormWeighted import TraceFormWeighted


@pytest.fixture
def weight_matrix() -> np.ndarray:
    """
    Create a sample weight matrix for testing.
    
    Returns
    -------
    np.ndarray
        A 3x3 weight matrix
    """
    return np.array([[2.0, 0.0, 0.0], [0.0, 3.0, 0.0], [0.0, 0.0, 4.0]])


@pytest.fixture
def trace_form_weighted(weight_matrix: np.ndarray) -> TraceFormWeighted:
    """
    Create a TraceFormWeighted instance with a weight matrix.
    
    Parameters
    ----------
    weight_matrix : np.ndarray
        The weight matrix to use
        
    Returns
    -------
    TraceFormWeighted
        An initialized TraceFormWeighted instance
    """
    return TraceFormWeighted(weight_matrix=weight_matrix)


@pytest.fixture
def trace_form_unweighted() -> TraceFormWeighted:
    """
    Create a TraceFormWeighted instance without a weight matrix.
    
    Returns
    -------
    TraceFormWeighted
        An initialized TraceFormWeighted instance with no weight matrix
    """
    return TraceFormWeighted()


@pytest.mark.unit
def test_initialization() -> None:
    """Test the initialization of TraceFormWeighted."""
    # Test with no weight matrix
    inner_product = TraceFormWeighted()
    assert inner_product.type == "TraceFormWeighted"
    assert inner_product.weight_matrix is None
    
    # Test with a weight matrix
    weight_matrix = np.eye(3)
    inner_product = TraceFormWeighted(weight_matrix=weight_matrix)
    assert inner_product.type == "TraceFormWeighted"
    assert np.array_equal(inner_product.weight_matrix, weight_matrix)


@pytest.mark.unit
def test_resource() -> None:
    """Test the resource attribute of TraceFormWeighted."""
    inner_product = TraceFormWeighted()
    assert inner_product.resource == "inner_product"


@pytest.mark.unit
def test_type() -> None:
    """Test the type attribute of TraceFormWeighted."""
    inner_product = TraceFormWeighted()
    assert inner_product.type == "TraceFormWeighted"


@pytest.mark.unit
def test_serialization() -> None:
    """Test serialization and deserialization of TraceFormWeighted."""
    # Test with no weight matrix
    inner_product = TraceFormWeighted()
    serialized = inner_product.model_dump_json()
    deserialized = TraceFormWeighted.model_validate_json(serialized)
    assert deserialized.weight_matrix is None
    
    # Test with a weight matrix
    weight_matrix = np.array([[1.0, 0.0], [0.0, 2.0]])
    inner_product = TraceFormWeighted(weight_matrix=weight_matrix)
    serialized = inner_product.model_dump_json()
    deserialized = TraceFormWeighted.model_validate_json(serialized)
    assert np.array_equal(deserialized.weight_matrix, weight_matrix)


@pytest.mark.unit
def test_compute_unweighted(trace_form_unweighted: TraceFormWeighted) -> None:
    """
    Test the compute method with no weight matrix.
    
    Parameters
    ----------
    trace_form_unweighted : TraceFormWeighted
        TraceFormWeighted instance with no weight matrix
    """
    # For unweighted case, should be equivalent to trace(A @ B.T)
    A = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    B = np.array([[2.0, 3.0, 4.0], [5.0, 6.0, 7.0]])
    
    # Manual calculation: trace(A @ B.T)
    expected = np.trace(A @ B.T)
    result = trace_form_unweighted.compute(A, B)
    
    assert np.isclose(result, expected)
    assert np.isclose(result, 91.0)  # Verify with known value


@pytest.mark.unit
def test_compute_weighted(trace_form_weighted: TraceFormWeighted) -> None:
    """
    Test the compute method with a weight matrix.
    
    Parameters
    ----------
    trace_form_weighted : TraceFormWeighted
        TraceFormWeighted instance with a weight matrix
    """
    A = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    B = np.array([[2.0, 3.0, 4.0], [5.0, 6.0, 7.0]])
    
    # Manual calculation: trace(A @ W @ B.T)
    W = trace_form_weighted.weight_matrix
    expected = np.trace(A @ W @ B.T)
    result = trace_form_weighted.compute(A, B)
    
    assert np.isclose(result, expected)


@pytest.mark.unit
@pytest.mark.parametrize("vec1,vec2,expected", [
    (np.array([[1.0, 2.0], [3.0, 4.0]]), np.array([[1.0, 2.0], [3.0, 4.0]]), True),  # Compatible matrices
    (np.array([[1.0, 2.0]]), np.array([[1.0, 2.0], [3.0, 4.0]]), False),  # Different shapes
    (np.array([1.0, 2.0]), np.array([1.0, 2.0]), False),  # Not 2D
    ("not an array", np.array([[1.0, 2.0]]), False),  # Not numpy arrays
    (np.array([[1.0, 2.0]]), "not an array", False),  # Not numpy arrays
])
def test_is_compatible_without_weight(
    trace_form_unweighted: TraceFormWeighted,
    vec1: np.ndarray,
    vec2: np.ndarray,
    expected: bool
) -> None:
    """
    Test the is_compatible method with various inputs without weight matrix.
    
    Parameters
    ----------
    trace_form_unweighted : TraceFormWeighted
        TraceFormWeighted instance with no weight matrix
    vec1 : np.ndarray
        First input to check compatibility
    vec2 : np.ndarray
        Second input to check compatibility
    expected : bool
        Expected compatibility result
    """
    result = trace_form_unweighted.is_compatible(vec1, vec2)
    assert result == expected


@pytest.mark.unit
def test_is_compatible_with_weight(trace_form_weighted: TraceFormWeighted) -> None:
    """
    Test the is_compatible method with a weight matrix.
    
    Parameters
    ----------
    trace_form_weighted : TraceFormWeighted
        TraceFormWeighted instance with a weight matrix
    """
    # Compatible case
    A = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    B = np.array([[2.0, 3.0, 4.0], [5.0, 6.0, 7.0]])
    assert trace_form_weighted.is_compatible(A, B)
    
    # Incompatible case - wrong dimensions for weight matrix
    C = np.array([[1.0, 2.0], [3.0, 4.0]])
    assert not trace_form_weighted.is_compatible(C, C)


@pytest.mark.unit
def test_set_weight_matrix() -> None:
    """Test setting and updating the weight matrix."""
    inner_product = TraceFormWeighted()
    assert inner_product.weight_matrix is None
    
    # Set weight matrix
    weight_matrix = np.array([[1.0, 0.0], [0.0, 2.0]])
    inner_product.set_weight_matrix(weight_matrix)
    assert np.array_equal(inner_product.weight_matrix, weight_matrix)
    
    # Update weight matrix
    new_weight_matrix = np.array([[3.0, 0.0], [0.0, 4.0]])
    inner_product.set_weight_matrix(new_weight_matrix)
    assert np.array_equal(inner_product.weight_matrix, new_weight_matrix)


@pytest.mark.unit
def test_set_weight_matrix_errors() -> None:
    """Test error handling when setting an invalid weight matrix."""
    inner_product = TraceFormWeighted()
    
    # Test with non-numpy array
    with pytest.raises(TypeError):
        inner_product.set_weight_matrix("not an array")
    
    # Test with 1D array
    with pytest.raises(ValueError):
        inner_product.set_weight_matrix(np.array([1.0, 2.0]))


@pytest.mark.unit
def test_get_weight_matrix(weight_matrix: np.ndarray) -> None:
    """
    Test getting the weight matrix.
    
    Parameters
    ----------
    weight_matrix : np.ndarray
        The weight matrix to use
    """
    # Test with no weight matrix
    inner_product = TraceFormWeighted()
    assert inner_product.get_weight_matrix() is None
    
    # Test with a weight matrix
    inner_product = TraceFormWeighted(weight_matrix=weight_matrix)
    retrieved_matrix = inner_product.get_weight_matrix()
    assert np.array_equal(retrieved_matrix, weight_matrix)


@pytest.mark.unit
def test_compute_error_handling(trace_form_weighted: TraceFormWeighted) -> None:
    """
    Test error handling in the compute method.
    
    Parameters
    ----------
    trace_form_weighted : TraceFormWeighted
        TraceFormWeighted instance with a weight matrix
    """
    # Test with incompatible matrices
    A = np.array([[1.0, 2.0]])
    B = np.array([[1.0, 2.0, 3.0]])
    
    with pytest.raises(ValueError):
        trace_form_weighted.compute(A, B)
    
    # Test with non-numpy arrays
    with pytest.raises(ValueError):
        trace_form_weighted.compute("not an array", B)


@pytest.mark.unit
def test_special_cases(trace_form_unweighted: TraceFormWeighted) -> None:
    """
    Test special cases for the compute method.
    
    Parameters
    ----------
    trace_form_unweighted : TraceFormWeighted
        TraceFormWeighted instance with no weight matrix
    """
    # Test with zero matrices
    A = np.zeros((2, 3))
    B = np.zeros((2, 3))
    result = trace_form_unweighted.compute(A, B)
    assert np.isclose(result, 0.0)
    
    # Test with identity matrices
    A = np.eye(3)
    B = np.eye(3)
    result = trace_form_unweighted.compute(A, B)
    assert np.isclose(result, 3.0)  # Trace of 3x3 identity matrix