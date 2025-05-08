import logging
import pytest
import numpy as np
from typing import Any, List, Tuple

from swarmauri_standard.seminorms.TraceSeminorm import TraceSeminorm

# Set up logging
logger = logging.getLogger(__name__)

@pytest.fixture
def trace_seminorm() -> TraceSeminorm:
    """
    Fixture that provides a TraceSeminorm instance.
    
    Returns
    -------
    TraceSeminorm
        An instance of the TraceSeminorm class.
    """
    return TraceSeminorm()

@pytest.mark.unit
def test_initialization() -> None:
    """Test that TraceSeminorm initializes correctly."""
    seminorm = TraceSeminorm()
    assert seminorm.type == "TraceSeminorm"
    assert seminorm.resource == "Seminorm"

@pytest.mark.unit
def test_type_attribute() -> None:
    """Test that the type attribute is correctly set."""
    seminorm = TraceSeminorm()
    assert seminorm.type == "TraceSeminorm"
    
@pytest.mark.unit
def test_serialization(trace_seminorm: TraceSeminorm) -> None:
    """
    Test that TraceSeminorm can be serialized and deserialized correctly.
    
    Parameters
    ----------
    trace_seminorm : TraceSeminorm
        The trace seminorm fixture.
    """
    json_data = trace_seminorm.model_dump_json()
    deserialized = TraceSeminorm.model_validate_json(json_data)
    assert deserialized.type == trace_seminorm.type
    assert deserialized.resource == trace_seminorm.resource

@pytest.mark.unit
@pytest.mark.parametrize("matrix, expected", [
    (np.array([[1, 0], [0, 1]]), 2.0),  # Identity matrix, trace = 2
    (np.array([[3, 1], [2, 5]]), 8.0),  # Random matrix, trace = 8
    (np.array([[0, 1], [1, 0]]), 0.0),  # Off-diagonal matrix, trace = 0
    (np.array([[-2, 0], [0, -3]]), 5.0),  # Negative diagonal, trace = -5, abs(trace) = 5
    (np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), 15.0),  # 3x3 matrix, trace = 15
])
def test_evaluate(trace_seminorm: TraceSeminorm, matrix: np.ndarray, expected: float) -> None:
    """
    Test the evaluate method with various matrices.
    
    Parameters
    ----------
    trace_seminorm : TraceSeminorm
        The trace seminorm fixture.
    matrix : np.ndarray
        The input matrix to evaluate.
    expected : float
        The expected result of the seminorm evaluation.
    """
    result = trace_seminorm.evaluate(matrix)
    assert np.isclose(result, expected)

@pytest.mark.unit
def test_evaluate_non_square_matrix(trace_seminorm: TraceSeminorm) -> None:
    """
    Test that evaluate raises ValueError for non-square matrices.
    
    Parameters
    ----------
    trace_seminorm : TraceSeminorm
        The trace seminorm fixture.
    """
    non_square_matrix = np.array([[1, 2, 3], [4, 5, 6]])
    with pytest.raises(ValueError, match="Input must be a square matrix"):
        trace_seminorm.evaluate(non_square_matrix)

@pytest.mark.unit
@pytest.mark.parametrize("matrix, alpha, expected", [
    (np.array([[1, 0], [0, 1]]), 2.0, 4.0),  # Identity matrix, trace = 2, scaled by 2
    (np.array([[3, 1], [2, 5]]), -1.0, 8.0),  # Random matrix, trace = 8, scaled by -1
    (np.array([[0, 1], [1, 0]]), 5.0, 0.0),  # Off-diagonal matrix, trace = 0, scaled by 5
])
def test_scale(trace_seminorm: TraceSeminorm, matrix: np.ndarray, alpha: float, expected: float) -> None:
    """
    Test the scale method with various matrices and scaling factors.
    
    Parameters
    ----------
    trace_seminorm : TraceSeminorm
        The trace seminorm fixture.
    matrix : np.ndarray
        The input matrix to scale.
    alpha : float
        The scaling factor.
    expected : float
        The expected result of the scaled seminorm.
    """
    result = trace_seminorm.scale(matrix, alpha)
    assert np.isclose(result, expected)

