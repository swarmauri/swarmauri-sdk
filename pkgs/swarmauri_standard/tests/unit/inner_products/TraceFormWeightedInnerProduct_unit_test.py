import logging
from typing import Tuple

import numpy as np
import pytest

from swarmauri_standard.inner_products.TraceFormWeightedInnerProduct import (
    TraceFormWeightedInnerProduct,
)

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture
def weight_matrix() -> np.ndarray:
    """
    Fixture providing a default weight matrix for tests.

    Returns
    -------
    np.ndarray
        A 3x3 weight matrix
    """
    return np.array([[2.0, 0.5, 0.0], [0.5, 3.0, 0.0], [0.0, 0.0, 1.0]])


@pytest.fixture
def hermitian_weight_matrix() -> np.ndarray:
    """
    Fixture providing a hermitian weight matrix for tests.

    Returns
    -------
    np.ndarray
        A 3x3 hermitian weight matrix
    """
    return np.array(
        [[2.0, 0.5 + 0.5j, 1.0], [0.5 - 0.5j, 3.0, 0.0], [1.0, 0.0, 1.0]], dtype=complex
    )


@pytest.fixture
def inner_product(weight_matrix) -> TraceFormWeightedInnerProduct:
    """
    Fixture providing a TraceFormWeightedInnerProduct instance.

    Parameters
    ----------
    weight_matrix : np.ndarray
        The weight matrix to use

    Returns
    -------
    TraceFormWeightedInnerProduct
        An initialized inner product calculator
    """
    return TraceFormWeightedInnerProduct(weight_matrix)


@pytest.fixture
def complex_inner_product(hermitian_weight_matrix) -> TraceFormWeightedInnerProduct:
    """
    Fixture providing a TraceFormWeightedInnerProduct instance with complex weights.

    Parameters
    ----------
    hermitian_weight_matrix : np.ndarray
        The hermitian weight matrix to use

    Returns
    -------
    TraceFormWeightedInnerProduct
        An initialized inner product calculator with complex weights
    """
    return TraceFormWeightedInnerProduct(hermitian_weight_matrix)


@pytest.fixture
def matrix_pair() -> Tuple[np.ndarray, np.ndarray]:
    """
    Fixture providing a pair of matrices for testing.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        A pair of 3x2 matrices
    """
    a = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    b = np.array([[0.5, 1.5], [2.5, 3.5], [4.5, 5.5]])
    return a, b


@pytest.mark.unit
def test_initialization_with_weight_matrix(weight_matrix):
    """
    Test initialization with a provided weight matrix.

    Parameters
    ----------
    weight_matrix : np.ndarray
        The weight matrix fixture
    """
    inner_product = TraceFormWeightedInnerProduct(weight_matrix)
    assert np.array_equal(inner_product.weight_matrix, weight_matrix)


@pytest.mark.unit
def test_initialization_without_weight_matrix():
    """Test initialization without providing a weight matrix."""
    inner_product = TraceFormWeightedInnerProduct()
    assert np.array_equal(inner_product.weight_matrix, np.eye(1))


@pytest.mark.unit
def test_resource_type():
    """Test that the resource type is correctly set."""
    inner_product = TraceFormWeightedInnerProduct()
    assert inner_product.resource == "InnerProduct"


@pytest.mark.unit
def test_component_type():
    """Test that the component type is correctly set."""
    inner_product = TraceFormWeightedInnerProduct()
    assert inner_product.type == "TraceFormWeightedInnerProduct"


@pytest.mark.unit
def test_compute(inner_product, matrix_pair):
    """
    Test the compute method for calculating inner products.

    Parameters
    ----------
    inner_product : TraceFormWeightedInnerProduct
        The inner product calculator
    matrix_pair : Tuple[np.ndarray, np.ndarray]
        A pair of test matrices
    """
    a, b = matrix_pair
    # Manually calculate expected result: trace(a.T @ weight_matrix @ b)
    expected = np.trace(a.T @ inner_product.weight_matrix @ b)
    result = inner_product.compute(a, b)

    assert np.isclose(result, expected)
    assert isinstance(result, float)


@pytest.mark.unit
def test_compute_with_incompatible_dimensions(inner_product):
    """
    Test that compute raises an error with incompatible dimensions.

    Parameters
    ----------
    inner_product : TraceFormWeightedInnerProduct
        The inner product calculator
    """
    a = np.array([[1.0, 2.0]])  # 1x2 matrix
    b = np.array([[3.0, 4.0]])  # 1x2 matrix

    # These matrices are incompatible with the 3x3 weight matrix
    with pytest.raises(ValueError, match="Incompatible dimensions"):
        inner_product.compute(a, b)


