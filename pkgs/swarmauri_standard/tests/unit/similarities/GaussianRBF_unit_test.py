import pytest
import numpy as np
import logging
from typing import List, Union
from swarmauri_standard.similarities.GaussianRBF import GaussianRBF

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture
def default_rbf():
    """
    Fixture that provides a default GaussianRBF instance with gamma=1.0.
    
    Returns
    -------
    GaussianRBF
        Default GaussianRBF instance
    """
    return GaussianRBF(gamma=1.0)

@pytest.fixture
def custom_rbf():
    """
    Fixture that provides a GaussianRBF instance with custom gamma=0.5.
    
    Returns
    -------
    GaussianRBF
        Custom GaussianRBF instance
    """
    return GaussianRBF(gamma=0.5)

@pytest.mark.unit
def test_type():
    """Test the type attribute of GaussianRBF."""
    rbf = GaussianRBF()
    assert rbf.type == "GaussianRBF"

@pytest.mark.unit
def test_resource():
    """Test the resource attribute of GaussianRBF."""
    assert GaussianRBF.resource == "Similarity"

@pytest.mark.unit
def test_default_initialization():
    """Test default initialization of GaussianRBF."""
    rbf = GaussianRBF()
    assert rbf.gamma == 1.0
    assert rbf.is_bounded is True
    assert rbf.lower_bound == 0.0
    assert rbf.upper_bound == 1.0

@pytest.mark.unit
def test_custom_initialization():
    """Test initialization with custom parameters."""
    rbf = GaussianRBF(gamma=0.5)
    assert rbf.gamma == 0.5

@pytest.mark.unit
def test_gamma_validation():
    """Test that gamma validation works correctly."""
    # Valid gamma
    rbf = GaussianRBF(gamma=0.1)
    assert rbf.gamma == 0.1
    
    # Invalid gamma (should raise ValueError)
    with pytest.raises(ValueError):
        GaussianRBF(gamma=0)
    
    with pytest.raises(ValueError):
        GaussianRBF(gamma=-1.0)

@pytest.mark.unit
@pytest.mark.parametrize("a, b, expected", [
    ([0, 0], [0, 0], 1.0),  # Same vectors should have similarity 1
    ([1, 1], [1, 1], 1.0),  # Same vectors should have similarity 1
    ([0, 0], [1, 1], np.exp(-2)),  # Distance 2, with gamma=1
    ([0, 0, 0], [1, 1, 1], np.exp(-3)),  # Distance 3, with gamma=1
])
def test_calculate(default_rbf: GaussianRBF, a: List[float], b: List[float], expected: float):
    """
    Test the calculate method with various input vectors.
    
    Parameters
    ----------
    default_rbf : GaussianRBF
        Default RBF instance
    a : List[float]
        First vector
    b : List[float]
        Second vector
    expected : float
        Expected similarity value
    """
    similarity = default_rbf.calculate(a, b)
    assert np.isclose(similarity, expected)

@pytest.mark.unit
def test_calculate_with_different_gamma(custom_rbf: GaussianRBF):
    """
    Test that gamma parameter affects the similarity calculation correctly.
    
    Parameters
    ----------
    custom_rbf : GaussianRBF
        Custom RBF instance with gamma=0.5
    """
    a = [0, 0]
    b = [1, 1]
    
    # With gamma=0.5, the similarity should be exp(-0.5 * 2) = exp(-1)
    expected = np.exp(-1)
    similarity = custom_rbf.calculate(a, b)
    assert np.isclose(similarity, expected)

@pytest.mark.unit
def test_calculate_with_numpy_arrays(default_rbf: GaussianRBF):
    """
    Test calculate method with numpy arrays as input.
    
    Parameters
    ----------
    default_rbf : GaussianRBF
        Default RBF instance
    """
    a = np.array([0, 0])
    b = np.array([1, 1])
    
    expected = np.exp(-2)
    similarity = default_rbf.calculate(a, b)
    assert np.isclose(similarity, expected)

@pytest.mark.unit
def test_calculate_with_mismatched_dimensions(default_rbf: GaussianRBF):
    """
    Test calculate method with vectors of different dimensions.
    
    Parameters
    ----------
    default_rbf : GaussianRBF
        Default RBF instance
    """
    a = [0, 0]
    b = [0, 0, 0]
    
    with pytest.raises(ValueError):
        default_rbf.calculate(a, b)

@pytest.mark.unit
def test_is_reflexive(default_rbf: GaussianRBF):
    """
    Test that the similarity measure is reflexive.
    
    Parameters
    ----------
    default_rbf : GaussianRBF
        Default RBF instance
    """
    assert default_rbf.is_reflexive() is True

@pytest.mark.unit
def test_is_symmetric(default_rbf: GaussianRBF):
    """
    Test that the similarity measure is symmetric.
    
    Parameters
    ----------
    default_rbf : GaussianRBF
        Default RBF instance
    """
    assert default_rbf.is_symmetric() is True

@pytest.mark.unit
def test_similarity_bounds(default_rbf: GaussianRBF):
    """
    Test that similarity values are bounded between 0 and 1.
    
    Parameters
    ----------
    default_rbf : GaussianRBF
        Default RBF instance
    """
    # Test with vectors that are far apart
    a = [0, 0]
    b = [10, 10]
    similarity = default_rbf.calculate(a, b)
    assert 0 <= similarity <= 1
    
    # Test with identical vectors (should be 1)
    a = [5, 5]
    b = [5, 5]
    similarity = default_rbf.calculate(a, b)
    assert np.isclose(similarity, 1.0)

@pytest.mark.unit
def test_serialization():
    """Test serialization and deserialization of GaussianRBF."""
    rbf = GaussianRBF(gamma=0.75)
    
    # Serialize to JSON
    json_str = rbf.model_dump_json()
    
    # Deserialize from JSON
    deserialized_rbf = GaussianRBF.model_validate_json(json_str)
    
    # Check that the deserialized object has the same attributes
    assert deserialized_rbf.gamma == rbf.gamma
    assert deserialized_rbf.is_bounded == rbf.is_bounded
    assert deserialized_rbf.lower_bound == rbf.lower_bound
    assert deserialized_rbf.upper_bound == rbf.upper_bound

@pytest.mark.unit
def test_string_representation():
    """Test the string representation of GaussianRBF."""
    rbf = GaussianRBF(gamma=1.0)
    str_repr = str(rbf)
    
    assert "GaussianRBF" in str_repr
    assert "gamma=1.0" in str_repr
    assert "bounds: [0.0, 1.0]" in str_repr