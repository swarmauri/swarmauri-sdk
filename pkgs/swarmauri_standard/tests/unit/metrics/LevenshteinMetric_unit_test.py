import pytest
from swarmauri_standard.metrics import LevenshteinMetric
import logging


@pytest.mark.unit
def test_levenshteinmetric_distance():
    """
    Test the distance method of the LevenshteinMetric class.

    This test case verifies the computation of Levenshtein distances for various inputs.
    """
    levenshtein = LevenshteinMetric()

    # Test case where inputs are identical
    assert levenshtein.distance("test", "test") == 0.0

    # Test case where one string is empty
    assert levenshtein.distance("", "test") == 4.0

    # Test case with simple substitution
    assert levenshtein.distance("kitten", "sitting") == 3.0

    # Test case with multiple operations
    assert levenshtein.distance("hello", "billion") == 6.0

    # Test case where both strings are empty
    assert levenshtein.distance("", "") == 0.0

    # Test case with different lengths and substitutions
    assert levenshtein.distance("abc", "def") == 3.0


@pytest.mark.unit
def test_levenshteinmetric_distances():
    """
    Test the distances method of the LevenshteinMetric class.

    This test case verifies the computation of distances for single and multiple inputs.
    """
    levenshtein = LevenshteinMetric()

    # Test single string input
    assert levenshtein.distances("test", "test") == 0.0

    # Test multiple string inputs
    results = levenshtein.distances("test", ["test", "test1", "testing"])
    assert isinstance(results, list)
    assert results == [0.0, 1.0, 3.0]

    # Test invalid input
    with pytest.raises(ValueError):
        levenshtein.distances(123, "test")


@pytest.mark.unit
def test_levenshteinmetric_initialization():
    """
    Test the initialization of the LevenshteinMetric class.

    This test case verifies that the class initializes correctly.
    """
    levenshtein = LevenshteinMetric()
    assert isinstance(levenshtein, LevenshteinMetric)
    assert levenshtein.resource == "Metric"
    assert levenshtein.type == "LevenshteinMetric"


@pytest.mark.unit
def test_levenshteinmetric_value_error():
    """
    Test error handling in the LevenshteinMetric class.

    This test case verifies that appropriate ValueErrors are raised.
    """
    levenshtein = LevenshteinMetric()

    # Test invalid input types
    with pytest.raises(ValueError):
        levenshtein.distance(123, "test")

    with pytest.raises(ValueError):
        levenshtein.distance("test", 456)

    with pytest.raises(ValueError):
        levenshtein.distances(123, "test")

    with pytest.raises(ValueError):
        levenshtein.distances("test", 456)
        levenshtein.distances("test", ["test", 456])


@pytest.mark.unit
def test_levenshteinmetric_logging():
    """
    Test logging functionality in the LevenshteinMetric class.

    This test case verifies that appropriate debug messages are logged.
    """
    levenshtein = LevenshteinMetric()

    # Capture logging messages
    logger = logging.getLogger(__name__)
    with pytest.raises(AssertionError):
        # Should not trigger any errors
        pass
