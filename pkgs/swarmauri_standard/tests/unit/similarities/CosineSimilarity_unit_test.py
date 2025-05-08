import pytest
import numpy as np
import logging
from typing import List, Tuple, Any
from swarmauri_standard.similarities.CosineSimilarity import CosineSimilarity

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
def cosine_similarity():
    """
    Fixture that returns a CosineSimilarity instance.
    
    Returns
    -------
    CosineSimilarity
        A CosineSimilarity instance for testing
    """
    return CosineSimilarity()

@pytest.mark.unit
def test_cosine_similarity_initialization():
    """Test proper initialization of CosineSimilarity."""
    similarity = CosineSimilarity()
    
    assert similarity.type == "CosineSimilarity"
    assert similarity.resource == "Similarity"
    assert similarity.is_bounded is True
    assert similarity.lower_bound == 0.0
    assert similarity.upper_bound == 1.0

@pytest.mark.unit
def test_cosine_similarity_reflexive(cosine_similarity):
    """Test reflexivity property of cosine similarity."""
    assert cosine_similarity.is_reflexive() is True

@pytest.mark.unit
def test_cosine_similarity_symmetric(cosine_similarity):
    """Test symmetry property of cosine similarity."""
    assert cosine_similarity.is_symmetric() is True

@pytest.mark.unit
@pytest.mark.parametrize("vector_a, vector_b, expected", [
    ([1, 0, 0], [1, 0, 0], 1.0),                  # Identical vectors
    ([1, 0, 0], [0, 1, 0], 0.0),                  # Orthogonal vectors
    ([1, 1, 0], [1, 0, 0], 0.7071067811865475),   # 45-degree angle
    ([1, 2, 3], [4, 5, 6], 0.9746318461970762),   # Arbitrary vectors
    (np.array([1, 0, 0]), np.array([1, 0, 0]), 1.0),  # NumPy arrays
    ([0.5, 0.5], [0.5, 0.5], 1.0),                # Identical normalized vectors
])
def test_cosine_similarity_calculate(cosine_similarity, vector_a, vector_b, expected):
    """
    Test cosine similarity calculation with various vector pairs.
    
    Parameters
    ----------
    cosine_similarity : CosineSimilarity
        The similarity instance
    vector_a : List[float] or np.ndarray
        First vector
    vector_b : List[float] or np.ndarray
        Second vector
    expected : float
        Expected similarity value
    """
    result = cosine_similarity.calculate(vector_a, vector_b)
    assert np.isclose(result, expected, rtol=1e-10)

@pytest.mark.unit
def test_cosine_similarity_handles_numerical_precision():
    """Test that cosine similarity handles numerical precision issues."""
    # Create a case where floating point might result in value slightly > 1
    similarity = CosineSimilarity()
    
    # These vectors are almost identical but with slight numerical differences
    a = [0.7071067811865475, 0.7071067811865475]
    b = [0.7071067811865474, 0.7071067811865477]
    
    result = similarity.calculate(a, b)
    assert 0.0 <= result <= 1.0
    assert np.isclose(result, 1.0, rtol=1e-10)

@pytest.mark.unit
def test_cosine_similarity_zero_vector():
    """Test that cosine similarity raises an error for zero vectors."""
    similarity = CosineSimilarity()
    
    with pytest.raises(ValueError) as excinfo:
        similarity.calculate([0, 0, 0], [1, 2, 3])
    
    assert "zero-length vectors" in str(excinfo.value)
    
    with pytest.raises(ValueError) as excinfo:
        similarity.calculate([1, 2, 3], [0, 0, 0])
    
    assert "zero-length vectors" in str(excinfo.value)

@pytest.mark.unit
def test_cosine_similarity_serialization():
    """Test serialization and deserialization of CosineSimilarity."""
    similarity = CosineSimilarity()
    
    # Serialize to JSON
    json_data = similarity.model_dump_json()
    
    # Deserialize from JSON
    deserialized = CosineSimilarity.model_validate_json(json_data)
    
    # Check that the deserialized object has the same properties
    assert deserialized.type == similarity.type
    assert deserialized.resource == similarity.resource
    assert deserialized.is_bounded == similarity.is_bounded
    assert deserialized.lower_bound == similarity.lower_bound
    assert deserialized.upper_bound == similarity.upper_bound

@pytest.mark.unit
def test_cosine_similarity_with_different_dimensions():
    """Test that cosine similarity works with vectors of different dimensions."""
    similarity = CosineSimilarity()
    
    # This should work without error as numpy.dot handles broadcasting
    with pytest.raises(ValueError):
        similarity.calculate([1, 2, 3], [1, 2, 3, 4])

@pytest.mark.unit
def test_cosine_similarity_with_float_lists():
    """Test cosine similarity with lists of floats."""
    similarity = CosineSimilarity()
    
    a = [0.1, 0.2, 0.3]
    b = [0.4, 0.5, 0.6]
    
    result = similarity.calculate(a, b)
    expected = 0.9746318461970762
    
    assert np.isclose(result, expected, rtol=1e-10)