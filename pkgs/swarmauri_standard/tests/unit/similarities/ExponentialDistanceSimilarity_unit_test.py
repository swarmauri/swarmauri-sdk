import pytest
import logging
import math
from typing import Any, Callable, List, Tuple
import numpy as np

from swarmauri_standard.similarities.ExponentialDistanceSimilarity import ExponentialDistanceSimilarity

# Set up logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Define fixtures for common test data
@pytest.fixture
def euclidean_distance() -> Callable[[List[float], List[float]], float]:
    """
    Fixture providing a Euclidean distance function.
    
    Returns
    -------
    Callable
        Function that calculates Euclidean distance between two vectors
    """
    def distance(a: List[float], b: List[float]) -> float:
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))
    
    return distance


@pytest.fixture
def manhattan_distance() -> Callable[[List[float], List[float]], float]:
    """
    Fixture providing a Manhattan distance function.
    
    Returns
    -------
    Callable
        Function that calculates Manhattan distance between two vectors
    """
    def distance(a: List[float], b: List[float]) -> float:
        return sum(abs(x - y) for x, y in zip(a, b))
    
    return distance


@pytest.fixture
def default_similarity(euclidean_distance) -> ExponentialDistanceSimilarity:
    """
    Fixture providing a default ExponentialDistanceSimilarity instance.
    
    Parameters
    ----------
    euclidean_distance : Callable
        Euclidean distance function from fixture
    
    Returns
    -------
    ExponentialDistanceSimilarity
        A default instance with Euclidean distance and decay_factor=1.0
    """
    return ExponentialDistanceSimilarity(distance_function=euclidean_distance, decay_factor=1.0)


# Basic tests for initialization and attributes
@pytest.mark.unit
def test_initialization(euclidean_distance):
    """Test that ExponentialDistanceSimilarity initializes with correct attributes."""
    # Test with default parameters
    similarity = ExponentialDistanceSimilarity(distance_function=euclidean_distance)
    
    assert similarity.distance_function == euclidean_distance
    assert similarity.decay_factor == 1.0
    assert similarity.is_bounded is True
    assert similarity.lower_bound == 0.0
    assert similarity.upper_bound == 1.0
    assert similarity.type == "ExponentialDistanceSimilarity"


@pytest.mark.unit
def test_custom_initialization(manhattan_distance):
    """Test initialization with custom parameters."""
    similarity = ExponentialDistanceSimilarity(
        distance_function=manhattan_distance,
        decay_factor=2.5,
        is_bounded=False,
        lower_bound=-1.0,  # Should not matter if is_bounded=False
        upper_bound=2.0    # Should not matter if is_bounded=False
    )
    
    assert similarity.distance_function == manhattan_distance
    assert similarity.decay_factor == 2.5
    assert similarity.is_bounded is False
    assert similarity.lower_bound == -1.0
    assert similarity.upper_bound == 2.0


# Tests for calculation functionality
@pytest.mark.unit
@pytest.mark.parametrize("a, b, expected_similarity", [
    ([0, 0], [0, 0], 1.0),  # Same point
    ([0, 0], [1, 0], math.exp(-1.0)),  # Distance of 1
    ([0, 0], [3, 4], math.exp(-5.0)),  # Distance of 5
])
def test_calculate_euclidean(euclidean_distance, a, b, expected_similarity):
    """Test similarity calculation using Euclidean distance."""
    similarity = ExponentialDistanceSimilarity(distance_function=euclidean_distance, decay_factor=1.0)
    result = similarity.calculate(a, b)
    
    assert pytest.approx(result) == expected_similarity


@pytest.mark.unit
@pytest.mark.parametrize("a, b, decay_factor, expected_similarity", [
    ([0, 0], [1, 1], 0.5, math.exp(-0.5 * math.sqrt(2))),  # Lower decay factor
    ([0, 0], [1, 1], 2.0, math.exp(-2.0 * math.sqrt(2))),  # Higher decay factor
])
def test_decay_factor_effect(euclidean_distance, a, b, decay_factor, expected_similarity):
    """Test the effect of different decay factors on similarity calculation."""
    similarity = ExponentialDistanceSimilarity(
        distance_function=euclidean_distance, 
        decay_factor=decay_factor
    )
    result = similarity.calculate(a, b)
    
    assert pytest.approx(result) == expected_similarity


