import logging

import pytest

from swarmauri_standard.metrics.EuclideanMetric import EuclideanMetric
from swarmauri_standard.vectors.Vector import Vector

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def euclidean_metric():
    """
    Fixture that provides an EuclideanMetric instance for tests.

    Returns
    -------
    EuclideanMetric
        An instance of the EuclideanMetric class
    """
    return EuclideanMetric()


@pytest.mark.unit
def test_euclidean_metric_resource_type(euclidean_metric):
    """Test that EuclideanMetric has the correct resource type."""
    assert euclidean_metric.resource == "Metric"


@pytest.mark.unit
def test_euclidean_metric_type(euclidean_metric):
    """Test that EuclideanMetric has the correct type."""
    assert euclidean_metric.type == "EuclideanMetric"


# Replace the mock_vector fixture with a real_vector fixture
@pytest.fixture
def real_vector_pair():
    """
    Fixture that provides a pair of concrete Vector instances for testing.

    Returns
    -------
    tuple
        A pair of Vector instances
    """
    v1 = Vector(value=[1.0, 2.0, 3.0])
    v2 = Vector(value=[4.0, 5.0, 6.0])
    return v1, v2


# Update the test_euclidean_distance_with_vectors test
@pytest.mark.unit
def test_euclidean_distance_with_vectors(euclidean_metric, real_vector_pair):
    """
    Test the distance method with Vector inputs.

    Parameters
    ----------
    euclidean_metric : EuclideanMetric
        The metric instance
    real_vector_pair : tuple
        A pair of Vector instances
    """
    v1, v2 = real_vector_pair

    result = euclidean_metric.distance(v1, v2)
    expected = 5.196152422706632  # sqrt((4-1)^2 + (5-2)^2 + (6-3)^2)
    assert abs(result - expected) < 1e-10


# Update the test_distances_with_vectors test
@pytest.mark.unit
def test_distances_with_vectors(euclidean_metric, real_vector_pair):
    """
    Test the distances method with Vector inputs.

    Parameters
    ----------
    euclidean_metric : EuclideanMetric
        The metric instance
    real_vector_pair : tuple
        A pair of Vector instances
    """
    v1, v2 = real_vector_pair

    result = euclidean_metric.distances(v1, v2)
    expected = [5.196152422706632]  # sqrt((4-1)^2 + (5-2)^2 + (6-3)^2)
    assert len(result) == 1
    assert abs(result[0] - expected[0]) < 1e-10


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y, expected",
    [
        ([1, 0, 0], [0, 0, 0], 1.0),
        ([0, 0, 0], [1, 0, 0], 1.0),
        ([1, 2, 3], [4, 5, 6], 5.196152422706632),
        ([0, 0, 0], [0, 0, 0], 0.0),
        ([1.5, 2.5], [1.5, 2.5], 0.0),
    ],
)
def test_euclidean_distance_with_sequences(euclidean_metric, x, y, expected):
    """
    Test the distance method with sequence inputs.

    Parameters
    ----------
    euclidean_metric : EuclideanMetric
        The metric instance
    x : List[float]
        First point
    y : List[float]
        Second point
    expected : float
        Expected distance
    """
    result = euclidean_metric.distance(x, y)
    assert abs(result - expected) < 1e-10


@pytest.mark.unit
def test_euclidean_distance_with_different_dimensions(euclidean_metric):
    """
    Test that distance method raises ValueError for inputs with different dimensions.

    Parameters
    ----------
    euclidean_metric : EuclideanMetric
        The metric instance
    """
    with pytest.raises(ValueError):
        euclidean_metric.distance([1, 2, 3], [1, 2])


@pytest.mark.unit
def test_euclidean_distance_with_unsupported_types(euclidean_metric):
    """
    Test that distance method raises TypeError for unsupported input types.

    Parameters
    ----------
    euclidean_metric : EuclideanMetric
        The metric instance
    """
    with pytest.raises(TypeError):
        euclidean_metric.distance("string1", "string2")


@pytest.mark.unit
def test_distances_with_list_of_lists(euclidean_metric):
    """
    Test the distances method with lists of lists inputs.

    Parameters
    ----------
    euclidean_metric : EuclideanMetric
        The metric instance
    """
    x = [[1, 2, 3], [4, 5, 6]]
    y = [[7, 8, 9], [10, 11, 12]]

    result = euclidean_metric.distances(x, y)

    # Expected distances:
    # d([1,2,3], [7,8,9]) = sqrt((7-1)^2 + (8-2)^2 + (9-3)^2) = sqrt(36+36+36) = sqrt(108) = 10.392
    # d([1,2,3], [10,11,12]) = sqrt((10-1)^2 + (11-2)^2 + (12-3)^2) = sqrt(81+81+81) = sqrt(243) = 15.588
    # d([4,5,6], [7,8,9]) = sqrt((7-4)^2 + (8-5)^2 + (9-6)^2) = sqrt(9+9+9) = sqrt(27) = 5.196
    # d([4,5,6], [10,11,12]) = sqrt((10-4)^2 + (11-5)^2 + (12-6)^2) = sqrt(36+36+36) = sqrt(108) = 10.392

    expected = [
        [10.392304845413264, 15.588457268119896],
        [5.196152422706632, 10.392304845413264],
    ]

    assert len(result) == len(expected)
    for i in range(len(result)):
        assert len(result[i]) == len(expected[i])
        for j in range(len(result[i])):
            assert abs(result[i][j] - expected[i][j]) < 1e-10


