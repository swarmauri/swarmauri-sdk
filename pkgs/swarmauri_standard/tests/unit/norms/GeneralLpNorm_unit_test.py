import pytest
import numpy as np
import logging
from typing import List, Tuple, Any

from swarmauri_standard.norms.GeneralLpNorm import GeneralLpNorm

# Configure logging
logger = logging.getLogger(__name__)


@pytest.fixture
def generallp_norm():
    """
    Fixture providing a default GeneralLpNorm instance with p=2.
    
    Returns
    -------
    GeneralLpNorm
        A GeneralLpNorm instance with default parameters
    """
    return GeneralLpNorm()


@pytest.fixture
def generallp_norm_custom_p():
    """
    Fixture providing a GeneralLpNorm instance with custom p value.
    
    Returns
    -------
    GeneralLpNorm
        A GeneralLpNorm instance with p=3
    """
    return GeneralLpNorm(p=3.0)


@pytest.mark.unit
def test_resource():
    """Test that the resource type is correctly set."""
    assert GeneralLpNorm.resource == "Norm"


@pytest.mark.unit
def test_type():
    """Test that the type identifier is correctly set."""
    assert GeneralLpNorm.type == "GeneralLpNorm"


@pytest.mark.unit
def test_default_p_value(generallp_norm):
    """Test that the default p value is 2."""
    assert generallp_norm.p == 2.0


@pytest.mark.unit
def test_custom_p_value(generallp_norm_custom_p):
    """Test that custom p value is correctly set."""
    assert generallp_norm_custom_p.p == 3.0


@pytest.mark.unit
def test_invalid_p_value():
    """Test that invalid p values raise a validation error."""
    with pytest.raises(ValueError):
        GeneralLpNorm(p=0.5)  # p must be > 1
    
    with pytest.raises(ValueError):
        GeneralLpNorm(p=1.0)  # p must be > 1


@pytest.mark.unit
def test_serialization(generallp_norm):
    """Test serialization and deserialization of GeneralLpNorm."""
    json_data = generallp_norm.model_dump_json()
    deserialized = GeneralLpNorm.model_validate_json(json_data)
    
    assert deserialized.p == generallp_norm.p
    assert deserialized.type == generallp_norm.type


@pytest.mark.unit
@pytest.mark.parametrize("vector, expected_norm", [
    ([3, 4], 5.0),  # L2 norm of [3, 4] is 5
    ([1, 1, 1], 3 ** 0.5),  # L2 norm of [1, 1, 1] is sqrt(3)
    ([0, 0, 0], 0.0),  # L2 norm of [0, 0, 0] is 0
    ([-5, 12], 13.0),  # L2 norm of [-5, 12] is 13
])
def test_compute_l2_norm(generallp_norm, vector, expected_norm):
    """Test computation of L2 norm with default p=2."""
    computed_norm = generallp_norm.compute(vector)
    assert np.isclose(computed_norm, expected_norm)


@pytest.mark.unit
@pytest.mark.parametrize("vector, expected_norm", [
    ([3, 4], (3**3 + 4**3)**(1/3)),  # L3 norm of [3, 4]
    ([1, 1, 1], 3**(1/3)),  # L3 norm of [1, 1, 1]
    ([0, 0, 0], 0.0),  # L3 norm of [0, 0, 0] is 0
    ([-5, 12], ((-5)**3 + 12**3)**(1/3)),  # L3 norm of [-5, 12]
])
def test_compute_l3_norm(generallp_norm_custom_p, vector, expected_norm):
    """Test computation of L3 norm with p=3."""
    computed_norm = generallp_norm_custom_p.compute(vector)
    assert np.isclose(computed_norm, expected_norm)


@pytest.mark.unit
@pytest.mark.parametrize("input_type", [
    list,  # Test with list input
    tuple,  # Test with tuple input
    np.ndarray,  # Test with numpy array input
])
def test_compute_with_different_input_types(generallp_norm, input_type):
    """Test that compute works with different input types."""
    vector = [1, 2, 3]
    
    if input_type == list:
        result = generallp_norm.compute(vector)
    elif input_type == tuple:
        result = generallp_norm.compute(tuple(vector))
    else:  # np.ndarray
        result = generallp_norm.compute(np.array(vector))
    
    expected = (1**2 + 2**2 + 3**2)**0.5
    assert np.isclose(result, expected)


