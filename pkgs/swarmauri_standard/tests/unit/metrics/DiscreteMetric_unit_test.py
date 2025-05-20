import logging

import numpy as np
import pytest

from swarmauri_standard.metrics.DiscreteMetric import DiscreteMetric

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def discrete_metric():
    """
    Fixture that provides a DiscreteMetric instance.

    Returns
    -------
    DiscreteMetric
        An instance of the DiscreteMetric class
    """
    return DiscreteMetric()


@pytest.mark.unit
def test_initialization():
    """Test the initialization of DiscreteMetric."""
    metric = DiscreteMetric()
    assert metric.type == "DiscreteMetric"
    assert metric.resource == "Metric"


@pytest.mark.unit
def test_serialization():
    """Test serialization and deserialization of DiscreteMetric."""
    metric = DiscreteMetric()
    serialized = metric.model_dump_json()
    deserialized = DiscreteMetric.model_validate_json(serialized)

    assert isinstance(deserialized, DiscreteMetric)
    assert deserialized.type == metric.type
    assert deserialized.resource == metric.resource


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y, expected",
    [
        (1, 1, 0.0),
        (1, 2, 1.0),
        ("a", "a", 0.0),
        ("a", "b", 1.0),
        (True, True, 0.0),
        (True, False, 1.0),
        ((1, 2), (1, 2), 0.0),
        ((1, 2), (2, 1), 1.0),
    ],
)
def test_distance(discrete_metric, x, y, expected):
    """
    Test the distance method with various inputs.

    Parameters
    ----------
    discrete_metric : DiscreteMetric
        The metric instance from the fixture
    x : float
        First input value
    y : float
        Second input value
    expected : float
        Expected distance result
    """
    result = discrete_metric.distance(x, y)
    assert result == expected

    # Test symmetry property
    assert discrete_metric.distance(x, y) == discrete_metric.distance(y, x)


@pytest.mark.unit
def test_distance_with_unhashable_input(discrete_metric):
    """Test that distance method raises TypeError with unhashable inputs."""
    with pytest.raises(TypeError):
        discrete_metric.distance([1, 2], [1, 2])


@pytest.mark.unit
def test_distances_single_elements(discrete_metric):
    """Test the distances method with single element collections."""
    x = [1]
    y = [2]
    result = discrete_metric.distances(x, y)
    assert isinstance(result, np.ndarray)
    assert result.shape == (1, 1)
    assert result[0, 0] == 1.0


@pytest.mark.unit
def test_distances_multiple_elements(discrete_metric):
    """Test the distances method with multiple element collections."""
    x = [1, 2, 3]
    y = [1, 2, 4]
    result = discrete_metric.distances(x, y)

    assert isinstance(result, np.ndarray)
    assert result.shape == (3, 3)

    # Expected distance matrix:
    # [0, 1, 1]
    # [1, 0, 1]
    # [1, 1, 1]
    expected = np.array([[0.0, 1.0, 1.0], [1.0, 0.0, 1.0], [1.0, 1.0, 1.0]])

    np.testing.assert_array_equal(result, expected)


@pytest.mark.unit
def test_distances_with_numpy_arrays(discrete_metric):
    """Test the distances method with numpy arrays as input."""
    x = np.array([1, 2, 3])
    y = np.array([1, 2, 4])
    result = discrete_metric.distances(x, y)

    assert isinstance(result, np.ndarray)
    assert result.shape == (3, 3)

    expected = np.array([[0.0, 1.0, 1.0], [1.0, 0.0, 1.0], [1.0, 1.0, 1.0]])

    np.testing.assert_array_equal(result, expected)


@pytest.mark.unit
def test_distances_with_different_sized_collections(discrete_metric):
    """Test the distances method with collections of different sizes."""
    x = [1, 2]
    y = [1, 2, 3]
    result = discrete_metric.distances(x, y)

    assert isinstance(result, np.ndarray)
    assert result.shape == (2, 3)

    expected = np.array([[0.0, 1.0, 1.0], [1.0, 0.0, 1.0]])

    np.testing.assert_array_equal(result, expected)


@pytest.mark.unit
def test_distances_with_strings(discrete_metric):
    """Test the distances method with string inputs."""
    x = ["a", "b"]
    y = ["a", "c"]
    result = discrete_metric.distances(x, y)

    expected = np.array([[0.0, 1.0], [1.0, 1.0]])

    np.testing.assert_array_equal(result, expected)


@pytest.mark.unit
def test_check_non_negativity(discrete_metric):
    """Test that the non-negativity axiom is satisfied."""
    assert discrete_metric.check_non_negativity(1, 2) is True
    assert discrete_metric.check_non_negativity("a", "b") is True
    assert discrete_metric.check_non_negativity(1, 1) is True


@pytest.mark.unit
def test_check_identity_of_indiscernibles(discrete_metric):
    """Test that the identity of indiscernibles axiom is satisfied."""
    assert discrete_metric.check_identity_of_indiscernibles(1, 2) is True
    assert discrete_metric.check_identity_of_indiscernibles(1, 1) is True
    assert discrete_metric.check_identity_of_indiscernibles("a", "a") is True


@pytest.mark.unit
def test_check_symmetry(discrete_metric):
    """Test that the symmetry axiom is satisfied."""
    assert discrete_metric.check_symmetry(1, 2) is True
    assert discrete_metric.check_symmetry("a", "b") is True
    assert discrete_metric.check_symmetry(True, False) is True


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y, z",
    [
        (1, 2, 3),
        ("a", "b", "c"),
        (True, False, True),
        ((1, 2), (3, 4), (5, 6)),
    ],
)
def test_check_triangle_inequality(discrete_metric, x, y, z):
    """
    Test that the triangle inequality axiom is satisfied.

    Parameters
    ----------
    discrete_metric : DiscreteMetric
        The metric instance from the fixture
    x : float
        First point
    y : float
        Second point
    z : float
        Third point
    """
    assert discrete_metric.check_triangle_inequality(x, y, z) is True

    # Verify the actual inequality
    d_xz = discrete_metric.distance(x, z)
    d_xy = discrete_metric.distance(x, y)
    d_yz = discrete_metric.distance(y, z)

    assert d_xz <= d_xy + d_yz


@pytest.mark.unit
def test_all_metric_axioms(discrete_metric):
    """Test that all metric axioms are satisfied for various inputs."""
    test_points = [1, "a", True, (1, 2)]

    for x in test_points:
        for y in test_points:
            # Non-negativity
            assert discrete_metric.distance(x, y) >= 0

            # Identity of indiscernibles
            assert (discrete_metric.distance(x, y) == 0) == (x == y)

            # Symmetry
            assert discrete_metric.distance(x, y) == discrete_metric.distance(y, x)

            for z in test_points:
                # Triangle inequality
                assert discrete_metric.distance(x, z) <= discrete_metric.distance(
                    x, y
                ) + discrete_metric.distance(y, z)