@pytest.mark.unit
@pytest.mark.parametrize("matrix_x, matrix_y", [
    (np.array([[1, 0], [0, 1]]), np.array([[2, 1], [1, 3]])),
    (np.array([[3, 1], [2, 5]]), np.array([[1, 2], [2, 1]])),
    (np.array([[0, 1], [1, 0]]), np.array([[0, -1], [-1, 0]])),
])
def test_triangle_inequality(trace_seminorm: TraceSeminorm, matrix_x: np.ndarray, matrix_y: np.ndarray) -> None:
    """
    Test that the triangle inequality holds for the trace seminorm.
    
    Parameters
    ----------
    trace_seminorm : TraceSeminorm
        The trace seminorm fixture.
    matrix_x : np.ndarray
        The first input matrix.
    matrix_y : np.ndarray
        The second input matrix.
    """
    # Triangle inequality: p(x + y) <= p(x) + p(y)
    assert trace_seminorm.triangle_inequality(matrix_x, matrix_y)
    
    # Manually verify
    sum_norm = trace_seminorm.evaluate(matrix_x + matrix_y)
    individual_norms_sum = trace_seminorm.evaluate(matrix_x) + trace_seminorm.evaluate(matrix_y)
    assert sum_norm <= individual_norms_sum + 1e-10  # Adding small tolerance

@pytest.mark.unit
def test_triangle_inequality_mismatched_dimensions(trace_seminorm: TraceSeminorm) -> None:
    """
    Test that triangle_inequality raises ValueError for matrices with mismatched dimensions.
    
    Parameters
    ----------
    trace_seminorm : TraceSeminorm
        The trace seminorm fixture.
    """
    matrix_x = np.array([[1, 0], [0, 1]])
    matrix_y = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    
    with pytest.raises(ValueError, match="Matrices must have the same dimensions"):
        trace_seminorm.triangle_inequality(matrix_x, matrix_y)

@pytest.mark.unit
@pytest.mark.parametrize("matrix, tolerance, expected", [
    (np.array([[0, 0], [0, 0]]), 1e-10, True),  # Zero matrix
    (np.array([[0, 1], [1, 0]]), 1e-10, True),  # Trace-zero matrix
    (np.array([[1e-11, 0], [0, 0]]), 1e-10, True),  # Almost zero trace
    (np.array([[1, 0], [0, 1]]), 1e-10, False),  # Non-zero trace
])
def test_is_zero(trace_seminorm: TraceSeminorm, matrix: np.ndarray, tolerance: float, expected: bool) -> None:
    """
    Test the is_zero method with various matrices.
    
    Parameters
    ----------
    trace_seminorm : TraceSeminorm
        The trace seminorm fixture.
    matrix : np.ndarray
        The input matrix to check.
    tolerance : float
        The tolerance for considering a value as zero.
    expected : bool
        The expected result of the is_zero check.
    """
    result = trace_seminorm.is_zero(matrix, tolerance)
    assert result == expected

@pytest.mark.unit
def test_is_definite(trace_seminorm: TraceSeminorm) -> None:
    """
    Test that the trace seminorm is not definite.
    
    Parameters
    ----------
    trace_seminorm : TraceSeminorm
        The trace seminorm fixture.
    """
    # The trace seminorm is not definite because there are non-zero matrices with trace zero
    assert not trace_seminorm.is_definite()
    
    # Verify with a concrete example: a traceless matrix
    traceless_matrix = np.array([[0, 1], [1, 0]])
    assert not np.array_equal(traceless_matrix, np.zeros_like(traceless_matrix))  # Matrix is not zero
    assert trace_seminorm.evaluate(traceless_matrix) == 0  # But its seminorm is zero