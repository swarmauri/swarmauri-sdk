import logging

import numpy as np
import pytest

from swarmauri_standard.metrics.LevenshteinMetric import LevenshteinMetric

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture
def levenshtein_metric():
    """
    Fixture that provides a LevenshteinMetric instance.

    Returns
    -------
    LevenshteinMetric
        An instance of LevenshteinMetric
    """
    return LevenshteinMetric()


@pytest.mark.unit
def test_levenshtein_metric_initialization():
    """Test that LevenshteinMetric initializes correctly."""
    metric = LevenshteinMetric()
    assert metric.type == "LevenshteinMetric"
    assert isinstance(metric, LevenshteinMetric)


@pytest.mark.unit
def test_levenshtein_metric_serialization():
    """Test that LevenshteinMetric can be serialized and deserialized correctly."""
    metric = LevenshteinMetric()
    serialized = metric.model_dump_json()
    deserialized = LevenshteinMetric.model_validate_json(serialized)

    assert isinstance(deserialized, LevenshteinMetric)
    assert deserialized.type == metric.type


@pytest.mark.unit
@pytest.mark.parametrize(
    "str1, str2, expected",
    [
        ("", "", 0),
        ("a", "", 1),
        ("", "a", 1),
        ("kitten", "sitting", 3),
        ("saturday", "sunday", 3),
        ("hello", "hello", 0),
        ("abc", "def", 3),
        ("test", "test123", 3),
    ],
)
def test_levenshtein_distance(levenshtein_metric, str1, str2, expected):
    """
    Test the Levenshtein distance calculation for various string pairs.

    Parameters
    ----------
    levenshtein_metric : LevenshteinMetric
        The metric instance
    str1 : str
        First string
    str2 : str
        Second string
    expected : int
        Expected Levenshtein distance
    """
    assert levenshtein_metric.distance(str1, str2) == expected


@pytest.mark.unit
def test_levenshtein_distance_type_error(levenshtein_metric):
    """Test that TypeError is raised when non-string inputs are provided."""
    with pytest.raises(TypeError):
        levenshtein_metric.distance(123, "abc")

    with pytest.raises(TypeError):
        levenshtein_metric.distance("abc", 123)

    with pytest.raises(TypeError):
        levenshtein_metric.distance(123, 456)


@pytest.mark.unit
def test_levenshtein_distances_lists(levenshtein_metric):
    """Test the distances method with lists of strings."""
    x = ["kitten", "hello", "test"]
    y = ["sitting", "world", "testing"]

    result = levenshtein_metric.distances(x, y)

    expected = [[3, 6, 5], [7, 4, 6], [6, 5, 3]]
    assert result == expected


@pytest.mark.unit
def test_levenshtein_distances_single_string(levenshtein_metric):
    """Test the distances method with a single string in x."""
    x = ["kitten"]
    y = ["sitting", "world", "testing"]

    result = levenshtein_metric.distances(x, y)

    # Expected: [3, 6, 5]
    expected = [3, 6, 5]

    assert result == expected


@pytest.mark.unit
def test_levenshtein_distances_numpy_arrays(levenshtein_metric):
    """Test the distances method with numpy arrays."""
    x = np.array(["kitten", "hello"])
    y = np.array(["sitting", "world"])

    result = levenshtein_metric.distances(x, y)
    expected = [
        [3, 6],
        [7, 4],
    ]
    assert result == expected


@pytest.mark.unit
def test_levenshtein_distances_type_error(levenshtein_metric):
    """Test that TypeError is raised for invalid inputs to distances method."""
    # Test with non-list/array inputs
    with pytest.raises(TypeError):
        levenshtein_metric.distances("kitten", ["sitting"])

    with pytest.raises(TypeError):
        levenshtein_metric.distances(["kitten"], "sitting")

    # Test with non-string elements
    with pytest.raises(TypeError):
        levenshtein_metric.distances([123], ["abc"])

    with pytest.raises(TypeError):
        levenshtein_metric.distances(["abc"], [123])


@pytest.mark.unit
@pytest.mark.parametrize(
    "str1, str2",
    [
        ("kitten", "sitting"),
        ("", ""),
        ("hello", "world"),
        ("test", "testing"),
    ],
)
def test_non_negativity_axiom(levenshtein_metric, str1, str2):
    """Test that the non-negativity axiom holds for Levenshtein distance."""
    assert levenshtein_metric.check_non_negativity(str1, str2) is True
    assert levenshtein_metric.distance(str1, str2) >= 0


@pytest.mark.unit
@pytest.mark.parametrize(
    "str1, str2",
    [
        ("kitten", "kitten"),
        ("", ""),
        ("hello", "hello"),
        ("kitten", "sitting"),
    ],
)
def test_identity_of_indiscernibles_axiom(levenshtein_metric, str1, str2):
    """Test that the identity of indiscernibles axiom holds for Levenshtein distance."""
    assert levenshtein_metric.check_identity_of_indiscernibles(str1, str2) is True
    assert (levenshtein_metric.distance(str1, str2) == 0) == (str1 == str2)


@pytest.mark.unit
@pytest.mark.parametrize(
    "str1, str2",
    [
        ("kitten", "sitting"),
        ("", ""),
        ("hello", "world"),
        ("test", "testing"),
    ],
)
def test_symmetry_axiom(levenshtein_metric, str1, str2):
    """Test that the symmetry axiom holds for Levenshtein distance."""
    assert levenshtein_metric.check_symmetry(str1, str2) is True
    assert levenshtein_metric.distance(str1, str2) == levenshtein_metric.distance(
        str2, str1
    )


@pytest.mark.unit
@pytest.mark.parametrize(
    "str1, str2, str3",
    [
        ("kitten", "sitting", "smitten"),
        ("", "a", "ab"),
        ("hello", "hallo", "hillo"),
        ("test", "testing", "tests"),
    ],
)
def test_triangle_inequality_axiom(levenshtein_metric, str1, str2, str3):
    """Test that the triangle inequality axiom holds for Levenshtein distance."""
    assert levenshtein_metric.check_triangle_inequality(str1, str2, str3) is True

    d_xy = levenshtein_metric.distance(str1, str2)
    d_yz = levenshtein_metric.distance(str2, str3)
    d_xz = levenshtein_metric.distance(str1, str3)

    assert d_xz <= d_xy + d_yz


@pytest.mark.unit
def test_all_metric_axioms(levenshtein_metric):
    """Test that all metric axioms hold for a set of strings."""
    strings = ["kitten", "sitting", "smitten", "mitten", "written"]

    # Test all pairs for non-negativity and symmetry
    for i, s1 in enumerate(strings):
        for j, s2 in enumerate(strings):
            assert levenshtein_metric.check_non_negativity(s1, s2)
            assert levenshtein_metric.check_identity_of_indiscernibles(s1, s2)
            assert levenshtein_metric.check_symmetry(s1, s2)

    # Test all triplets for triangle inequality
    for i, s1 in enumerate(strings):
        for j, s2 in enumerate(strings):
            for k, s3 in enumerate(strings):
                assert levenshtein_metric.check_triangle_inequality(s1, s2, s3)
