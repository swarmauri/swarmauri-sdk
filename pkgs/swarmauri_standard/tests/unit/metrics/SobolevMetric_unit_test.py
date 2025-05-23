import logging
from typing import Callable, List
from unittest.mock import MagicMock, patch

import pytest

from swarmauri_standard.metrics.SobolevMetric import SobolevMetric
from swarmauri_standard.norms.SobolevNorm import SobolevNorm
from swarmauri_standard.vectors.Vector import Vector

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def sobolev_metric():
    """
    Create a basic SobolevMetric instance for testing.

    Returns
    -------
    SobolevMetric
        An instance of SobolevMetric with default parameters
    """
    return SobolevMetric()


@pytest.fixture
def custom_sobolev_metric():
    """
    Create a SobolevMetric instance with custom parameters.

    Returns
    -------
    SobolevMetric
        An instance of SobolevMetric with custom order and weights
    """
    return SobolevMetric(order=2, weights={0: 1.0, 1: 2.0, 2: 0.5})


@pytest.fixture
def vector_pair():
    """
    Create a pair of real Vector instances for testing.

    Returns
    -------
    tuple
        A pair of Vector instances
    """
    v1 = Vector(value=[1.0, 2.0, 3.0])
    v2 = Vector(value=[4.0, 5.0, 6.0])
    return v1, v2


@pytest.fixture
def mock_matrix():
    """
    Create a mock matrix for testing.

    Returns
    -------
    MagicMock
        A mock object that simulates an IMatrix
    """
    mock = MagicMock()
    mock.shape = (3, 2)
    mock.zeros.return_value = mock  # zeros returns another mock
    return mock


@pytest.fixture
def test_functions() -> List[Callable]:
    """
    Create test functions for distance calculations.

    Returns
    -------
    List[Callable]
        A list of test functions
    """

    def f1(x):
        return x**2

    def f2(x):
        return x**2 + 1

    def f3(x):
        return 2 * x + 3

    # Add derivative methods to functions
    def f1_derivative(x):
        return 2 * x

    def f2_derivative(x):
        return 2 * x

    def f3_derivative(x):
        return 2

    f1.derivative = lambda: f1_derivative
    f2.derivative = lambda: f2_derivative
    f3.derivative = lambda: f3_derivative

    return [f1, f2, f3]


@pytest.mark.unit
def test_initialization_default(sobolev_metric):
    """Test initialization with default parameters."""
    assert sobolev_metric.type == "SobolevMetric"
    assert sobolev_metric.order == 1
    assert sobolev_metric.weights == {0: 1.0, 1: 1.0}
    assert isinstance(sobolev_metric.norm, SobolevNorm)


@pytest.mark.unit
def test_initialization_custom(custom_sobolev_metric):
    """Test initialization with custom parameters."""
    assert custom_sobolev_metric.type == "SobolevMetric"
    assert custom_sobolev_metric.order == 2
    assert custom_sobolev_metric.weights == {0: 1.0, 1: 2.0, 2: 0.5}
    assert isinstance(custom_sobolev_metric.norm, SobolevNorm)
    assert custom_sobolev_metric.norm.order == 2
    assert custom_sobolev_metric.norm.weights == {0: 1.0, 1: 2.0, 2: 0.5}


@pytest.mark.unit
def test_distance_callable_functions(sobolev_metric, test_functions):
    """Test distance calculation between callable functions."""
    f1, f2, _ = test_functions

    # Patch the norm.compute method to return a known value
    with patch.object(sobolev_metric.norm, "compute", return_value=1.0) as mock_compute:
        dist = sobolev_metric.distance(f1, f2)

        # Check that the norm.compute was called once
        mock_compute.assert_called_once()

        # Check that the result is what we expect
        assert dist == 1.0

        # Verify that the function passed to compute is a callable
        args, _ = mock_compute.call_args
        assert callable(args[0])


@pytest.mark.unit
def test_distance_vectors(sobolev_metric, vector_pair):
    """Test distance calculation between vectors."""
    v1, v2 = vector_pair

    # Patch the norm.compute method to return a known value
    with patch.object(sobolev_metric.norm, "compute", return_value=2.5) as mock_compute:
        dist = sobolev_metric.distance(v1, v2)

        # Check that the norm.compute was called once
        mock_compute.assert_called_once()

        # Check that the result is what we expect
        assert dist == 2.5

        # We can't directly verify subtraction was called, but we can check
        # that the diff was passed to compute
        args, _ = mock_compute.call_args
        # Verify the difference vector was passed (don't need to check exact values)
        assert isinstance(args[0], Vector)


