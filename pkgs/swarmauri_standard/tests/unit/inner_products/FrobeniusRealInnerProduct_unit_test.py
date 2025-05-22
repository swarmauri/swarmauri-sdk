import logging
from typing import Tuple

import numpy as np
import pytest
from numpy.typing import NDArray

from swarmauri_standard.inner_products.FrobeniusRealInnerProduct import (
    FrobeniusRealInnerProduct,
)

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture
def frobenius_inner_product() -> FrobeniusRealInnerProduct:
    """
    Fixture that provides a FrobeniusRealInnerProduct instance.

    Returns
    -------
    FrobeniusRealInnerProduct
        An instance of the FrobeniusRealInnerProduct class
    """
    return FrobeniusRealInnerProduct()


@pytest.fixture
def sample_matrices() -> Tuple[NDArray, NDArray]:
    """
    Fixture that provides sample matrices for testing.

    Returns
    -------
    Tuple[NDArray, NDArray]
        A tuple containing two sample matrices
    """
    a = np.array([[1.0, 2.0], [3.0, 4.0]])
    b = np.array([[5.0, 6.0], [7.0, 8.0]])
    return a, b


@pytest.mark.unit
def test_type(frobenius_inner_product: FrobeniusRealInnerProduct) -> None:
    """
    Test that the type attribute is correctly set.

    Parameters
    ----------
    frobenius_inner_product : FrobeniusRealInnerProduct
        The FrobeniusRealInnerProduct instance to test
    """
    assert frobenius_inner_product.type == "FrobeniusRealInnerProduct"


@pytest.mark.unit
def test_compute_basic(
    frobenius_inner_product: FrobeniusRealInnerProduct,
    sample_matrices: Tuple[NDArray, NDArray],
) -> None:
    """
    Test basic computation of the Frobenius inner product.

    Parameters
    ----------
    frobenius_inner_product : FrobeniusRealInnerProduct
        The FrobeniusRealInnerProduct instance to test
    sample_matrices : Tuple[NDArray, NDArray]
        Sample matrices for testing
    """
    a, b = sample_matrices

    # Expected result: sum of element-wise products
    expected = np.sum(a * b)  # 1*5 + 2*6 + 3*7 + 4*8 = 5 + 12 + 21 + 32 = 70
    result = frobenius_inner_product.compute(a, b)

    assert isinstance(result, float)
    assert result == pytest.approx(expected)


@pytest.mark.unit
def test_compute_identity_matrices(
    frobenius_inner_product: FrobeniusRealInnerProduct,
) -> None:
    """
    Test computation with identity matrices.

    Parameters
    ----------
    frobenius_inner_product : FrobeniusRealInnerProduct
        The FrobeniusRealInnerProduct instance to test
    """
    a = np.eye(3)
    b = np.eye(3)

    # For identity matrices, the result should be the trace
    expected = np.trace(a @ b)  # Should be 3.0
    result = frobenius_inner_product.compute(a, b)

    assert result == pytest.approx(expected)


@pytest.mark.unit
def test_compute_zero_matrices(
    frobenius_inner_product: FrobeniusRealInnerProduct,
) -> None:
    """
    Test computation with zero matrices.

    Parameters
    ----------
    frobenius_inner_product : FrobeniusRealInnerProduct
        The FrobeniusRealInnerProduct instance to test
    """
    a = np.zeros((2, 2))
    b = np.zeros((2, 2))

    result = frobenius_inner_product.compute(a, b)

    assert result == 0.0


@pytest.mark.unit
@pytest.mark.parametrize("shape", [(3, 3), (2, 4), (4, 2), (1, 5)])
def test_compute_different_shapes(
    frobenius_inner_product: FrobeniusRealInnerProduct, shape: Tuple[int, int]
) -> None:
    """
    Test computation with matrices of different shapes.

    Parameters
    ----------
    frobenius_inner_product : FrobeniusRealInnerProduct
        The FrobeniusRealInnerProduct instance to test
    shape : Tuple[int, int]
        The shape to use for test matrices
    """
    a = np.ones(shape)
    b = np.ones(shape) * 2

    # Expected: number of elements * 1 * 2
    expected = np.prod(shape) * 2
    result = frobenius_inner_product.compute(a, b)

    assert result == pytest.approx(expected)


@pytest.mark.unit
def test_compute_mismatched_shapes(
    frobenius_inner_product: FrobeniusRealInnerProduct,
) -> None:
    """
    Test that computation with mismatched shapes raises ValueError.

    Parameters
    ----------
    frobenius_inner_product : FrobeniusRealInnerProduct
        The FrobeniusRealInnerProduct instance to test
    """
    a = np.ones((2, 3))
    b = np.ones((3, 2))

    with pytest.raises(ValueError, match="Matrix shapes must match"):
        frobenius_inner_product.compute(a, b)


@pytest.mark.unit
def test_compute_complex_matrices(
    frobenius_inner_product: FrobeniusRealInnerProduct,
) -> None:
    """
    Test that computation with complex matrices raises ValueError.

    Parameters
    ----------
    frobenius_inner_product : FrobeniusRealInnerProduct
        The FrobeniusRealInnerProduct instance to test
    """
    a = np.array([[1 + 1j, 2], [3, 4]])
    b = np.array([[5, 6], [7, 8]])

    with pytest.raises(ValueError, match="only supports real-valued matrices"):
        frobenius_inner_product.compute(a, b)


