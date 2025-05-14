import pytest
import logging
import math
from typing import Callable
from unittest.mock import Mock

from swarmauri_core.similarities.ISimilarity import ComparableType
from swarmauri_standard.similarities.ExponentialDistanceSimilarity import ExponentialDistanceSimilarity

# Set up logger for tests
logger = logging.getLogger(__name__)


@pytest.fixture
def euclidean_distance() -> Callable[[ComparableType, ComparableType], float]:
    """
    Fixture providing a simple Euclidean distance function for testing.

    Returns
    -------
    Callable
        Function that calculates Euclidean distance between two points
    """
    def distance(x, y):
        if not isinstance(x, (list, tuple)) or not isinstance(y, (list, tuple)):
            raise TypeError("Points must be lists or tuples")
        if len(x) != len(y):
            raise ValueError("Points must have the same dimension")
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(x, y)))
    
    return distance


@pytest.fixture
def manhattan_distance() -> Callable[[ComparableType, ComparableType], float]:
    """
    Fixture providing a Manhattan distance function for testing.

    Returns
    -------
    Callable
        Function that calculates Manhattan distance between two points
    """
    def distance(x, y):
        if not isinstance(x, (list, tuple)) or not isinstance(y, (list, tuple)):
            raise TypeError("Points must be lists or tuples")
        if len(x) != len(y):
            raise ValueError("Points must have the same dimension")
        return sum(abs(a - b) for a, b in zip(x, y))
    
    return distance


@pytest.fixture
def exp_similarity(euclidean_distance) -> ExponentialDistanceSimilarity:
    """
    Fixture providing an ExponentialDistanceSimilarity instance with default alpha.

    Parameters
    ----------
    euclidean_distance : Callable
        Distance function from fixture

    Returns
    -------
    ExponentialDistanceSimilarity
        Instance with default alpha=1.0
    """
    return ExponentialDistanceSimilarity(distance_func=euclidean_distance)


@pytest.fixture
def exp_similarity_custom_alpha(euclidean_distance) -> ExponentialDistanceSimilarity:
    """
    Fixture providing an ExponentialDistanceSimilarity instance with custom alpha.

    Parameters
    ----------
    euclidean_distance : Callable
        Distance function from fixture

    Returns
    -------
    ExponentialDistanceSimilarity
        Instance with alpha=0.5
    """
    return ExponentialDistanceSimilarity(distance_func=euclidean_distance, alpha=0.5)


@pytest.mark.unit
def test_type():
    """Test that the type attribute is correctly set."""
    assert ExponentialDistanceSimilarity.type == "ExponentialDistanceSimilarity"


@pytest.mark.unit
def test_initialization(euclidean_distance):
    """Test that the similarity measure can be properly initialized."""
    sim = ExponentialDistanceSimilarity(distance_func=euclidean_distance, alpha=1.5)
    assert sim.alpha == 1.5
    assert sim.distance_func == euclidean_distance


@pytest.mark.unit
def test_initialization_default_alpha(euclidean_distance):
    """Test that the default alpha value is used when not specified."""
    sim = ExponentialDistanceSimilarity(distance_func=euclidean_distance)
    assert sim.alpha == 1.0


@pytest.mark.unit
def test_initialization_invalid_alpha(euclidean_distance):
    """Test that initializing with a non-positive alpha raises ValueError."""
    with pytest.raises(ValueError, match="alpha must be positive"):
        ExponentialDistanceSimilarity(distance_func=euclidean_distance, alpha=0)
    
    with pytest.raises(ValueError, match="alpha must be positive"):
        ExponentialDistanceSimilarity(distance_func=euclidean_distance, alpha=-1.0)


@pytest.mark.unit
def test_initialization_invalid_distance_func():
    """Test that initializing with a non-callable distance function raises ValueError."""
    with pytest.raises(ValueError, match="distance_func must be callable"):
        ExponentialDistanceSimilarity(distance_func="not_callable")


@pytest.mark.unit
def test_similarity_identical_points(exp_similarity):
    """Test similarity calculation for identical points."""
    point = [1, 2, 3]
    similarity = exp_similarity.similarity(point, point)
    # For identical points, distance is 0, so similarity should be e^0 = 1
    assert similarity == 1.0


@pytest.mark.unit
def test_similarity_different_points(exp_similarity):
    """Test similarity calculation for different points."""
    point1 = [0, 0, 0]
    point2 = [1, 0, 0]
    # Distance is 1, so similarity should be e^-1
    expected = math.exp(-1)
    similarity = exp_similarity.similarity(point1, point2)
    assert similarity == pytest.approx(expected)


@pytest.mark.unit
def test_similarity_with_custom_alpha(exp_similarity_custom_alpha):
    """Test similarity calculation with custom alpha value."""
    point1 = [0, 0, 0]
    point2 = [1, 0, 0]
    # Distance is 1, alpha is 0.5, so similarity should be e^(-0.5*1)
    expected = math.exp(-0.5)
    similarity = exp_similarity_custom_alpha.similarity(point1, point2)
    assert similarity == pytest.approx(expected)