@pytest.mark.unit
def test_distance_sequences(sobolev_metric):
    """Test distance calculation between sequences."""
    seq1 = [1, 2, 3]
    seq2 = [4, 5, 6]

    # Patch the norm.compute method to return a known value
    with patch.object(sobolev_metric.norm, "compute", return_value=3.0) as mock_compute:
        dist = sobolev_metric.distance(seq1, seq2)

        # Check that the norm.compute was called once
        mock_compute.assert_called_once()

        # Check that the result is what we expect
        assert dist == 3.0

        # Verify that the difference sequence was passed to compute
        args, _ = mock_compute.call_args
        assert args[0] == [-3, -3, -3]


@pytest.mark.unit
def test_distance_incompatible_types(sobolev_metric):
    """Test distance calculation with incompatible types."""
    with pytest.raises(TypeError):
        sobolev_metric.distance([1, 2, 3], "not_a_sequence")


@pytest.mark.unit
def test_distance_sequences_different_lengths(sobolev_metric):
    """Test distance calculation with sequences of different lengths."""
    seq1 = [1, 2, 3]
    seq2 = [4, 5]

    with pytest.raises(ValueError):
        sobolev_metric.distance(seq1, seq2)


@pytest.mark.unit
def test_distances_matrices(sobolev_metric, mock_matrix):
    """Test distances calculation between matrices."""
    # Set up the distance method to return a fixed value
    with patch.object(sobolev_metric, "distance", return_value=1.5):
        result = sobolev_metric.distances(mock_matrix, mock_matrix)

        # Check that the result is the mock matrix (since zeros returns self)
        assert result is mock_matrix

        # Verify that zeros was called with the right shape
        mock_matrix.zeros.assert_called_once_with((3, 3))


@pytest.mark.unit
def test_distances_vectors(sobolev_metric, vector_pair):
    """Test distances calculation between vectors."""
    v1, v2 = vector_pair

    # Set up the distance method to return a fixed value
    with patch.object(sobolev_metric, "distance", return_value=1.5):
        # Instead, we can directly test the result
        result = sobolev_metric.distances([v1, v2], [v1, v2])

        # Check that the result has the expected structure
        assert isinstance(result, list)
        assert len(result) == 2
        assert len(result[0]) == 2
        assert result[0][0] == 1.5


@pytest.mark.unit
def test_distances_lists_same_length(sobolev_metric):
    """Test distances calculation between lists of the same length."""
    list1 = [1, 2, 3]
    list2 = [4, 5, 6]

    # Set up the distance method to return fixed values
    distance_values = [3.0, 3.0, 3.0]
    with patch.object(sobolev_metric, "distance", side_effect=distance_values):
        result = sobolev_metric.distances(list1, list2)

        # Check that the result is a list of distances
        assert result == distance_values

        # Verify that distance was called for each pair of elements
        assert sobolev_metric.distance.call_count == 3


@pytest.mark.unit
def test_distances_lists_different_length(sobolev_metric):
    """Test distances calculation between lists of different lengths."""
    list1 = [1, 2]
    list2 = [3, 4, 5]

    # Set up the distance method to return fixed values
    with patch.object(sobolev_metric, "distance", return_value=2.5):
        result = sobolev_metric.distances(list1, list2)

        # Check that the result is a matrix of distances
        assert len(result) == 2
        assert len(result[0]) == 3
        assert result[0][0] == 2.5

        # Verify that distance was called for each pair of elements
        assert sobolev_metric.distance.call_count == 6


@pytest.mark.unit
def test_check_non_negativity(sobolev_metric, test_functions):
    """Test the non-negativity axiom check."""
    f1, f2, _ = test_functions

    # Patch the distance method to return a positive value
    with patch.object(sobolev_metric, "distance", return_value=1.5):
        assert sobolev_metric.check_non_negativity(f1, f2) is True

    # Patch the distance method to return zero
    with patch.object(sobolev_metric, "distance", return_value=0.0):
        assert sobolev_metric.check_non_negativity(f1, f2) is True

    # Patch the distance method to return a negative value (should not happen with a proper norm)
    with patch.object(sobolev_metric, "distance", return_value=-0.5):
        assert sobolev_metric.check_non_negativity(f1, f2) is False


