import pytest
import logging
from typing import List, Tuple
import string
import random
from swarmauri_standard.metrics.LevenshteinMetric import LevenshteinMetric

# Configure logger for tests
logger = logging.getLogger(__name__)


@pytest.fixture
def levenshtein_metric():
    """
    Fixture providing a default LevenshteinMetric instance.
    
    Returns
    -------
    LevenshteinMetric
        A default instance of LevenshteinMetric
    """
    return LevenshteinMetric()


@pytest.fixture
def case_insensitive_metric():
    """
    Fixture providing a case-insensitive LevenshteinMetric instance.
    
    Returns
    -------
    LevenshteinMetric
        A case-insensitive instance of LevenshteinMetric
    """
    return LevenshteinMetric(case_sensitive=False)


@pytest.fixture
def string_pairs() -> List[Tuple[str, str, float]]:
    """
    Fixture providing test string pairs and their expected Levenshtein distances.
    
    Returns
    -------
    List[Tuple[str, str, float]]
        List of tuples containing (string1, string2, expected_distance)
    """
    return [
        ("", "", 0.0),                   # Empty strings
        ("a", "a", 0.0),                 # Identical single chars
        ("abc", "abc", 0.0),             # Identical strings
        ("kitten", "sitting", 3.0),      # Classic example
        ("saturday", "sunday", 3.0),     # Another classic example
        ("book", "back", 2.0),           # Substitution
        ("hello", "hallo", 1.0),         # Single substitution
        ("hello", "hell", 1.0),          # Deletion
        ("hell", "hello", 1.0),          # Insertion
        ("hello", "", 5.0),              # Complete deletion
        ("", "world", 5.0),              # Complete insertion
        ("HELLO", "hello", 5.0),         # Case difference (case-sensitive)
        ("Levenshtein", "levenshtein", 1.0),  # Case difference in first letter
    ]


@pytest.fixture
def case_pairs() -> List[Tuple[str, str, bool]]:
    """
    Fixture providing test cases for case sensitivity testing.
    
    Returns
    -------
    List[Tuple[str, str, bool]]
        List of tuples containing (string1, string2, are_identical_when_case_insensitive)
    """
    return [
        ("HELLO", "hello", True),
        ("World", "world", True),
        ("LeVeNsHtEiN", "levenshtein", True),
        ("HELLO", "hallo", False),
        ("WORLD", "word", False),
    ]


@pytest.mark.unit
def test_type():
    """Test that the metric type is correctly set."""
    metric = LevenshteinMetric()
    assert metric.type == "LevenshteinMetric"


@pytest.mark.unit
def test_resource():
    """Test that the resource value is correctly set."""
    metric = LevenshteinMetric()
    assert metric.resource == "Metric"


@pytest.mark.unit
def test_case_sensitive_default():
    """Test that case_sensitive defaults to True."""
    metric = LevenshteinMetric()
    assert metric.case_sensitive is True


@pytest.mark.unit
def test_serialization_deserialization():
    """Test that the metric can be serialized and deserialized correctly."""
    original = LevenshteinMetric(case_sensitive=False)
    serialized = original.model_dump_json()
    deserialized = LevenshteinMetric.model_validate_json(serialized)
    
    assert deserialized.type == original.type
    assert deserialized.case_sensitive == original.case_sensitive


@pytest.mark.unit
@pytest.mark.parametrize("x, y, expected", [
    ("", "", 0.0),
    ("a", "a", 0.0),
    ("kitten", "sitting", 3.0),
    ("book", "back", 2.0),
    ("hello", "hello world", 6.0),
])
def test_distance_calculation(levenshtein_metric, x, y, expected):
    """
    Test Levenshtein distance calculation with various string pairs.
    
    Parameters
    ----------
    levenshtein_metric : LevenshteinMetric
        The metric instance
    x : str
        First string
    y : str
        Second string
    expected : float
        Expected distance
    """
    assert levenshtein_metric.distance(x, y) == expected


@pytest.mark.unit
def test_distance_with_string_pairs(levenshtein_metric, string_pairs):
    """
    Test Levenshtein distance with the predefined string pairs.
    
    Parameters
    ----------
    levenshtein_metric : LevenshteinMetric
        The metric instance
    string_pairs : List[Tuple[str, str, float]]
        List of test cases
    """
    for x, y, expected in string_pairs:
        assert levenshtein_metric.distance(x, y) == expected


@pytest.mark.unit
def test_distance_symmetry(levenshtein_metric, string_pairs):
    """
    Test that the Levenshtein distance is symmetric (d(x,y) = d(y,x)).
    
    Parameters
    ----------
    levenshtein_metric : LevenshteinMetric
        The metric instance
    string_pairs : List[Tuple[str, str, float]]
        List of test cases
    """
    for x, y, _ in string_pairs:
        assert levenshtein_metric.distance(x, y) == levenshtein_metric.distance(y, x)