@pytest.mark.unit
def test_similarity_error_handling(exp_similarity):
    """Test that errors from the distance function are properly propagated."""
    with pytest.raises(TypeError, match="Points must be lists or tuples"):
        exp_similarity.similarity("not_a_point", [1, 2, 3])
    
    with pytest.raises(ValueError, match="Points must have the same dimension"):
        exp_similarity.similarity([1, 2], [1, 2, 3])


@pytest.mark.unit
def test_similarities_calculation(exp_similarity):
    """Test calculation of similarities between one point and multiple others."""
    reference = [0, 0, 0]
    points = [[1, 0, 0], [0, 2, 0], [0, 0, 3]]
    
    # Expected similarities: e^-1, e^-2, e^-3
    expected = [math.exp(-1), math.exp(-2), math.exp(-3)]
    
    similarities = exp_similarity.similarities(reference, points)
    assert len(similarities) == 3
    assert similarities == pytest.approx(expected)


@pytest.mark.unit
def test_similarities_empty_list(exp_similarity):
    """Test calculation of similarities with empty list."""
    reference = [0, 0, 0]
    points = []
    
    similarities = exp_similarity.similarities(reference, points)
    assert similarities == []


@pytest.mark.unit
def test_similarities_error_handling(exp_similarity):
    """Test that errors in similarities calculation are properly propagated."""
    reference = [0, 0, 0]
    points = [[1, 0, 0], "not_a_point", [0, 0, 3]]
    
    with pytest.raises(TypeError, match="Points must be lists or tuples"):
        exp_similarity.similarities(reference, points)


@pytest.mark.unit
def test_dissimilarity(exp_similarity):
    """Test dissimilarity calculation."""
    point1 = [0, 0, 0]
    point2 = [1, 0, 0]
    
    # Similarity is e^-1, so dissimilarity is 1-e^-1
    expected = 1 - math.exp(-1)
    
    dissimilarity = exp_similarity.dissimilarity(point1, point2)
    assert dissimilarity == pytest.approx(expected)


@pytest.mark.unit
def test_check_bounded(exp_similarity):
    """Test that the similarity measure correctly reports being bounded."""
    assert exp_similarity.check_bounded() is True


@pytest.mark.unit
def test_negative_distance_handling():
    """Test handling of negative distances."""
    # Create a distance function that returns negative values
    def negative_distance(x, y):
        return -1.0
    
    sim = ExponentialDistanceSimilarity(distance_func=negative_distance)
    
    with pytest.raises(ValueError, match="Distance function returned negative value"):
        sim.similarity([1, 2], [3, 4])


@pytest.mark.unit
def test_to_dict(exp_similarity):
    """Test conversion to dictionary representation."""
    data = exp_similarity.to_dict()
    
    assert data["type"] == "ExponentialDistanceSimilarity"
    assert data["alpha"] == 1.0
    assert "distance_func_info" in data


@pytest.mark.unit
def test_from_dict():
    """Test creation from dictionary representation."""
    distance_func = Mock()
    data = {
        "type": "ExponentialDistanceSimilarity",
        "alpha": 2.5
    }
    
    sim = ExponentialDistanceSimilarity.from_dict(data, distance_func=distance_func)
    
    assert sim.type == "ExponentialDistanceSimilarity"
    assert sim.alpha == 2.5
    assert sim.distance_func == distance_func


@pytest.mark.unit
def test_from_dict_missing_distance_func():
    """Test that from_dict raises an error when distance_func is not provided."""
    data = {
        "type": "ExponentialDistanceSimilarity",
        "alpha": 1.0
    }
    
    with pytest.raises(ValueError, match="distance_func must be provided"):
        ExponentialDistanceSimilarity.from_dict(data)


@pytest.mark.unit
@pytest.mark.parametrize("alpha,point1,point2,expected", [
    (1.0, [0, 0], [3, 4], math.exp(-5)),  # distance = 5
    (0.5, [0, 0], [3, 4], math.exp(-2.5)),  # distance = 5, alpha = 0.5
    (2.0, [1, 1], [2, 2], math.exp(-2.83)),  # distance ≈ 1.414, alpha = 2
])
def test_similarity_parameterized(euclidean_distance, alpha, point1, point2, expected):
    """Test similarity calculation with various parameters."""
    sim = ExponentialDistanceSimilarity(distance_func=euclidean_distance, alpha=alpha)
    result = sim.similarity(point1, point2)
    assert result == pytest.approx(expected, abs=1e-2)


@pytest.mark.unit
def test_with_different_distance_functions(euclidean_distance, manhattan_distance):
    """Test similarity calculation with different distance functions."""
    points = ([0, 0], [1, 1])
    
    # Euclidean distance between points is sqrt(2) ≈ 1.414
    euclidean_sim = ExponentialDistanceSimilarity(distance_func=euclidean_distance)
    euclidean_result = euclidean_sim.similarity(*points)
    assert euclidean_result == pytest.approx(math.exp(-math.sqrt(2)))
    
    # Manhattan distance between points is 2
    manhattan_sim = ExponentialDistanceSimilarity(distance_func=manhattan_distance)
    manhattan_result = manhattan_sim.similarity(*points)
    assert manhattan_result == pytest.approx(math.exp(-2))