import pytest
import numpy as np
import logging
from typing import List, Tuple, Any
from swarmauri_standard.metrics.HammingMetric import HammingMetric

# Configure logger for tests
logger = logging.getLogger(__name__)

# Fixtures for common test data
@pytest.fixture
def binary_sequences() -> List[Tuple[List[int], List[int], float, float]]:
    """
    Fixture providing binary sequence pairs with expected distances.
    
    Returns
    -------
    List[Tuple[List[int], List[int], float, float]]
        List of tuples containing (seq1, seq2, raw_distance, normalized_distance)
    """
    return [
        ([0, 0, 0, 0], [0, 0, 0, 0], 0.0, 0.0),  # Identical
        ([1, 1, 1, 1], [0, 0, 0, 0], 4.0, 1.0),  # Completely different
        ([1, 0, 1, 0], [1, 0, 0, 0], 1.0, 0.25), # One difference
        ([1, 1, 0, 0], [0, 1, 0, 1], 2.0, 0.5),  # Two differences
    ]

@pytest.fixture
def string_sequences() -> List[Tuple[str, str, float, float]]:
    """
    Fixture providing string sequence pairs with expected distances.
    
    Returns
    -------
    List[Tuple[str, str, float, float]]
        List of tuples containing (str1, str2, raw_distance, normalized_distance)
    """
    return [
        ("abcd", "abcd", 0.0, 0.0),       # Identical
        ("abcd", "efgh", 4.0, 1.0),       # Completely different
        ("karolin", "kathrin", 3.0, 3/7), # Three differences
        ("0000", "1111", 4.0, 1.0),       # Completely different
    ]

@pytest.fixture
def numpy_arrays() -> List[Tuple[np.ndarray, np.ndarray, float, float]]:
    """
    Fixture providing numpy array pairs with expected distances.
    
    Returns
    -------
    List[Tuple[np.ndarray, np.ndarray, float, float]]
        List of tuples containing (array1, array2, raw_distance, normalized_distance)
    """
    return [
        (np.array([1, 2, 3]), np.array([1, 2, 3]), 0.0, 0.0),         # Identical
        (np.array([1, 2, 3]), np.array([4, 5, 6]), 3.0, 1.0),         # Completely different
        (np.array([1, 2, 3, 4]), np.array([1, 2, 4, 4]), 1.0, 0.25),  # One difference
    ]

@pytest.fixture
def invalid_sequences() -> List[Tuple[Any, Any]]:
    """
    Fixture providing invalid sequence pairs that should raise exceptions.
    
    Returns
    -------
    List[Tuple[Any, Any]]
        List of tuples containing invalid sequence pairs
    """
    return [
        ([1, 2, 3], [1, 2]),          # Different lengths
        (np.array([1, 2]), np.array([1, 2, 3])),  # Different lengths
        ("abc", "abcd"),              # Different lengths
    ]

@pytest.fixture
def batch_test_data() -> Tuple[List[int], List[List[int]], List[float], List[float]]:
    """
    Fixture providing data for batch distance testing.
    
    Returns
    -------
    Tuple[List[int], List[List[int]], List[float], List[float]]
        Tuple containing (reference_seq, comparison_seqs, expected_raw_distances, expected_normalized_distances)
    """
    reference = [1, 0, 1, 0]
    comparisons = [
        [1, 0, 1, 0],  # Same
        [0, 0, 0, 0],  # 2 differences
        [1, 1, 1, 1],  # 2 differences
        [0, 1, 0, 1],  # 4 differences
    ]
    raw_distances = [0.0, 2.0, 2.0, 4.0]
    normalized_distances = [0.0, 0.5, 0.5, 1.0]
    
    return reference, comparisons, raw_distances, normalized_distances


# Tests
@pytest.mark.unit
def test_hamming_metric_instantiation():
    """Test that HammingMetric can be instantiated with default parameters."""
    metric = HammingMetric()
    assert metric.type == "HammingMetric"
    assert metric.normalize is False
    
    # Test with normalize=True
    metric = HammingMetric(normalize=True)
    assert metric.normalize is True

@pytest.mark.unit
def test_hamming_metric_serialization():
    """Test that HammingMetric can be serialized and deserialized correctly."""
    metric = HammingMetric(normalize=True)
    json_str = metric.model_dump_json()
    
    # Deserialize
    deserialized = HammingMetric.model_validate_json(json_str)
    
    assert deserialized.type == metric.type
    assert deserialized.normalize == metric.normalize

@pytest.mark.unit
@pytest.mark.parametrize("normalize", [True, False])
def test_binary_sequences(binary_sequences, normalize):
    """
    Test Hamming distance calculation with binary sequences.
    
    Parameters
    ----------
    binary_sequences : List[Tuple[List[int], List[int], float, float]]
        Test data from fixture
    normalize : bool
        Whether to normalize the distance
    """
    metric = HammingMetric(normalize=normalize)
    
    for seq1, seq2, raw_dist, norm_dist in binary_sequences:
        expected = norm_dist if normalize else raw_dist
        result = metric.distance(seq1, seq2)
        assert result == pytest.approx(expected), f"Failed for {seq1} and {seq2}, expected {expected}, got {result}"