@pytest.mark.unit
def test_check_conjugate_symmetry_with_hermitian_weight(complex_inner_product):
    """
    Test conjugate symmetry property with a hermitian weight matrix.

    Parameters
    ----------
    complex_inner_product : TraceFormWeightedInnerProduct
        The inner product calculator with a hermitian weight matrix
    """
    a = np.array([[1.0 + 1j, 2.0], [3.0, 4.0 - 2j], [5.0, 6.0]], dtype=complex)
    b = np.array([[0.5, 1.5 + 1j], [2.5 - 1j, 3.5], [4.5, 5.5]], dtype=complex)

    assert complex_inner_product.check_conjugate_symmetry(a, b)


@pytest.mark.unit
def test_check_conjugate_symmetry_with_non_hermitian_weight(inner_product):
    """
    Test conjugate symmetry property with a non-hermitian weight matrix.

    Parameters
    ----------
    inner_product : TraceFormWeightedInnerProduct
        The inner product calculator
    """
    # Modify the weight matrix to be non-hermitian
    non_hermitian_weight = inner_product.weight_matrix.copy()
    non_hermitian_weight[0, 1] = 0.7  # Make it asymmetric
    inner_product.set_weight_matrix(non_hermitian_weight)

    a = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    b = np.array([[0.5, 1.5], [2.5, 3.5], [4.5, 5.5]])

    assert not inner_product.check_conjugate_symmetry(a, b)


@pytest.mark.unit
def test_check_linearity_first_argument(inner_product, matrix_pair):
    """
    Test linearity in the first argument.

    Parameters
    ----------
    inner_product : TraceFormWeightedInnerProduct
        The inner product calculator
    matrix_pair : Tuple[np.ndarray, np.ndarray]
        A pair of test matrices
    """
    a, b = matrix_pair
    c = np.array([[2.0, 3.0], [4.0, 5.0], [6.0, 7.0]])
    alpha = 2.5
    beta = -1.5

    assert inner_product.check_linearity_first_argument(a, c, b, alpha, beta)


@pytest.mark.unit
def test_check_positivity_with_positive_definite_weight(inner_product):
    """
    Test positivity property with a positive definite weight matrix.

    Parameters
    ----------
    inner_product : TraceFormWeightedInnerProduct
        The inner product calculator
    """
    # The default weight matrix is positive definite
    a = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])

    assert inner_product.check_positivity(a)


@pytest.mark.unit
def test_check_positivity_with_non_positive_definite_weight():
    """Test positivity property with a non-positive definite weight matrix."""
    # Create a non-positive definite weight matrix
    non_psd_weight = np.array([[-1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])

    inner_product = TraceFormWeightedInnerProduct(non_psd_weight)
    a = np.array([[1.0, 0.0], [0.0, 0.0], [0.0, 0.0]])

    assert not inner_product.check_positivity(a)


@pytest.mark.unit
def test_check_positivity_with_zero_matrix(inner_product):
    """
    Test positivity property with a zero matrix.

    Parameters
    ----------
    inner_product : TraceFormWeightedInnerProduct
        The inner product calculator
    """
    a = np.zeros((3, 2))

    assert inner_product.check_positivity(a)


@pytest.mark.unit
def test_set_and_get_weight_matrix(inner_product):
    """
    Test setting and getting the weight matrix.

    Parameters
    ----------
    inner_product : TraceFormWeightedInnerProduct
        The inner product calculator
    """
    new_weight = np.array([[4.0, 1.0, 0.0], [1.0, 5.0, 0.0], [0.0, 0.0, 6.0]])

    inner_product.set_weight_matrix(new_weight)
    retrieved_weight = inner_product.get_weight_matrix()

    assert np.array_equal(retrieved_weight, new_weight)


@pytest.mark.unit
def test_serialization():
    """Test serialization and deserialization of the inner product."""
    weight_matrix = np.array([[2.0, 0.5, 0.0], [0.5, 3.0, 0.0], [0.0, 0.0, 1.0]])

    inner_product = TraceFormWeightedInnerProduct(weight_matrix)
    serialized = inner_product.model_dump_json()
    deserialized = TraceFormWeightedInnerProduct.model_validate_json(serialized)

    assert np.array_equal(inner_product.weight_matrix, deserialized.weight_matrix)
    assert inner_product.type == deserialized.type
    assert inner_product.resource == deserialized.resource


@pytest.mark.unit
@pytest.mark.parametrize(
    "alpha,beta", [(1.0, 1.0), (2.5, -1.5), (0.0, 3.0), (-2.0, -2.0)]
)
def test_linearity_with_different_coefficients(inner_product, matrix_pair, alpha, beta):
    """
    Test linearity with different coefficient values.

    Parameters
    ----------
    inner_product : TraceFormWeightedInnerProduct
        The inner product calculator
    matrix_pair : Tuple[np.ndarray, np.ndarray]
        A pair of test matrices
    alpha : float
        First coefficient for linearity test
    beta : float
        Second coefficient for linearity test
    """
    a, b = matrix_pair
    c = np.array([[2.0, 3.0], [4.0, 5.0], [6.0, 7.0]])

    assert inner_product.check_linearity_first_argument(a, c, b, alpha, beta)
