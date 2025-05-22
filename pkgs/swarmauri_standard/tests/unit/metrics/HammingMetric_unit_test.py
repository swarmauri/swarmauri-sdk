import logging
from typing import List, Tuple

import numpy as np
import pytest

from swarmauri_standard.metrics.HammingMetric import HammingMetric

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Fixtures for test data
@pytest.fixture
def binary_sequences() -> Tuple[List[int], List[int]]:
    """
    Fixture providing two binary sequences for testing.

    Returns
    -------
    Tuple[List[int], List[int]]
        Two binary sequences of equal length
    """
    return [0, 1, 0, 1, 0], [0, 0, 1, 1, 0]


@pytest.fixture
def string_sequences() -> Tuple[str, str]:
    """
    Fixture providing two string sequences for testing.

    Returns
    -------
    Tuple[str, str]
        Two string sequences of equal length
    """
    return "karolin", "kathrin"


@pytest.fixture
def sequence_collections() -> Tuple[List[List[int]], List[List[int]]]:
    """
    Fixture providing collections of sequences for testing.

    Returns
    -------
    Tuple[List[List[int]], List[List[int]]]
        Two collections of binary sequences
    """
    return [[0, 1, 0], [1, 1, 0], [0, 0, 1]], [[1, 1, 1], [0, 0, 0], [1, 0, 1]]


@pytest.fixture
def numpy_arrays() -> Tuple[np.ndarray, np.ndarray]:
    """
    Fixture providing numpy arrays for testing.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        Two numpy arrays of equal shape
    """
    return np.array([[0, 1, 0], [1, 1, 0]]), np.array([[1, 1, 1], [0, 0, 0]])


@pytest.fixture
def hamming_metric() -> HammingMetric:
    """
    Fixture providing a HammingMetric instance.

    Returns
    -------
    HammingMetric
        An instance of the HammingMetric class
    """
    return HammingMetric()


# Test cases
@pytest.mark.unit
def test_type_attribute(hamming_metric):
    """Test that the type attribute is correctly set."""
    assert hamming_metric.type == "HammingMetric"


@pytest.mark.unit
def test_resource_attribute(hamming_metric):
    """Test that the resource attribute is correctly set."""
    assert hamming_metric.resource == "Metric"


@pytest.mark.unit
def test_distance_binary_sequences(hamming_metric, binary_sequences):
    """Test Hamming distance calculation with binary sequences."""
    seq1, seq2 = binary_sequences
    distance = hamming_metric.distance(seq1, seq2)

    # Expected distance: positions 1 and 2 differ
    assert distance == 2.0
    assert isinstance(distance, float)


@pytest.mark.unit
def test_distance_string_sequences(hamming_metric, string_sequences):
    """Test Hamming distance calculation with string sequences."""
    str1, str2 = string_sequences
    distance = hamming_metric.distance(str1, str2)

    # Expected distance: 3 characters differ
    assert distance == 3.0
    assert isinstance(distance, float)


@pytest.mark.unit
def test_distance_unequal_length(hamming_metric):
    """Test that ValueError is raised when sequences have different lengths."""
    seq1 = [0, 1, 0]
    seq2 = [0, 1, 0, 1]

    with pytest.raises(ValueError) as excinfo:
        hamming_metric.distance(seq1, seq2)

    assert "Sequences must have equal length" in str(excinfo.value)


@pytest.mark.unit
def test_distance_invalid_types(hamming_metric):
    """Test that TypeError is raised when inputs are not sequences."""
    with pytest.raises(TypeError) as excinfo:
        hamming_metric.distance(123, 456)

    assert "Inputs must be sequences" in str(excinfo.value)


@pytest.mark.unit
def test_distances_single_sequences(hamming_metric, binary_sequences):
    """Test distances calculation with single sequences."""
    seq1, seq2 = binary_sequences
    distances = hamming_metric.distances(seq1, seq2)

    assert distances == [2.0]
    assert isinstance(distances, list)