@pytest.mark.unit
def test_compute_with_invalid_input(generallp_norm):
    """Test that compute raises appropriate errors for invalid inputs."""
    with pytest.raises(ValueError):
        generallp_norm.compute("not a vector")


@pytest.mark.unit
@pytest.mark.parametrize("x, y, expected_distance", [
    ([1, 0], [0, 1], 2**0.5),  # L2 distance between [1, 0] and [0, 1] is sqrt(2)
    ([3, 4], [0, 0], 5.0),  # L2 distance between [3, 4] and [0, 0] is 5
    ([1, 1, 1], [2, 2, 2], 3**0.5),  # L2 distance between [1, 1, 1] and [2, 2, 2] is sqrt(3)
])
def test_distance(generallp_norm, x, y, expected_distance):
    """Test distance calculation between vectors."""
    computed_distance = generallp_norm.distance(x, y)
    assert np.isclose(computed_distance, expected_distance)


@pytest.mark.unit
def test_distance_with_incompatible_dimensions(generallp_norm):
    """Test that distance raises error for incompatible dimensions."""
    with pytest.raises(ValueError):
        generallp_norm.distance([1, 2], [1, 2, 3])


@pytest.mark.unit
@pytest.mark.parametrize("vector, expected_normalized", [
    ([3, 4], [0.6, 0.8]),  # Normalized [3, 4] with L2 norm
    ([1, 1, 1], [1/3**0.5, 1/3**0.5, 1/3**0.5]),  # Normalized [1, 1, 1] with L2 norm
])
def test_normalize(generallp_norm, vector, expected_normalized):
    """Test vector normalization."""
    normalized = generallp_norm.normalize(vector)
    assert np.allclose(normalized, expected_normalized)


@pytest.mark.unit
def test_normalize_zero_vector(generallp_norm):
    """Test that normalizing a zero vector raises an error."""
    with pytest.raises(ValueError):
        generallp_norm.normalize([0, 0, 0])


@pytest.mark.unit
@pytest.mark.parametrize("input_type, vector", [
    (list, [3, 4]),  # Test with list input
    (tuple, (3, 4)),  # Test with tuple input
    (np.ndarray, np.array([3, 4])),  # Test with numpy array input
])
def test_normalize_preserves_input_type(generallp_norm, input_type, vector):
    """Test that normalize preserves the input type."""
    if input_type == list:
        result = generallp_norm.normalize(vector)
        assert isinstance(result, list)
    elif input_type == tuple:
        result = generallp_norm.normalize(vector)
        assert isinstance(result, tuple)
    else:  # np.ndarray
        result = generallp_norm.normalize(vector)
        assert isinstance(result, np.ndarray)


@pytest.mark.unit
@pytest.mark.parametrize("vector, expected_result", [
    ([1/2**0.5, 1/2**0.5], True),  # Unit vector with L2 norm
    ([3, 4], False),  # Non-unit vector with L2 norm
    ([1, 0], True),  # Unit vector with L2 norm
])
def test_is_normalized(generallp_norm, vector, expected_result):
    """Test checking if a vector is normalized."""
    assert generallp_norm.is_normalized(vector) == expected_result


@pytest.mark.unit
def test_is_normalized_with_tolerance(generallp_norm):
    """Test is_normalized with different tolerance values."""
    # Vector with norm very close to 1
    vector = [0.7071, 0.7072]  # Slightly off from [1/sqrt(2), 1/sqrt(2)]
    
    # Should be considered normalized with a larger tolerance
    assert generallp_norm.is_normalized(vector, tolerance=1e-3)
    
    # Should not be considered normalized with a very small tolerance
    assert not generallp_norm.is_normalized(vector, tolerance=1e-10)


@pytest.mark.unit
def test_name(generallp_norm, generallp_norm_custom_p):
    """Test the name method returns correct string identifier."""
    assert generallp_norm.name() == "L2.0 Norm"
    assert generallp_norm_custom_p.name() == "L3.0 Norm"