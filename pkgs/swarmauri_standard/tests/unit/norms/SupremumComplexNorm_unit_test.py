import logging

import numpy as np
import pytest

from swarmauri_standard.norms.SupremumComplexNorm import SupremumComplexNorm

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def supremum_norm():
    """
    Fixture that provides a SupremumComplexNorm instance.

    Returns
    -------
    SupremumComplexNorm
        An instance of the SupremumComplexNorm class.
    """
    return SupremumComplexNorm()


# Test data for parameterized tests
complex_vectors = [
    ([1 + 2j, 3 + 4j, 5 + 6j], 5 + 6j),  # List of complex numbers
    ([0, 1j, 2 + 2j], 2 + 2j),  # Mixed integers and complex
    ([-1 - 1j, -2 - 2j, -3 - 3j], -3 - 3j),  # Negative complex numbers
    ([1 + 0j, 0 + 1j, 1 + 1j], 1 + 1j),  # Unit complex numbers
    ([0 + 0j, 0 + 0j, 0 + 0j], 0 + 0j),  # Zero vector
]


@pytest.mark.unit
@pytest.mark.parametrize("vector, expected", complex_vectors)
def test_compute_with_vector(supremum_norm, vector, expected):
    """
    Test the compute method with various complex vectors.

    Parameters
    ----------
    supremum_norm : SupremumComplexNorm
        The norm instance to test.
    vector : List[complex]
        Input vector.
    expected : complex
        Expected result.
    """
    result = supremum_norm.compute(vector)
    assert result == expected


@pytest.mark.unit
def test_compute_with_numpy_array(supremum_norm):
    """
    Test the compute method with numpy arrays containing complex values.

    Parameters
    ----------
    supremum_norm : SupremumComplexNorm
        The norm instance to test.
    """
    # Create a numpy array with complex values
    array = np.array([1 + 1j, 2 + 2j, 3 + 3j])
    result = supremum_norm.compute(array)
    assert result == 3 + 3j

    # Test with a 2D array (should flatten or handle appropriately)
    array_2d = np.array([[1 + 1j, 2 + 2j], [3 + 3j, 4 + 4j]])
    result = supremum_norm.compute(array_2d)
    assert result == 4 + 4j


@pytest.mark.unit
def test_compute_with_single_value(supremum_norm):
    """
    Test the compute method with single complex values.

    Parameters
    ----------
    supremum_norm : SupremumComplexNorm
        The norm instance to test.
    """
    assert supremum_norm.compute(3 + 4j) == 3 + 4j
    assert supremum_norm.compute(0 + 0j) == 0 + 0j
    assert supremum_norm.compute(5) == 5 + 0j  # Integer should be converted to complex


@pytest.mark.unit
def test_compute_with_string(supremum_norm):
    """
    Test the compute method with string representations of complex numbers.

    Parameters
    ----------
    supremum_norm : SupremumComplexNorm
        The norm instance to test.
    """
    assert supremum_norm.compute("3+4j") == 3 + 4j
    assert supremum_norm.compute("[1+2j, 3+4j]") == 3 + 4j


@pytest.mark.unit
def test_compute_with_callable(supremum_norm):
    """
    Test the compute method with callable functions.

    Parameters
    ----------
    supremum_norm : SupremumComplexNorm
        The norm instance to test.
    """

    # Define a complex-valued function
    def complex_func(t):
        return t + 1j * t**2

    # The compute method should evaluate the function at points in a domain
    result = supremum_norm.compute(complex_func)

    # The exact expected value depends on the domain used in the implementation
    # but we can check that the result is a complex number
    assert isinstance(result, complex)


@pytest.mark.unit
def test_empty_vector(supremum_norm):
    """
    Test the compute method with an empty vector.

    Parameters
    ----------
    supremum_norm : SupremumComplexNorm
        The norm instance to test.
    """
    result = supremum_norm.compute([])
    assert result == 0 + 0j


@pytest.mark.unit
def test_resource_type(supremum_norm):
    """
    Test that the resource type is correctly set.

    Parameters
    ----------
    supremum_norm : SupremumComplexNorm
        The norm instance to test.
    """
    assert supremum_norm.resource == "Norm"


@pytest.mark.unit
def test_component_type(supremum_norm):
    """
    Test that the component type is correctly set.

    Parameters
    ----------
    supremum_norm : SupremumComplexNorm
        The norm instance to test.
    """
    assert supremum_norm.type == "SupremumComplexNorm"


