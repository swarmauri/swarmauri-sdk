import logging
import pytest
import numpy as np
from typing import Tuple, Union, Callable
import numpy.typing as npt

from swarmauri_standard.inner_products.SobolevH1 import SobolevH1

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture
def sobolev_h1_default():
    """
    Fixture providing a default SobolevH1 instance with alpha=1.0 and beta=1.0.
    
    Returns
    -------
    SobolevH1
        A default SobolevH1 instance
    """
    return SobolevH1()


@pytest.fixture
def sobolev_h1_custom():
    """
    Fixture providing a custom SobolevH1 instance with alpha=2.0 and beta=3.0.
    
    Returns
    -------
    SobolevH1
        A custom SobolevH1 instance
    """
    return SobolevH1(alpha=2.0, beta=3.0)


@pytest.fixture
def compatible_arrays():
    """
    Fixture providing compatible array inputs for testing.
    
    Returns
    -------
    Tuple[Tuple[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]]
        Two tuples each containing a function array and its derivative array
    """
    # Create sample function values and their derivatives
    f = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    df = np.array([1.0, 1.0, 1.0, 1.0, 1.0])
    g = np.array([5.0, 4.0, 3.0, 2.0, 1.0])
    dg = np.array([0.0, -1.0, -1.0, -1.0, -1.0])
    
    return (f, df), (g, dg)


@pytest.fixture
def incompatible_arrays():
    """
    Fixture providing incompatible array inputs for testing.
    
    Returns
    -------
    Tuple[Tuple[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]]
        Two tuples with mismatched array lengths
    """
    f = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    df = np.array([1.0, 1.0, 1.0, 1.0, 1.0])
    g = np.array([5.0, 4.0, 3.0])  # Different length
    dg = np.array([0.0, -1.0, -1.0])
    
    return (f, df), (g, dg)


@pytest.mark.unit
def test_initialization_default():
    """Test default initialization of SobolevH1."""
    h1 = SobolevH1()
    assert h1.alpha == 1.0
    assert h1.beta == 1.0
    assert h1.type == "SobolevH1"


@pytest.mark.unit
def test_initialization_custom():
    """Test custom initialization of SobolevH1."""
    h1 = SobolevH1(alpha=2.5, beta=3.5)
    assert h1.alpha == 2.5
    assert h1.beta == 3.5


@pytest.mark.unit
def test_compute_with_arrays(sobolev_h1_default, compatible_arrays):
    """
    Test the compute method with numpy arrays.
    
    Parameters
    ----------
    sobolev_h1_default : SobolevH1
        Default SobolevH1 instance from fixture
    compatible_arrays : Tuple
        Compatible array inputs from fixture
    """
    vec1, vec2 = compatible_arrays
    
    # Manually calculate expected result
    f, df = vec1
    g, dg = vec2
    expected = np.sum(f * g) + np.sum(df * dg)
    
    result = sobolev_h1_default.compute(vec1, vec2)
    
    assert isinstance(result, float)
    assert np.isclose(result, expected)


@pytest.mark.unit
def test_compute_with_custom_weights(sobolev_h1_custom, compatible_arrays):
    """
    Test the compute method with custom weights.
    
    Parameters
    ----------
    sobolev_h1_custom : SobolevH1
        Custom SobolevH1 instance from fixture
    compatible_arrays : Tuple
        Compatible array inputs from fixture
    """
    vec1, vec2 = compatible_arrays
    
    # Manually calculate expected result with custom weights
    f, df = vec1
    g, dg = vec2
    expected = 2.0 * np.sum(f * g) + 3.0 * np.sum(df * dg)
    
    result = sobolev_h1_custom.compute(vec1, vec2)
    
    assert isinstance(result, float)
    assert np.isclose(result, expected)


@pytest.mark.unit
def test_compute_with_incompatible_arrays(sobolev_h1_default, incompatible_arrays):
    """
    Test that compute raises ValueError for incompatible arrays.
    
    Parameters
    ----------
    sobolev_h1_default : SobolevH1
        Default SobolevH1 instance from fixture
    incompatible_arrays : Tuple
        Incompatible array inputs from fixture
    """
    vec1, vec2 = incompatible_arrays
    
    with pytest.raises(ValueError):
        sobolev_h1_default.compute(vec1, vec2)


