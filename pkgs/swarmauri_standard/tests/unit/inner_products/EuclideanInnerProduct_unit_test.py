import logging

import numpy as np
import pytest

from swarmauri_standard.inner_products.EuclideanInnerProduct import (
    EuclideanInnerProduct,
)

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture
def euclidean_inner_product():
    """
    Fixture providing an instance of EuclideanInnerProduct for testing.

    Returns
    -------
    EuclideanInnerProduct
        An instance of the EuclideanInnerProduct class
    """
    return EuclideanInnerProduct()


@pytest.mark.unit
def test_type_attribute(euclidean_inner_product):
    """
    Test that the type attribute is correctly set.
    """
    assert euclidean_inner_product.type == "EuclideanInnerProduct"


@pytest.mark.unit
def test_resource_attribute(euclidean_inner_product):
    """
    Test that the resource attribute is correctly set.
    """
    assert euclidean_inner_product.resource == "InnerProduct"


@pytest.mark.unit
@pytest.mark.parametrize(
    "a, b, expected",
    [
        ([1, 2, 3], [4, 5, 6], 32),  # Basic vector dot product
        ([0, 0, 0], [1, 2, 3], 0),  # Zero vector
        ([1, 1, 1], [1, 1, 1], 3),  # Unit vectors
        ([-1, -2, -3], [4, 5, 6], -32),  # Negative values
        (
            np.array([1.5, 2.5]),
            np.array([3.5, 4.5]),
            16.5,
        ),  # Float values - Fixed value
    ],
)
def test_compute_valid_inputs(euclidean_inner_product, a, b, expected):
    """
    Test the compute method with various valid inputs.

    Parameters
    ----------
    euclidean_inner_product : EuclideanInnerProduct
        The inner product instance from the fixture
    a : list or ndarray
        First vector
    b : list or ndarray
        Second vector
    expected : float
        Expected inner product result
    """
    result = euclidean_inner_product.compute(a, b)
    assert np.isclose(result, expected)
    assert isinstance(result, float)


@pytest.mark.unit
def test_compute_with_numpy_arrays(euclidean_inner_product):
    """
    Test the compute method with NumPy arrays.

    Parameters
    ----------
    euclidean_inner_product : EuclideanInnerProduct
        The inner product instance from the fixture
    """
    a = np.array([1, 2, 3])
    b = np.array([4, 5, 6])
    expected = 32
    result = euclidean_inner_product.compute(a, b)
    assert np.isclose(result, expected)


@pytest.mark.unit
def test_compute_with_lists(euclidean_inner_product):
    """
    Test the compute method with Python lists.

    Parameters
    ----------
    euclidean_inner_product : EuclideanInnerProduct
        The inner product instance from the fixture
    """
    a = [1, 2, 3]
    b = [4, 5, 6]
    expected = 32
    result = euclidean_inner_product.compute(a, b)
    assert np.isclose(result, expected)


@pytest.mark.unit
@pytest.mark.parametrize(
    "a, b",
    [
        ([1, 2, 3], [4, 5]),  # Incompatible dimensions
        ("not a vector", [1, 2, 3]),  # Non-numeric input
        ([1, 2, 3], "not a vector"),  # Non-numeric input
        ([1, np.nan, 3], [4, 5, 6]),  # NaN values
        ([1, 2, 3], [4, np.inf, 6]),  # Infinite values
    ],
)
def test_compute_invalid_inputs(euclidean_inner_product, a, b):
    """
    Test the compute method with invalid inputs to ensure proper error handling.

    Parameters
    ----------
    euclidean_inner_product : EuclideanInnerProduct
        The inner product instance from the fixture
    a : any
        First input
    b : any
        Second input
    """
    with pytest.raises((ValueError, TypeError)):
        euclidean_inner_product.compute(a, b)