@pytest.mark.unit
def test_negative_distance_handling():
    """Test handling of negative distances by taking absolute value."""
    # Define a distance function that can return negative values
    def negative_distance(a: Any, b: Any) -> float:
        return -5.0  # Always returns negative distance
    
    similarity = ExponentialDistanceSimilarity(distance_function=negative_distance)
    result = similarity.calculate(None, None)  # Arguments don't matter
    
    # Should use absolute value of distance
    assert pytest.approx(result) == math.exp(-5.0)


# Tests for mathematical properties
@pytest.mark.unit
def test_reflexivity(default_similarity):
    """Test the reflexivity property (sim(a,a) = 1)."""
    a = [1, 2, 3]
    result = default_similarity.calculate(a, a)
    
    assert pytest.approx(result) == 1.0
    assert default_similarity.is_reflexive() is True


@pytest.mark.unit
def test_symmetry(default_similarity):
    """Test the symmetry property (sim(a,b) = sim(b,a))."""
    a = [1, 2, 3]
    b = [4, 5, 6]
    
    result_ab = default_similarity.calculate(a, b)
    result_ba = default_similarity.calculate(b, a)
    
    assert pytest.approx(result_ab) == result_ba
    assert default_similarity.is_symmetric() is True


# Test with various data types
@pytest.mark.unit
def test_with_numpy_arrays():
    """Test similarity calculation with numpy arrays."""
    def numpy_distance(a: np.ndarray, b: np.ndarray) -> float:
        return float(np.linalg.norm(a - b))
    
    similarity = ExponentialDistanceSimilarity(distance_function=numpy_distance)
    
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([4.0, 5.0, 6.0])
    
    result = similarity.calculate(a, b)
    expected = math.exp(-numpy_distance(a, b))
    
    assert pytest.approx(result) == expected


@pytest.mark.unit
def test_with_custom_objects():
    """Test similarity calculation with custom objects."""
    class Point:
        def __init__(self, x, y):
            self.x = x
            self.y = y
    
    def point_distance(a: Point, b: Point) -> float:
        return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)
    
    similarity = ExponentialDistanceSimilarity(distance_function=point_distance)
    
    a = Point(0, 0)
    b = Point(3, 4)
    
    result = similarity.calculate(a, b)
    expected = math.exp(-5.0)  # Distance is 5
    
    assert pytest.approx(result) == expected


# Test error handling
@pytest.mark.unit
def test_error_handling():
    """Test error handling during calculation."""
    def faulty_distance(a: Any, b: Any) -> float:
        raise ValueError("Simulated error in distance function")
    
    similarity = ExponentialDistanceSimilarity(distance_function=faulty_distance)
    
    with pytest.raises(ValueError):
        similarity.calculate("a", "b")


# Test string representation
@pytest.mark.unit
def test_string_representation(default_similarity):
    """Test the string representation of the similarity measure."""
    string_repr = str(default_similarity)
    
    assert "ExponentialDistanceSimilarity" in string_repr
    assert "decay factor: 1.0" in string_repr
    assert "bounds: [0.0, 1.0]" in string_repr


@pytest.mark.unit
def test_unbounded_string_representation():
    """Test string representation for unbounded similarity."""
    similarity = ExponentialDistanceSimilarity(
        distance_function=lambda a, b: 0,
        is_bounded=False
    )
    
    string_repr = str(similarity)
    
    assert "unbounded" in string_repr


# Test serialization
@pytest.mark.unit
def test_serialization_deserialization(default_similarity):
    """Test serialization and deserialization."""
    # Serialize to JSON
    json_data = default_similarity.model_dump_json()
    
    # Deserialize from JSON
    deserialized = ExponentialDistanceSimilarity.model_validate_json(json_data)
    
    # Check that the deserialized object has the same attributes
    assert deserialized.decay_factor == default_similarity.decay_factor
    assert deserialized.is_bounded == default_similarity.is_bounded
    assert deserialized.lower_bound == default_similarity.lower_bound
    assert deserialized.upper_bound == default_similarity.upper_bound
    
    # Note: We can't directly compare the distance_function as it's not serializable
    # But we can check that it's callable
    assert callable(deserialized.distance_function)