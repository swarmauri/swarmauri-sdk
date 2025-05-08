import pytest
import logging
from typing import List, Any
from swarmauri_standard.pseudometrics.ZeroPseudometric import ZeroPseudometric

# Set up logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def zero_pseudometric():
    """
    Fixture that provides a ZeroPseudometric instance for testing.
    
    Returns:
        ZeroPseudometric: An instance of the ZeroPseudometric class
    """
    return ZeroPseudometric()


@pytest.mark.unit
def test_type():
    """Test that the type attribute is correctly set."""
    assert ZeroPseudometric.type == "ZeroPseudometric"


@pytest.mark.unit
def test_resource():
    """Test that the resource attribute is correctly inherited."""
    assert ZeroPseudometric.resource == "Pseudometric"


@pytest.mark.unit
def test_initialization():
    """Test that the ZeroPseudometric initializes correctly."""
    zero_metric = ZeroPseudometric()
    assert isinstance(zero_metric, ZeroPseudometric)


@pytest.mark.unit
def test_distance(zero_pseudometric):
    """Test that the distance method always returns zero."""
    # Test with various data types
    test_cases = [
        (1, 2),
        ("a", "b"),
        ([1, 2, 3], [4, 5, 6]),
        ({"key": "value"}, {"another_key": "another_value"}),
        (None, None),
        (True, False)
    ]
    
    for x, y in test_cases:
        distance = zero_pseudometric.distance(x, y)
        assert distance == 0.0
        assert isinstance(distance, float)


@pytest.mark.unit
@pytest.mark.parametrize("xs,ys", [
    ([1, 2, 3], [4, 5, 6]),
    (["a", "b", "c"], ["d", "e", "f"]),
    ([True, False, True], [False, True, False]),
    ([None, None], [None, None])
])
def test_batch_distance(zero_pseudometric, xs, ys):
    """Test that the batch_distance method returns zeros for all pairs."""
    distances = zero_pseudometric.batch_distance(xs, ys)
    assert len(distances) == len(xs)
    assert all(d == 0.0 for d in distances)
    assert all(isinstance(d, float) for d in distances)


@pytest.mark.unit
def test_batch_distance_different_lengths(zero_pseudometric):
    """Test that batch_distance raises ValueError for different length inputs."""
    with pytest.raises(ValueError) as excinfo:
        zero_pseudometric.batch_distance([1, 2, 3], [4, 5])
    
    assert "Input lists must have the same length" in str(excinfo.value)


@pytest.mark.unit
@pytest.mark.parametrize("points,expected_size", [
    ([1, 2, 3, 4], 4),
    (["a", "b"], 2),
    ([], 0),
    ([None], 1)
])
def test_pairwise_distances(zero_pseudometric, points, expected_size):
    """Test that pairwise_distances returns a matrix of zeros with correct dimensions."""
    distances = zero_pseudometric.pairwise_distances(points)
    
    # Check matrix dimensions
    assert len(distances) == expected_size
    for row in distances:
        assert len(row) == expected_size
    
    # Check all values are zero
    for i in range(expected_size):
        for j in range(expected_size):
            assert distances[i][j] == 0.0
            assert isinstance(distances[i][j], float)


@pytest.mark.unit
def test_serialization():
    """Test serialization and deserialization of ZeroPseudometric."""
    zero_metric = ZeroPseudometric()
    serialized = zero_metric.model_dump_json()
    deserialized = ZeroPseudometric.model_validate_json(serialized)
    
    assert isinstance(deserialized, ZeroPseudometric)
    assert deserialized.type == zero_metric.type


@pytest.mark.unit
def test_pseudometric_axioms(zero_pseudometric):
    """Test that ZeroPseudometric satisfies the pseudometric axioms."""
    # Test points
    a, b, c = "point_a", "point_b", "point_c"
    
    # Non-negativity: d(x,y) ≥ 0
    assert zero_pseudometric.distance(a, b) >= 0
    
    # Symmetry: d(x,y) = d(y,x)
    assert zero_pseudometric.distance(a, b) == zero_pseudometric.distance(b, a)
    
    # Identity of indiscernibles (for pseudometrics, only one direction is required):
    # If x=y, then d(x,y)=0 (but the converse is not necessarily true)
    assert zero_pseudometric.distance(a, a) == 0
    
    # Triangle inequality: d(x,z) ≤ d(x,y) + d(y,z)
    assert (zero_pseudometric.distance(a, c) <= 
            zero_pseudometric.distance(a, b) + zero_pseudometric.distance(b, c))