@pytest.mark.unit
def test_distances_with_simple_lists(euclidean_metric):
    """
    Test the distances method with simple list inputs.

    Parameters
    ----------
    euclidean_metric : EuclideanMetric
        The metric instance
    """
    x = [1, 2, 3]
    y = [4, 5, 6]

    result = euclidean_metric.distances(x, y)
    expected = [5.196152422706632]  # sqrt((4-1)^2 + (5-2)^2 + (6-3)^2)

    assert len(result) == 1
    assert abs(result[0] - expected[0]) < 1e-10


@pytest.mark.unit
def test_distances_with_incompatible_dimensions(euclidean_metric):
    """
    Test that distances method raises ValueError for inputs with incompatible dimensions.

    Parameters
    ----------
    euclidean_metric : EuclideanMetric
        The metric instance
    """
    x = [[1, 2, 3], [4, 5, 6]]
    y = [[7, 8], [10, 11]]

    with pytest.raises(ValueError):
        euclidean_metric.distances(x, y)


@pytest.mark.unit
def test_distances_with_unsupported_types(euclidean_metric):
    """
    Test that distances method raises TypeError for unsupported input types.

    Parameters
    ----------
    euclidean_metric : EuclideanMetric
        The metric instance
    """
    with pytest.raises(TypeError):
        euclidean_metric.distances("string1", "string2")


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y",
    [
        ([1, 2, 3], [4, 5, 6]),
        ([0, 0, 0], [0, 0, 0]),
        ([-1, -2, -3], [-4, -5, -6]),
    ],
)
def test_check_non_negativity(euclidean_metric, x, y):
    """
    Test the check_non_negativity method.

    Parameters
    ----------
    euclidean_metric : EuclideanMetric
        The metric instance
    x : List[float]
        First point
    y : List[float]
        Second point
    """
    assert euclidean_metric.check_non_negativity(x, y) is True


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y, expected",
    [
        ([1, 2, 3], [1, 2, 3], True),  # Same points -> distance should be 0
        ([1, 2, 3], [4, 5, 6], True),  # Different points -> distance should be > 0
        ([0, 0, 0], [0, 0, 0], True),  # Same points at origin
    ],
)
def test_check_identity_of_indiscernibles(euclidean_metric, x, y, expected):
    """
    Test the check_identity_of_indiscernibles method.

    Parameters
    ----------
    euclidean_metric : EuclideanMetric
        The metric instance
    x : List[float]
        First point
    y : List[float]
        Second point
    expected : bool
        Expected result
    """
    assert euclidean_metric.check_identity_of_indiscernibles(x, y) is expected


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y",
    [
        ([1, 2, 3], [4, 5, 6]),
        ([0, 0, 0], [0, 0, 0]),
        ([-1, -2, -3], [-4, -5, -6]),
    ],
)
def test_check_symmetry(euclidean_metric, x, y):
    """
    Test the check_symmetry method.

    Parameters
    ----------
    euclidean_metric : EuclideanMetric
        The metric instance
    x : List[float]
        First point
    y : List[float]
        Second point
    """
    assert euclidean_metric.check_symmetry(x, y) is True


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y, z",
    [
        ([0, 0, 0], [1, 0, 0], [0, 1, 0]),  # Right-angle triangle
        ([1, 2, 3], [4, 5, 6], [7, 8, 9]),  # Arbitrary points
        ([0, 0, 0], [0, 0, 0], [0, 0, 0]),  # All same point
    ],
)
def test_check_triangle_inequality(euclidean_metric, x, y, z):
    """
    Test the check_triangle_inequality method.

    Parameters
    ----------
    euclidean_metric : EuclideanMetric
        The metric instance
    x : List[float]
        First point
    y : List[float]
        Second point
    z : List[float]
        Third point
    """
    assert euclidean_metric.check_triangle_inequality(x, y, z) is True


@pytest.mark.unit
def test_serialization_deserialization(euclidean_metric):
    """
    Test serialization and deserialization of EuclideanMetric.

    Parameters
    ----------
    euclidean_metric : EuclideanMetric
        The metric instance
    """
    # Serialize
    serialized = euclidean_metric.model_dump_json()

    # Deserialize
    deserialized = EuclideanMetric.model_validate_json(serialized)

    # Check type and resource
    assert deserialized.type == euclidean_metric.type
    assert deserialized.resource == euclidean_metric.resource

    # Test functionality is preserved
    x = [1, 2, 3]
    y = [4, 5, 6]
    original_distance = euclidean_metric.distance(x, y)
    deserialized_distance = deserialized.distance(x, y)

    assert abs(original_distance - deserialized_distance) < 1e-10