@pytest.mark.unit
def test_distance_non_string_inputs(levenshtein_metric):
    """
    Test that the distance method raises TypeError for non-string inputs.
    
    Parameters
    ----------
    levenshtein_metric : LevenshteinMetric
        The metric instance
    """
    with pytest.raises(TypeError):
        levenshtein_metric.distance(123, "abc")
    
    with pytest.raises(TypeError):
        levenshtein_metric.distance("abc", 123)
    
    with pytest.raises(TypeError):
        levenshtein_metric.distance(123, 456)


@pytest.mark.unit
def test_case_sensitivity(levenshtein_metric, case_insensitive_metric, case_pairs):
    """
    Test case sensitivity behavior of the metric.
    
    Parameters
    ----------
    levenshtein_metric : LevenshteinMetric
        Case-sensitive metric instance
    case_insensitive_metric : LevenshteinMetric
        Case-insensitive metric instance
    case_pairs : List[Tuple[str, str, bool]]
        List of test cases
    """
    for x, y, expected_identical in case_pairs:
        # Case-sensitive metric should consider different cases as different
        if x.lower() == y.lower() and x != y:
            assert levenshtein_metric.distance(x, y) > 0
            assert not levenshtein_metric.are_identical(x, y)
        
        # Case-insensitive metric should ignore case differences
        if expected_identical:
            assert case_insensitive_metric.distance(x, y) == 0
            assert case_insensitive_metric.are_identical(x, y)
        else:
            assert case_insensitive_metric.distance(x, y) > 0
            assert not case_insensitive_metric.are_identical(x, y)


@pytest.mark.unit
def test_are_identical(levenshtein_metric):
    """
    Test the are_identical method.
    
    Parameters
    ----------
    levenshtein_metric : LevenshteinMetric
        The metric instance
    """
    assert levenshtein_metric.are_identical("hello", "hello") is True
    assert levenshtein_metric.are_identical("hello", "world") is False
    assert levenshtein_metric.are_identical("", "") is True
    assert levenshtein_metric.are_identical("HELLO", "hello") is False


@pytest.mark.unit
def test_are_identical_non_string_inputs(levenshtein_metric):
    """
    Test that are_identical raises TypeError for non-string inputs.
    
    Parameters
    ----------
    levenshtein_metric : LevenshteinMetric
        The metric instance
    """
    with pytest.raises(TypeError):
        levenshtein_metric.are_identical(123, "abc")
    
    with pytest.raises(TypeError):
        levenshtein_metric.are_identical("abc", 123)


@pytest.mark.unit
@pytest.mark.parametrize("x, y, expected", [
    ("", "", 1.0),
    ("a", "a", 1.0),
    ("kitten", "sitting", 0.57),  # ~0.57 similarity
    ("hello", "world", 0.2),      # ~0.2 similarity
    ("abc", "abcdef", 0.5),       # 0.5 similarity
])
def test_similarity(levenshtein_metric, x, y, expected):
    """
    Test the similarity method with various string pairs.
    
    Parameters
    ----------
    levenshtein_metric : LevenshteinMetric
        The metric instance
    x : str
        First string
    y : str
        Second string
    expected : float
        Expected similarity (approximate)
    """
    # Using approx to allow for small floating-point differences
    assert pytest.approx(levenshtein_metric.similarity(x, y), abs=0.01) == expected


@pytest.mark.unit
def test_similarity_edge_cases(levenshtein_metric):
    """
    Test the similarity method with edge cases.
    
    Parameters
    ----------
    levenshtein_metric : LevenshteinMetric
        The metric instance
    """
    # Identical strings should have similarity 1.0
    assert levenshtein_metric.similarity("hello", "hello") == 1.0
    
    # Empty strings should have similarity 1.0
    assert levenshtein_metric.similarity("", "") == 1.0
    
    # One empty string and one non-empty string should have similarity 0.0
    assert levenshtein_metric.similarity("hello", "") == 0.0
    assert levenshtein_metric.similarity("", "world") == 0.0


@pytest.mark.unit
def test_similarity_non_string_inputs(levenshtein_metric):
    """
    Test that similarity raises TypeError for non-string inputs.
    
    Parameters
    ----------
    levenshtein_metric : LevenshteinMetric
        The metric instance
    """
    with pytest.raises(TypeError):
        levenshtein_metric.similarity(123, "abc")
    
    with pytest.raises(TypeError):
        levenshtein_metric.similarity("abc", 123)


@pytest.mark.unit
def test_similarity_symmetry(levenshtein_metric):
    """
    Test that similarity is symmetric (sim(x,y) = sim(y,x)).
    
    Parameters
    ----------
    levenshtein_metric : LevenshteinMetric
        The metric instance
    """
    test_pairs = [
        ("kitten", "sitting"),
        ("hello", "world"),
        ("", "test"),
        ("abc", "abcdef"),
    ]
    
    for x, y in test_pairs:
        assert levenshtein_metric.similarity(x, y) == levenshtein_metric.similarity(y, x)


@pytest.mark.unit
def test_with_random_strings():
    """Test the metric with randomly generated strings."""
    metric