@pytest.mark.unit
def test_compute_with_invalid_input_types(sobolev_h1_default):
    """
    Test that compute raises TypeError for invalid input types.
    
    Parameters
    ----------
    sobolev_h1_default : SobolevH1
        Default SobolevH1 instance from fixture
    """
    # Test with non-tuple inputs
    with pytest.raises(ValueError):
        sobolev_h1_default.compute([1, 2, 3], [4, 5, 6])
    
    # Test with incomplete tuples
    with pytest.raises(ValueError):
        sobolev_h1_default.compute((np.array([1, 2, 3]),), (np.array([4, 5, 6]),))


@pytest.mark.unit
def test_is_compatible_with_arrays(sobolev_h1_default, compatible_arrays):
    """
    Test is_compatible method with compatible arrays.
    
    Parameters
    ----------
    sobolev_h1_default : SobolevH1
        Default SobolevH1 instance from fixture
    compatible_arrays : Tuple
        Compatible array inputs from fixture
    """
    vec1, vec2 = compatible_arrays
    assert sobolev_h1_default.is_compatible(vec1, vec2) is True


@pytest.mark.unit
def test_is_compatible_with_incompatible_arrays(sobolev_h1_default, incompatible_arrays):
    """
    Test is_compatible method with incompatible arrays.
    
    Parameters
    ----------
    sobolev_h1_default : SobolevH1
        Default SobolevH1 instance from fixture
    incompatible_arrays : Tuple
        Incompatible array inputs from fixture
    """
    vec1, vec2 = incompatible_arrays
    assert sobolev_h1_default.is_compatible(vec1, vec2) is False


@pytest.mark.unit
def test_is_compatible_with_invalid_types(sobolev_h1_default):
    """
    Test is_compatible method with invalid input types.
    
    Parameters
    ----------
    sobolev_h1_default : SobolevH1
        Default SobolevH1 instance from fixture
    """
    # Test with non-tuple inputs
    assert sobolev_h1_default.is_compatible([1, 2, 3], [4, 5, 6]) is False
    
    # Test with incomplete tuples
    assert sobolev_h1_default.is_compatible((np.array([1, 2, 3]),), (np.array([4, 5, 6]),)) is False
    
    # Test with mismatched types
    f = np.array([1.0, 2.0, 3.0])
    df = np.array([1.0, 1.0, 1.0])
    
    # Function is array but derivative is not
    assert sobolev_h1_default.is_compatible((f, "not_array"), (f, df)) is False
    
    # Function is callable but derivative is not
    def func(x): return x**2
    assert sobolev_h1_default.is_compatible((func, f), (func, lambda x: 2*x)) is False


@pytest.mark.unit
def test_callable_not_implemented(sobolev_h1_default):
    """
    Test that using callable functions raises NotImplementedError.
    
    Parameters
    ----------
    sobolev_h1_default : SobolevH1
        Default SobolevH1 instance from fixture
    """
    def f(x): return x**2
    def df(x): return 2*x
    def g(x): return x**3
    def dg(x): return 3*x**2
    
    # The implementation should recognize these as compatible
    assert sobolev_h1_default.is_compatible((f, df), (g, dg)) is True
    
    # But compute should raise NotImplementedError
    with pytest.raises(NotImplementedError):
        sobolev_h1_default.compute((f, df), (g, dg))


@pytest.mark.unit
def test_type_registration():
    """Test that SobolevH1 is correctly registered with its type."""
    assert SobolevH1.type == "SobolevH1"


@pytest.mark.unit
def test_serialization_deserialization():
    """Test that SobolevH1 can be serialized and deserialized."""
    original = SobolevH1(alpha=2.5, beta=3.5)
    serialized = original.model_dump_json()
    deserialized = SobolevH1.model_validate_json(serialized)
    
    assert deserialized.alpha == original.alpha
    assert deserialized.beta == original.beta
    assert deserialized.type == original.type