@pytest.mark.unit
@pytest.mark.parametrize(
    "a, b",
    [
        ([1, 2, 3], [4, 5, 6]),
        ([0, 0, 0], [0, 0, 0]),
        ([-1, -2, -3], [4, 5, 6]),
        (np.array([1.5, 2.5]), np.array([3.5, 4.5])),
    ],
)
def test_conjugate_symmetry(euclidean_inner_product, a, b):
    """
    Test that the inner product satisfies conjugate symmetry.

    Parameters
    ----------
    euclidean_inner_product : EuclideanInnerProduct
        The inner product instance from the fixture
    a : list or ndarray
        First vector
    b : list or ndarray
        Second vector
    """
    assert euclidean_inner_product.check_conjugate_symmetry(a, b)

    # Direct computation to verify
    ab_product = euclidean_inner_product.compute(a, b)
    ba_product = euclidean_inner_product.compute(b, a)
    assert np.isclose(ab_product, ba_product)


@pytest.mark.unit
@pytest.mark.parametrize(
    "a1, a2, b, alpha, beta",
    [
        ([1, 2, 3], [4, 5, 6], [7, 8, 9], 2, 3),
        ([0, 0, 0], [1, 1, 1], [2, 2, 2], 1, 1),
        ([-1, -2, -3], [4, 5, 6], [7, 8, 9], -1, 2),
        (np.array([1.5, 2.5]), np.array([3.5, 4.5]), np.array([5.5, 6.5]), 0.5, 1.5),
    ],
)
def test_linearity_first_argument(euclidean_inner_product, a1, a2, b, alpha, beta):
    """
    Test that the inner product satisfies linearity in the first argument.

    Parameters
    ----------
    euclidean_inner_product : EuclideanInnerProduct
        The inner product instance from the fixture
    a1 : list or ndarray
        First component of the first argument
    a2 : list or ndarray
        Second component of the first argument
    b : list or ndarray
        Second vector
    alpha : float
        Scalar multiplier for a1
    beta : float
        Scalar multiplier for a2
    """
    assert euclidean_inner_product.check_linearity_first_argument(
        a1, a2, b, alpha, beta
    )

    # Direct computation to verify
    a1_array = np.array(a1)
    a2_array = np.array(a2)

    combined = alpha * a1_array + beta * a2_array
    left_side = euclidean_inner_product.compute(combined, b)
    right_side = alpha * euclidean_inner_product.compute(
        a1, b
    ) + beta * euclidean_inner_product.compute(a2, b)

    assert np.isclose(left_side, right_side)


@pytest.mark.unit
@pytest.mark.parametrize(
    "a",
    [
        ([1, 2, 3]),
        ([0, 0, 0]),
        ([-1, -2, -3]),
        (np.array([1.5, 2.5])),
    ],
)
def test_positivity(euclidean_inner_product, a):
    """
    Test that the inner product satisfies the positivity property.

    Parameters
    ----------
    euclidean_inner_product : EuclideanInnerProduct
        The inner product instance from the fixture
    a : list or ndarray
        Vector to check positivity for
    """
    assert euclidean_inner_product.check_positivity(a)

    # Direct computation to verify
    self_product = euclidean_inner_product.compute(a, a)
    a_array = np.array(a)

    assert self_product >= 0
    if np.allclose(a_array, 0):
        assert np.isclose(self_product, 0)
    else:
        assert self_product > 0


@pytest.mark.unit
def test_serialization(euclidean_inner_product):
    """
    Test serialization and deserialization of the EuclideanInnerProduct class.

    Parameters
    ----------
    euclidean_inner_product : EuclideanInnerProduct
        The inner product instance from the fixture
    """
    # Serialize to JSON
    json_data = euclidean_inner_product.model_dump_json()

    # Deserialize from JSON
    deserialized = EuclideanInnerProduct.model_validate_json(json_data)

    # Check if the deserialized object is of the correct type
    assert isinstance(deserialized, EuclideanInnerProduct)

    # Check if the type attribute is preserved
    assert deserialized.type == "EuclideanInnerProduct"


@pytest.mark.unit
def test_inheritance():
    """
    Test that EuclideanInnerProduct inherits from the correct base classes.
    """
    from swarmauri_base.inner_products.InnerProductBase import InnerProductBase

    euclidean_inner_product = EuclideanInnerProduct()
    assert isinstance(euclidean_inner_product, InnerProductBase)