@pytest.mark.unit
def test_distances_collections(hamming_metric, sequence_collections):
    """Test distances calculation with collections of sequences."""
    coll1, coll2 = sequence_collections
    distances = hamming_metric.distances(coll1, coll2)

    # Correct expected distances matrix
    expected = [
        [2.0, 1.0, 3.0],  # distances from coll1[0] to each seq in coll2
        [1.0, 2.0, 2.0],  # distances from coll1[1] to each seq in coll2
        [2.0, 1.0, 1.0],  # distances from coll1[2] to each seq in coll2
    ]

    assert distances == expected


@pytest.mark.unit
def test_distances_numpy_arrays(hamming_metric, numpy_arrays):
    """Test distances calculation with numpy arrays."""
    arr1, arr2 = numpy_arrays
    distances = hamming_metric.distances(arr1, arr2)

    # Corrected expected distances matrix
    expected = [
        [2.0, 1.0],  # distances from arr1[0] to each row in arr2
        [1.0, 2.0],  # distances from arr1[1] to each row in arr2
    ]

    assert distances == expected


@pytest.mark.unit
def test_distances_mixed_inputs(hamming_metric):
    """Test distances calculation with mixed input types."""
    seq = [0, 1, 0]
    coll = [[0, 0, 0], [1, 1, 1]]

    # Single sequence to collection
    distances1 = hamming_metric.distances(seq, coll)
    assert distances1 == [1.0, 2.0]

    # Collection to single sequence
    distances2 = hamming_metric.distances(coll, seq)
    assert distances2 == [1.0, 2.0]


@pytest.mark.unit
def test_check_non_negativity(hamming_metric, binary_sequences):
    """Test that Hamming metric satisfies non-negativity axiom."""
    seq1, seq2 = binary_sequences
    assert hamming_metric.check_non_negativity(seq1, seq2) is True


@pytest.mark.unit
def test_check_identity_of_indiscernibles(hamming_metric):
    """Test that Hamming metric satisfies identity of indiscernibles axiom."""
    seq1 = [0, 1, 0, 1]
    seq2 = [0, 1, 0, 1]  # identical to seq1
    seq3 = [0, 0, 0, 1]  # different from seq1

    assert hamming_metric.check_identity_of_indiscernibles(seq1, seq2) is True
    assert hamming_metric.check_identity_of_indiscernibles(seq1, seq3) is True


@pytest.mark.unit
def test_check_symmetry(hamming_metric, binary_sequences):
    """Test that Hamming metric satisfies symmetry axiom."""
    seq1, seq2 = binary_sequences
    assert hamming_metric.check_symmetry(seq1, seq2) is True


@pytest.mark.unit
def test_check_triangle_inequality(hamming_metric):
    """Test that Hamming metric satisfies triangle inequality axiom."""
    seq1 = [0, 1, 0, 1]
    seq2 = [1, 1, 0, 0]
    seq3 = [1, 0, 1, 0]

    assert hamming_metric.check_triangle_inequality(seq1, seq2, seq3) is True


@pytest.mark.unit
@pytest.mark.parametrize(
    "seq1,seq2,expected",
    [
        ([0, 1, 0, 1], [0, 1, 0, 1], 0.0),  # identical
        ([0, 1, 0, 1], [1, 1, 0, 1], 1.0),  # one difference
        ([0, 1, 0, 1], [1, 0, 1, 0], 4.0),  # all different
        ("abcd", "abcd", 0.0),  # identical strings
        ("abcd", "abce", 1.0),  # one char different
        ("abcd", "wxyz", 4.0),  # all chars different
    ],
)
def test_distance_parameterized(hamming_metric, seq1, seq2, expected):
    """Test Hamming distance calculation with various sequence pairs."""
    distance = hamming_metric.distance(seq1, seq2)
    assert distance == expected


@pytest.mark.unit
def test_serialization(hamming_metric):
    """Test serialization and deserialization of HammingMetric."""
    # Serialize to JSON
    json_data = hamming_metric.model_dump_json()

    # Deserialize from JSON
    deserialized = HammingMetric.model_validate_json(json_data)

    # Check type
    assert isinstance(deserialized, HammingMetric)
    assert deserialized.type == "HammingMetric"

    # Verify functionality is preserved
    seq1, seq2 = [0, 1, 0], [1, 1, 0]
    assert deserialized.distance(seq1, seq2) == hamming_metric.distance(seq1, seq2)