@pytest.mark.unit
@pytest.mark.parametrize("normalize", [True, False])
def test_string_sequences(string_sequences, normalize):
    """
    Test Hamming distance calculation with string sequences.
    
    Parameters
    ----------
    string_sequences : List[Tuple[str, str, float, float]]
        Test data from fixture
    normalize : bool
        Whether to normalize the distance
    """
    metric = HammingMetric(normalize=normalize)
    
    for str1, str2, raw_dist, norm_dist in string_sequences:
        expected = norm_dist if normalize else raw_dist
        result = metric.distance(list(str1), list(str2))
        assert result == pytest.approx(expected), f"Failed for {str1} and {str2}, expected {expected}, got {result}"

@pytest.mark.unit
@pytest.mark.parametrize("normalize", [True, False])
def test_numpy_arrays(numpy_arrays, normalize):
    """
    Test Hamming distance calculation with numpy arrays.
    
    Parameters
    ----------
    numpy_arrays : List[Tuple[np.ndarray, np.ndarray, float, float]]
        Test data from fixture
    normalize : bool
        Whether to normalize the distance
    """
    metric = HammingMetric(normalize=normalize)
    
    for arr1, arr2, raw_dist, norm_dist in numpy_arrays:
        expected = norm_dist if normalize else raw_dist
        result = metric.distance(arr1, arr2)
        assert result == pytest.approx(expected), f"Failed for {arr1} and {arr2}, expected {expected}, got {result}"

@pytest.mark.unit
def test_invalid_sequences(invalid_sequences):
    """
    Test that appropriate exceptions are raised for invalid inputs.
    
    Parameters
    ----------
    invalid_sequences : List[Tuple[Any, Any]]
        Test data from fixture with invalid sequence pairs
    """
    metric = HammingMetric()
    
    for seq1, seq2 in invalid_sequences:
        with pytest.raises(ValueError, match="Sequences must have equal length"):
            metric.distance(seq1, seq2)

@pytest.mark.unit
def test_are_identical():
    """Test the are_identical method for correct identification of identical sequences."""
    metric = HammingMetric()
    
    # Identical sequences
    assert metric.are_identical([1, 2, 3], [1, 2, 3]) is True
    assert metric.are_identical("abc", "abc") is True
    assert metric.are_identical(np.array([1, 2, 3]), np.array([1, 2, 3])) is True
    
    # Different sequences
    assert metric.are_identical([1, 2, 3], [1, 2, 4]) is False
    assert metric.are_identical("abc", "abd") is False
    assert metric.are_identical(np.array([1, 2, 3]), np.array([1, 2, 4])) is False
    
    # Different length sequences should return False without raising an exception
    assert metric.are_identical([1, 2, 3], [1, 2]) is False
    assert metric.are_identical("abc", "abcd") is False

@pytest.mark.unit
@pytest.mark.parametrize("normalize", [True, False])
def test_batch_distance(batch_test_data, normalize):
    """
    Test the batch_distance method for computing distances to multiple points.
    
    Parameters
    ----------
    batch_test_data : Tuple[List[int], List[List[int]], List[float], List[float]]
        Test data from fixture
    normalize : bool
        Whether to normalize the distance
    """
    reference, comparisons, raw_distances, normalized_distances = batch_test_data
    metric = HammingMetric(normalize=normalize)
    
    expected = normalized_distances if normalize else raw_distances
    results = metric.batch_distance(reference, comparisons)
    
    assert len(results) == len(expected)
    for result, exp in zip(results, expected):
        assert result == pytest.approx(exp)

@pytest.mark.unit
def test_normalize_validator():
    """Test that the normalize validator correctly handles different input types."""
    # Boolean values should be preserved
    metric = HammingMetric(normalize=True)
    assert metric.normalize is True
    
    metric = HammingMetric(normalize=False)
    assert metric.normalize is False
    
    # Non-boolean values should be converted to boolean
    # Note: This requires direct validation since the Pydantic model would handle this automatically
    # We're testing the validator function directly
    validator_result = HammingMetric.validate_normalize(1)
    assert validator_result is True
    
    validator_result = HammingMetric.validate_normalize(0)
    assert validator_result is False
    
    validator_result = HammingMetric.validate_normalize("")
    assert validator_result is False
    
    validator_result = HammingMetric.validate_normalize("True")
    assert validator_result is True

@pytest.mark.unit
def test_edge_cases():
    """Test edge cases for the Hamming metric."""
    metric = HammingMetric()
    
    # Empty sequences
    assert metric.distance([], []) == 0.0
    
    # Single element sequences
    assert metric.distance([1], [1]) == 0.0
    assert metric.distance([1], [0]) == 1.0
    
    # Normalized distance with empty sequences should not cause division by zero
    metric_normalize