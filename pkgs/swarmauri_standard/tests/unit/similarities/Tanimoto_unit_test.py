import logging
import pytest
import numpy as np
from typing import List, Tuple

from swarmauri_standard.similarities.Tanimoto import Tanimoto

# Set up logging
logger = logging.getLogger(__name__)

# Test fixtures
@pytest.fixture
def tanimoto_instance():
    """Fixture that provides a Tanimoto instance."""
    return Tanimoto()

@pytest.fixture
def vector_pairs() -> List[Tuple[List[float], List[float], float]]:
    """
    Fixture that provides test vector pairs and their expected similarity scores.
    
    Returns
    -------
    List[Tuple[List[float], List[float], float]]
        List of tuples containing (vector1, vector2, expected_similarity)
    """
    return [
        ([1.0, 1.0, 1.0], [1.0, 1.0, 1.0], 1.0),  # Identical vectors
        ([1.0, 0.0, 0.0], [0.0, 1.0, 0.0], 0.0),  # Orthogonal vectors
        ([0.5, 0.5, 0.5], [1.0, 1.0, 1.0], 0.6),  # Similar vectors
        ([0.1, 0.2, 0.3], [0.3, 0.2, 0.1], 0.7),  # Different but related vectors
        ([1.0, 2.0, 3.0], [2.0, 4.0, 6.0], 0.857142857),  # Proportional vectors
    ]

@pytest.mark.unit
def test_type():
    """Test that the type attribute is correctly set to 'Tanimoto'."""
    tanimoto = Tanimoto()
    assert tanimoto.type == "Tanimoto"

@pytest.mark.unit
def test_resource():
    """Test that the resource attribute is correctly set to 'Similarity'."""
    tanimoto = Tanimoto()
    assert tanimoto.resource == "Similarity"

@pytest.mark.unit
def test_bounds():
    """Test that the similarity bounds are correctly set."""
    tanimoto = Tanimoto()
    assert tanimoto.is_bounded is True
    assert tanimoto.lower_bound == 0.0
    assert tanimoto.upper_bound == 1.0

@pytest.mark.unit
def test_is_reflexive():
    """Test that the Tanimoto similarity is reflexive."""
    tanimoto = Tanimoto()
    assert tanimoto.is_reflexive() is True

@pytest.mark.unit
def test_is_symmetric():
    """Test that the Tanimoto similarity is symmetric."""
    tanimoto = Tanimoto()
    assert tanimoto.is_symmetric() is True

@pytest.mark.unit
@pytest.mark.parametrize("a, b, expected", [
    ([1.0, 1.0, 1.0], [1.0, 1.0, 1.0], 1.0),  # Identical vectors
    ([1.0, 0.0, 0.0], [0.0, 1.0, 0.0], 0.0),  # Orthogonal vectors
    ([0.5, 0.5, 0.5], [1.0, 1.0, 1.0], 0.6),  # Similar vectors
    ([0.1, 0.2, 0.3], [0.3, 0.2, 0.1], 0.7),  # Different but related vectors
])
def test_calculate(a, b, expected, tanimoto_instance):
    """
    Test the calculate method with various vector pairs.
    
    Parameters
    ----------
    a : List[float]
        First vector
    b : List[float]
        Second vector
    expected : float
        Expected similarity value
    tanimoto_instance : Tanimoto
        Instance of Tanimoto similarity
    """
    similarity = tanimoto_instance.calculate(a, b)
    assert pytest.approx(similarity, abs=1e-6) == expected

@pytest.mark.unit
def test_calculate_with_numpy_arrays(tanimoto_instance):
    """Test that the calculate method works with numpy arrays."""
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([3.0, 2.0, 1.0])
    
    similarity = tanimoto_instance.calculate(a, b)
    # Expected: (1*3 + 2*2 + 3*1) / (14 + 14 - 10) = 10 / 18 = 0.555...
    assert pytest.approx(similarity, abs=1e-6) == 0.5555555555555556

@pytest.mark.unit
def test_symmetry_property(vector_pairs, tanimoto_instance):
    """
    Test that the Tanimoto similarity is symmetric in practice.
    
    Parameters
    ----------
    vector_pairs : List[Tuple[List[float], List[float], float]]
        List of test vector pairs and expected similarities
    tanimoto_instance : Tanimoto
        Instance of Tanimoto similarity
    """
    for a, b, _ in vector_pairs:
        sim_ab = tanimoto_instance.calculate(a, b)
        sim_ba = tanimoto_instance.calculate(b, a)
        assert pytest.approx(sim_ab, abs=1e-6) == sim_ba

@pytest.mark.unit
def test_reflexive_property(tanimoto_instance):
    """
    Test that the Tanimoto similarity is reflexive in practice.
    
    Parameters
    ----------
    tanimoto_instance : Tanimoto
        Instance of Tanimoto similarity
    """
    test_vectors = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.5, 0.5, 0.5],
        [0.1, 0.2, 0.3]
    ]
    
    for vector in test_vectors:
        similarity = tanimoto_instance.calculate(vector, vector)
        assert pytest.approx(similarity, abs=1e-6) == 1.0

@pytest.mark.unit
def test_zero_vector_error(tanimoto_instance):
    """
    Test that the calculate method raises a ValueError for zero vectors.
    
    Parameters
    ----------
    tanimoto_instance : Tanimoto
        Instance of Tanimoto similarity
    """
    zero_vector = [0.0, 0.0, 0.0]
    non_zero_vector = [1.0, 2.0, 3.0]
    
    with pytest.raises(ValueError, match="Tanimoto similarity is undefined for zero vectors"):
        tanimoto_instance.calculate(zero_vector, non_zero_vector)
    
    with pytest.raises(ValueError, match="Tanimoto similarity is undefined for zero vectors"):
        tanimoto_instance.calculate(non_zero_vector, zero_vector)
    
    with pytest.raises(ValueError, match="Tanimoto similarity is undefined for zero vectors"):
        tanimoto_instance.calculate(zero_vector, zero_vector)

@pytest.mark.unit
def test_serialization():
    """Test serialization and deserialization of Tanimoto instances."""
    tanimoto = Tanimoto()
    json_str = tanimoto.model_dump_json()
    
    # Deserialize
    deserialized = Tanimoto.model_validate_json(json_str)
    
    # Check that the deserialized instance has the same properties
    assert deserialized.type == tanimoto.type
    assert deserialized.resource == tanimoto.resource
    assert deserialized.is_bounded == tanimoto.is_bounded
    assert deserialized.lower_bound == tanimoto.lower_bound
    assert deserialized.upper_bound == tanimoto.upper_bound

@pytest.mark.unit
def test_str_representation():
    """Test the string representation of Tanimoto instances."""
    tanimoto = Tanimoto()
    str_repr = str(tanimoto)
    
    assert "Tanimoto" in str_repr
    assert f"bounds: [{tanimoto.lower_bound}, {tanimoto.upper_bound}]" in str_repr