@pytest.mark.unit
def test_check_identity_of_indiscernibles(sobolev_metric, test_functions):
    """Test the identity of indiscernibles axiom check."""
    f1, f2, _ = test_functions

    # Patch the distance method to return zero and _are_effectively_equal to return True
    with (
        patch.object(sobolev_metric, "distance", return_value=0.0),
        patch.object(sobolev_metric, "_are_effectively_equal", return_value=True),
    ):
        assert sobolev_metric.check_identity_of_indiscernibles(f1, f1) is True

    # Patch the distance method to return non-zero and _are_effectively_equal to return False
    with (
        patch.object(sobolev_metric, "distance", return_value=1.5),
        patch.object(sobolev_metric, "_are_effectively_equal", return_value=False),
    ):
        assert sobolev_metric.check_identity_of_indiscernibles(f1, f2) is True

    # Patch the distance method to return zero but _are_effectively_equal to return False (inconsistent)
    with (
        patch.object(sobolev_metric, "distance", return_value=0.0),
        patch.object(sobolev_metric, "_are_effectively_equal", return_value=False),
    ):
        assert sobolev_metric.check_identity_of_indiscernibles(f1, f2) is False

    # Patch the distance method to return non-zero but _are_effectively_equal to return True (inconsistent)
    with (
        patch.object(sobolev_metric, "distance", return_value=1.5),
        patch.object(sobolev_metric, "_are_effectively_equal", return_value=True),
    ):
        assert sobolev_metric.check_identity_of_indiscernibles(f1, f2) is False


@pytest.mark.unit
def test_check_symmetry(sobolev_metric, test_functions):
    """Test the symmetry axiom check."""
    f1, f2, _ = test_functions

    # Patch the distance method to return the same value in both directions
    with patch.object(sobolev_metric, "distance", return_value=1.5):
        assert sobolev_metric.check_symmetry(f1, f2) is True

    # Patch the distance method to return different values depending on the order
    distance_values = [1.5, 1.5001]  # Close enough to be considered equal
    with patch.object(sobolev_metric, "distance", side_effect=distance_values):
        assert sobolev_metric.check_symmetry(f1, f2) is True

    # Patch the distance method to return significantly different values
    distance_values = [1.5, 2.0]
    with patch.object(sobolev_metric, "distance", side_effect=distance_values):
        assert sobolev_metric.check_symmetry(f1, f2) is False


@pytest.mark.unit
def test_check_triangle_inequality(sobolev_metric, test_functions):
    """Test the triangle inequality axiom check."""
    f1, f2, f3 = test_functions

    # Patch the distance method to return values that satisfy the triangle inequality
    distance_values = [
        3.0,
        4.0,
        6.0,
    ]  # d(x,y), d(y,z), d(x,z) where d(x,z) < d(x,y) + d(y,z)
    with patch.object(sobolev_metric, "distance", side_effect=distance_values):
        assert sobolev_metric.check_triangle_inequality(f1, f2, f3) is True

    # Patch the distance method to return values at the boundary of the triangle inequality
    distance_values = [
        3.0,
        4.0,
        7.0,
    ]  # d(x,y), d(y,z), d(x,z) where d(x,z) = d(x,y) + d(y,z)
    with patch.object(sobolev_metric, "distance", side_effect=distance_values):
        assert sobolev_metric.check_triangle_inequality(f1, f2, f3) is True

    # Patch the distance method to return values that violate the triangle inequality
    distance_values = [
        3.0,
        4.0,
        8.0,
    ]  # d(x,y), d(y,z), d(x,z) where d(x,z) > d(x,y) + d(y,z)
    with patch.object(sobolev_metric, "distance", side_effect=distance_values):
        assert sobolev_metric.check_triangle_inequality(f1, f2, f3) is False


@pytest.mark.unit
def test_are_effectively_equal_functions(sobolev_metric, test_functions):
    """Test the _are_effectively_equal method with functions."""
    f1, f2, _ = test_functions

    # Same function should be equal to itself
    assert sobolev_metric._are_effectively_equal(f1, f1) is True

    # Different functions should not be equal
    assert sobolev_metric._are_effectively_equal(f1, f2) is False


@pytest.mark.unit
def test_are_effectively_equal_sequences(sobolev_metric):
    """Test the _are_effectively_equal method with sequences."""
    # Identical sequences should be equal
    assert sobolev_metric._are_effectively_equal([1, 2, 3], [1, 2, 3]) is True

    # Different sequences should not be equal
    assert sobolev_metric._are_effectively_equal([1, 2, 3], [1, 2, 4]) is False

    # Sequences with different lengths should not be equal
    assert sobolev_metric._are_effectively_equal([1, 2, 3], [1, 2]) is False


@pytest.mark.unit
def test_serialization(sobolev_metric, custom_sobolev_metric):
    """Test serialization and deserialization of SobolevMetric."""
    # Serialize and deserialize the default metric
    json_str = sobolev_metric.model_dump_json()
    deserialized = SobolevMetric.model_validate_json(json_str)

    assert deserialized.type == "SobolevMetric"
    assert deserialized.order == 1
    assert deserialized.weights == {0: 1.0, 1: 1.0}

    # Serialize and deserialize the custom metric
    json_str = custom_sobolev_metric.model_dump_json()
    deserialized = SobolevMetric.model_validate_json(json_str)

    assert deserialized.type == "SobolevMetric"
    assert deserialized.order == 2
    assert deserialized.weights == {0: 1.0, 1: 2.0, 2: 0.5}