@pytest.mark.unit
def test_serialization(supremum_norm):
    """
    Test that the component can be serialized and deserialized.

    Parameters
    ----------
    supremum_norm : SupremumComplexNorm
        The norm instance to test.
    """
    json_data = supremum_norm.model_dump_json()
    deserialized = SupremumComplexNorm.model_validate_json(json_data)
    assert deserialized.type == supremum_norm.type
    assert deserialized.resource == supremum_norm.resource


@pytest.mark.unit
def test_non_negativity(supremum_norm):
    """
    Test the check_non_negativity method.

    Parameters
    ----------
    supremum_norm : SupremumComplexNorm
        The norm instance to test.
    """
    # Non-negativity should always be true for a valid complex norm
    assert supremum_norm.check_non_negativity([1 + 2j, 3 + 4j, 5 + 6j])
    assert supremum_norm.check_non_negativity([0 + 0j, 0 + 0j])
    assert supremum_norm.check_non_negativity([-1 - 1j, -2 - 2j])


@pytest.mark.unit
def test_definiteness(supremum_norm):
    """
    Test the check_definiteness method.

    Parameters
    ----------
    supremum_norm : SupremumComplexNorm
        The norm instance to test.
    """
    # Definiteness: norm(x) = 0 if and only if x = 0
    assert supremum_norm.check_definiteness([0 + 0j, 0 + 0j, 0 + 0j])
    assert supremum_norm.check_definiteness(0 + 0j)

    # Non-zero vectors should not have zero norm
    assert not supremum_norm.check_definiteness([1 + 1j, 0 + 0j, 0 + 0j])
    assert not supremum_norm.check_definiteness(1 + 1j)


@pytest.mark.unit
def test_triangle_inequality(supremum_norm):
    """
    Test the check_triangle_inequality method.

    Parameters
    ----------
    supremum_norm : SupremumComplexNorm
        The norm instance to test.
    """
    # Triangle inequality: norm(x + y) <= norm(x) + norm(y)
    x = [1 + 1j, 2 + 2j, 3 + 3j]
    y = [4 + 4j, 5 + 5j, 6 + 6j]
    assert supremum_norm.check_triangle_inequality(x, y)

    # Test with single values
    assert supremum_norm.check_triangle_inequality(1 + 1j, 2 + 2j)

    # Test with numpy arrays
    x_array = np.array([1 + 1j, 2 + 2j, 3 + 3j])
    y_array = np.array([4 + 4j, 5 + 5j, 6 + 6j])
    assert supremum_norm.check_triangle_inequality(x_array, y_array)


@pytest.mark.unit
def test_absolute_homogeneity(supremum_norm):
    """
    Test the check_absolute_homogeneity method.

    Parameters
    ----------
    supremum_norm : SupremumComplexNorm
        The norm instance to test.
    """
    # Absolute homogeneity: norm(a*x) = |a|*norm(x)
    x = [1 + 1j, 2 + 2j, 3 + 3j]
    scalar = 2 + 3j
    assert supremum_norm.check_absolute_homogeneity(x, scalar)

    # Test with single values
    assert supremum_norm.check_absolute_homogeneity(1 + 1j, 2 + 3j)

    # Test with numpy arrays
    x_array = np.array([1 + 1j, 2 + 2j, 3 + 3j])
    assert supremum_norm.check_absolute_homogeneity(x_array, scalar)


@pytest.mark.unit
def test_error_handling(supremum_norm):
    """
    Test error handling in the compute method.

    Parameters
    ----------
    supremum_norm : SupremumComplexNorm
        The norm instance to test.
    """

    # Test with an invalid input that can't be converted to complex
    class InvalidInput:
        def __complex__(self):
            raise ValueError("Cannot convert to complex")

    with pytest.raises(ValueError):
        supremum_norm.compute(InvalidInput())


@pytest.mark.unit
def test_callable_with_domain(supremum_norm):
    """
    Test the compute method with a callable function using a specific domain.

    Parameters
    ----------
    supremum_norm : SupremumComplexNorm
        The norm instance to test.
    """

    # Define a complex function with known maximum on [-1, 1]
    def complex_func(t):
        return t**2 + 1j * t**3

    # The maximum absolute value should occur at t = 1 or t = -1
    # |complex_func(1)| = |1 + 1j| = sqrt(2)
    # |complex_func(-1)| = |1 - 1j| = sqrt(2)
    result = supremum_norm.compute(complex_func)

    # Check if the result is one of the expected values (allowing for numerical precision)
    expected_values = [1 + 1j, 1 - 1j]
    assert any(abs(result - expected) < 1e-10 for expected in expected_values)
