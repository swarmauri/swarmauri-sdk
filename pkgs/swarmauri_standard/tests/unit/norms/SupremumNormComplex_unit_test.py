import pytest
import numpy as np
import logging
from typing import Any, List, Optional, Tuple, TypeVar, Union

from swarmauri_standard.norms.SupremumNormComplex import SupremumNormComplex


# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture
def supremum_norm():
    """
    Fixture providing a SupremumNormComplex instance for testing.

    Returns
    -------
    SupremumNormComplex
        An instance of the SupremumNormComplex class
    """
    return SupremumNormComplex()


@pytest.mark.unit
def test_type():
    """
    Test that the type attribute is correctly set.
    """
    assert SupremumNormComplex.type == "SupremumNormComplex"


@pytest.mark.unit
def test_name(supremum_norm):
    """
    Test the name method returns the correct string.
    """
    assert supremum_norm.name() == "SupremumNormComplex"


@pytest.mark.unit
@pytest.mark.parametrize(
    "vector, expected",
    [
        ([1+0j, 2+0j, 3+0j], 3.0),
        ([0+1j, 0+2j, 0+3j], 3.0),
        ([1+1j, 2+2j, 3+3j], np.abs(3+3j)),
        ([5+0j, -2+0j, 1+0j], 5.0),
        (np.array([3+4j, -1+2j, 2-3j]), 5.0),
        ([0+0j, 0+0j, 0+0j], 0.0),
        ([1+0j], 1.0),
    ]
)
def test_compute(supremum_norm, vector, expected):
    """
    Test the compute method with various complex vectors.
    
    Parameters
    ----------
    supremum_norm : SupremumNormComplex
        The norm instance
    vector : list or ndarray
        Input complex vector
    expected : float
        Expected norm value
    """
    result = supremum_norm.compute(vector)
    assert np.isclose(result, expected)
    assert isinstance(result, float)


@pytest.mark.unit
def test_compute_with_invalid_input(supremum_norm):
    """
    Test that compute method raises appropriate errors for invalid inputs.
    """
    with pytest.raises(Exception):
        supremum_norm.compute("not a vector")


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y, expected",
    [
        ([1+0j, 2+0j, 3+0j], [1+0j, 2+0j, 3+0j], 0.0),
        ([1+0j, 2+0j, 3+0j], [4+0j, 5+0j, 6+0j], 3.0),
        ([1+1j, 2+2j, 3+3j], [0+0j, 0+0j, 0+0j], np.abs(3+3j)),
        (np.array([3+4j, 1+2j]), np.array([1+1j, 0+0j]), np.abs(2+3j)),
    ]
)
def test_distance(supremum_norm, x, y, expected):
    """
    Test the distance method with various complex vector pairs.
    
    Parameters
    ----------
    supremum_norm : SupremumNormComplex
        The norm instance
    x : list or ndarray
        First complex vector
    y : list or ndarray
        Second complex vector
    expected : float
        Expected distance value
    """
    result = supremum_norm.distance(x, y)
    assert np.isclose(result, expected)
    assert isinstance(result, float)


@pytest.mark.unit
def test_distance_with_incompatible_shapes(supremum_norm):
    """
    Test that distance method raises error for incompatible vector shapes.
    """
    with pytest.raises(ValueError):
        supremum_norm.distance([1+0j, 2+0j], [1+0j, 2+0j, 3+0j])


@pytest.mark.unit
@pytest.mark.parametrize(
    "vector",
    [
        ([1+0j, 2+0j, 3+0j]),
        ([0+1j, 0+2j, 0+3j]),
        ([1+1j, 2+2j, 3+3j]),
        (np.array([3+4j, -1+2j, 2-3j])),
        ([5.0+0j]),
    ]
)
def test_normalize(supremum_norm, vector):
    """
    Test the normalize method with various complex vectors.
    
    Parameters
    ----------
    supremum_norm : SupremumNormComplex
        The norm instance
    vector : list or ndarray
        Complex vector to normalize
    """
    normalized = supremum_norm.normalize(vector)
    
    # Check that the normalized vector has unit norm
    assert np.isclose(supremum_norm.compute(normalized), 1.0)
    
    # Check that the normalized vector has the same direction
    original_array = np.asarray(vector, dtype=complex)
    norm_value = supremum_norm.compute(original_array)
    expected = original_array / norm_value
    
    if isinstance(normalized, np.ndarray):
        assert np.allclose(normalized, expected)
    else:
        assert np.allclose(np.asarray(normalized, dtype=complex), expected)


@pytest.mark.unit
def test_normalize_zero_vector(supremum_norm):
    """
    Test that normalize method raises error for zero vector.
    """
    with pytest.raises(ValueError):
        supremum_norm.normalize([0+0j, 0+0j, 0+0j])


@pytest.mark.unit
@pytest.mark.parametrize(
    "vector, tolerance, expected",
    [
        ([1+0j, 0+0j, 0+0j], 1e-10, True),
        ([0+0j, 0+1j, 0+0j], 1e-10, True),
        ([0.5+0j, 0+0j, 0+0j], 1e-10, False),
        ([0.707+0.707j, 0+0j], 1e-10, True),  # |0.707+0.707j| ≈ 1
        ([0.99+0j, 0+0j, 0+0j], 0.1, True),   # Within larger tolerance
        ([0.99+0j, 0+0j, 0+0j], 1e-10, False), # Outside small tolerance
    ]
)
def test_is_normalized(supremum_norm, vector, tolerance, expected):
    """
    Test the is_normalized method with various complex vectors.
    
    Parameters
    ----------
    supremum_norm : SupremumNormComplex
        The norm instance
    vector : list or ndarray
        Complex vector to check
    tolerance : float
        Tolerance for normalization check
    expected : bool
        Expected result
    """
    result = supremum_norm.is_normalized(vector, tolerance)
    assert result == expected


@pytest.mark.unit
def test_serialization():
    """
    Test serialization and deserialization of the SupremumNormComplex class.
    """
    # Create an instance
    norm = SupremumNormComplex()
    
    # Serialize to JSON
    json_data = norm.model_dump_json()
    
    # Deserialize from JSON
    deserialized = SupremumNormComplex.model_validate_json(json_data)
    
    # Check that the deserialized instance has the same type
    assert deserialized.type == norm.type


@pytest.mark.unit
def test_component_registration():
    """
    Test that SupremumNormComplex is properly registered as a component.
    """
    from swarmauri_base.ComponentBase import ComponentBase
    from swarmauri_base.norms.NormBase import NormBase
    
    # Check that the class is registered
    registered_class = ComponentBase.get_type(NormBase, "SupremumNormComplex")
    assert registered_class == SupremumNormComplex