@pytest.mark.unit
def test_check_conjugate_symmetry(
    frobenius_inner_product: FrobeniusRealInnerProduct,
    sample_matrices: Tuple[NDArray, NDArray],
) -> None:
    """
    Test the conjugate symmetry property.

    Parameters
    ----------
    frobenius_inner_product : FrobeniusRealInnerProduct
        The FrobeniusRealInnerProduct instance to test
    sample_matrices : Tuple[NDArray, NDArray]
        Sample matrices for testing
    """
    a, b = sample_matrices

    # For real matrices, conjugate symmetry means <a,b> = <b,a>
    result = frobenius_inner_product.check_conjugate_symmetry(a, b)

    assert result is True


@pytest.mark.unit
def test_check_linearity_first_argument(
    frobenius_inner_product: FrobeniusRealInnerProduct,
) -> None:
    """
    Test linearity in the first argument.

    Parameters
    ----------
    frobenius_inner_product : FrobeniusRealInnerProduct
        The FrobeniusRealInnerProduct instance to test
    """
    a1 = np.array([[1.0, 2.0], [3.0, 4.0]])
    a2 = np.array([[5.0, 6.0], [7.0, 8.0]])
    b = np.array([[9.0, 10.0], [11.0, 12.0]])
    alpha = 2.0
    beta = 3.0

    result = frobenius_inner_product.check_linearity_first_argument(
        a1, a2, b, alpha, beta
    )

    assert result is True


@pytest.mark.unit
def test_check_linearity_with_mismatched_shapes(
    frobenius_inner_product: FrobeniusRealInnerProduct,
) -> None:
    """
    Test that linearity check with mismatched shapes raises ValueError.

    Parameters
    ----------
    frobenius_inner_product : FrobeniusRealInnerProduct
        The FrobeniusRealInnerProduct instance to test
    """
    a1 = np.array([[1.0, 2.0], [3.0, 4.0]])
    a2 = np.array([[5.0, 6.0, 7.0], [8.0, 9.0, 10.0]])
    b = np.array([[11.0, 12.0], [13.0, 14.0]])

    with pytest.raises(ValueError, match="All matrices must have the same shape"):
        frobenius_inner_product.check_linearity_first_argument(a1, a2, b, 1.0, 1.0)


@pytest.mark.unit
def test_check_positivity_positive_matrix(
    frobenius_inner_product: FrobeniusRealInnerProduct,
) -> None:
    """
    Test positivity with a non-zero matrix.

    Parameters
    ----------
    frobenius_inner_product : FrobeniusRealInnerProduct
        The FrobeniusRealInnerProduct instance to test
    """
    a = np.array([[1.0, 2.0], [3.0, 4.0]])

    result = frobenius_inner_product.check_positivity(a)

    assert result is True


@pytest.mark.unit
def test_check_positivity_zero_matrix(
    frobenius_inner_product: FrobeniusRealInnerProduct,
) -> None:
    """
    Test positivity with a zero matrix.

    Parameters
    ----------
    frobenius_inner_product : FrobeniusRealInnerProduct
        The FrobeniusRealInnerProduct instance to test
    """
    a = np.zeros((2, 2))

    result = frobenius_inner_product.check_positivity(a)

    assert result


@pytest.mark.unit
def test_serialization(frobenius_inner_product: FrobeniusRealInnerProduct) -> None:
    """
    Test serialization and deserialization of the FrobeniusRealInnerProduct.

    Parameters
    ----------
    frobenius_inner_product : FrobeniusRealInnerProduct
        The FrobeniusRealInnerProduct instance to test
    """
    # Serialize to JSON
    json_data = frobenius_inner_product.model_dump_json()

    # Deserialize from JSON
    deserialized = FrobeniusRealInnerProduct.model_validate_json(json_data)

    # Check that the type is preserved
    assert deserialized.type == frobenius_inner_product.type
    assert isinstance(deserialized, FrobeniusRealInnerProduct)


@pytest.mark.unit
@pytest.mark.parametrize(
    "a,b,expected",
    [
        (
            np.array([[1.0, 0.0], [0.0, 1.0]]),
            np.array([[1.0, 0.0], [0.0, 1.0]]),
            2.0,
        ),  # Identity matrices
        (
            np.array([[1.0, 2.0], [3.0, 4.0]]),
            np.array([[0.0, 0.0], [0.0, 0.0]]),
            0.0,
        ),  # With zero matrix
        (
            np.array([[1.0, 2.0], [3.0, 4.0]]),
            np.array([[-1.0, -2.0], [-3.0, -4.0]]),
            -30.0,
        ),  # Negative values
    ],
)
def test_compute_parameterized(
    frobenius_inner_product: FrobeniusRealInnerProduct,
    a: NDArray,
    b: NDArray,
    expected: float,
) -> None:
    """
    Parameterized test for compute method with various inputs.

    Parameters
    ----------
    frobenius_inner_product : FrobeniusRealInnerProduct
        The FrobeniusRealInnerProduct instance to test
    a : NDArray
        First input matrix
    b : NDArray
        Second input matrix
    expected : float
        Expected result
    """
    result = frobenius_inner_product.compute(a, b)
    assert result == pytest.approx(expected)


@pytest.mark.unit
def test_invalid_input_types(
    frobenius_inner_product: FrobeniusRealInnerProduct,
) -> None:
    """
    Test that compute method raises ValueError for invalid input types.

    Parameters
    ----------
    frobenius_inner_product : FrobeniusRealInnerProduct
        The FrobeniusRealInnerProduct instance to test
    """
    a = [[1, 2], [3, 4]]  # Not a numpy array
    b = np.array([[5, 6], [7, 8]])

    with pytest.raises(ValueError, match="Both inputs must be numpy arrays"):
        frobenius_inner_product.compute(a, b)
