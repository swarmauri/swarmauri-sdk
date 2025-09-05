import logging

import numpy as np
import pytest

from swarmauri_standard.metrics.SupremumMetric import SupremumMetric

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def supremum_metric():
    """
    Create a SupremumMetric instance for testing.

    Returns
    -------
    SupremumMetric
        An instance of the SupremumMetric class
    """
    return SupremumMetric()


@pytest.mark.unit
def test_initialization():
    """Test the initialization of SupremumMetric."""
    metric = SupremumMetric()
    assert metric.type == "SupremumMetric"
    assert metric.resource == "Metric"


@pytest.mark.unit
def test_serialization():
    """Test serialization and deserialization of SupremumMetric."""
    metric = SupremumMetric()
    serialized = metric.model_dump_json()
    deserialized = SupremumMetric.model_validate_json(serialized)

    assert deserialized.type == metric.type
    assert deserialized.resource == metric.resource


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y, expected",
    [
        ([1, 2, 3], [1, 2, 3], 0.0),
        ([1, 2, 3], [4, 5, 6], 3.0),
        ([1, 2, 3], [2, 4, 7], 4.0),
        ([0, 0, 0], [5, 3, 2], 5.0),
        ([-1, -2, -3], [1, 2, 3], 6.0),
        ([1.5, 2.5], [3.5, 1.5], 2.0),
        (5, 8, 3.0),
        (3.5, 1.5, 2.0),
    ],
)
def test_distance_basic(supremum_metric, x, y, expected):
    """
    Test the distance method with various basic inputs.

    Parameters
    ----------
    supremum_metric : SupremumMetric
        The metric instance from the fixture
    x : Various
        First input value
    y : Various
        Second input value
    expected : float
        Expected distance
    """
    result = supremum_metric.distance(x, y)
    assert result == pytest.approx(expected)


@pytest.mark.unit
def test_distance_numpy_arrays(supremum_metric):
    """Test the distance method with numpy arrays."""
    x = np.array([1, 2, 3])
    y = np.array([4, 6, 7])
    result = supremum_metric.distance(x, y)
    assert result == 4.0


@pytest.mark.unit
def test_distance_with_different_dimensions(supremum_metric):
    """Test that the distance method raises ValueError for different dimensions."""
    x = [1, 2, 3]
    y = [1, 2]

    with pytest.raises(ValueError):
        supremum_metric.distance(x, y)


@pytest.mark.unit
def test_distance_with_unsupported_types(supremum_metric):
    """Test that the distance method raises TypeError for unsupported types."""
    x = "string1"
    y = "string2"

    with pytest.raises(TypeError):
        supremum_metric.distance(x, y)


# Mock class to test vector-like objects with to_array method
class MockVector:
    def __init__(self, data):
        self.data = data

    def to_array(self):
        return self.data


@pytest.mark.unit
def test_distance_with_vector_objects(supremum_metric):
    """Test the distance method with objects that have to_array method."""
    x = MockVector([1, 2, 3])
    y = MockVector([4, 6, 7])

    result = supremum_metric.distance(x, y)
    assert result == 4.0


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y, expected",
    [
        ([[1, 2], [3, 4]], [[5, 6], [7, 8]], [[4.0, 6.0], [2.0, 4.0]]),
        ([1, 2, 3], [4, 5, 6], [3.0, 3.0, 3.0]),
    ],
)
def test_distances_collections(supremum_metric, x, y, expected):
    """
    Test the distances method with collections of points.

    Parameters
    ----------
    supremum_metric : SupremumMetric
        The metric instance from the fixture
    x : List
        First collection of points
    y : List
        Second collection of points
    expected : List
        Expected distances
    """
    result = supremum_metric.distances(x, y)

    # Check each element in the result
    if isinstance(result[0], list):
        for i in range(len(result)):
            for j in range(len(result[i])):
                assert result[i][j] == pytest.approx(expected[i][j])
    else:
        for i in range(len(result)):
            assert result[i] == pytest.approx(expected[i])


@pytest.mark.unit
def test_distances_single_point_to_collection(supremum_metric):
    """Test the distances method with a single point and a collection."""
    x = [1, 2]
    y = [[3, 4], [5, 6], [7, 8]]

    result = supremum_metric.distances(x, y)
    expected = [2.0, 4.0, 6.0]

    assert len(result) == len(expected)
    for i in range(len(result)):
        assert result[i] == pytest.approx(expected[i])


@pytest.mark.unit
def test_distances_collection_to_single_point(supremum_metric):
    """Test the distances method with a collection and a single point."""
    x = [[1, 2], [3, 4], [5, 6]]
    y = [7, 8]

    result = supremum_metric.distances(x, y)
    expected = [6.0, 4.0, 2.0]

    assert len(result) == len(expected)
    for i in range(len(result)):
        assert result[i] == pytest.approx(expected[i])


@pytest.mark.unit
def test_check_non_negativity(supremum_metric):
    """Test the check_non_negativity method."""
    # The supremum metric should always satisfy non-negativity
    assert supremum_metric.check_non_negativity([1, 2, 3], [4, 5, 6]) is True
    assert supremum_metric.check_non_negativity([-1, -2, -3], [-4, -5, -6]) is True
    assert supremum_metric.check_non_negativity(5, 10) is True


@pytest.mark.unit
def test_check_identity_of_indiscernibles(supremum_metric):
    """Test the check_identity_of_indiscernibles method."""
    # The supremum metric should satisfy identity of indiscernibles
    assert (
        supremum_metric.check_identity_of_indiscernibles([1, 2, 3], [1, 2, 3]) is True
    )
    assert (
        supremum_metric.check_identity_of_indiscernibles([1, 2, 3], [1, 2, 4]) is True
    )
    assert supremum_metric.check_identity_of_indiscernibles(5, 5) is True
    assert supremum_metric.check_identity_of_indiscernibles(5, 6) is True

    # Test with numpy arrays
    assert (
        supremum_metric.check_identity_of_indiscernibles(
            np.array([1, 2, 3]), np.array([1, 2, 3])
        )
        is True
    )


@pytest.mark.unit
def test_check_symmetry(supremum_metric):
    """Test the check_symmetry method."""
    # The supremum metric should always satisfy symmetry
    assert supremum_metric.check_symmetry([1, 2, 3], [4, 5, 6]) is True
    assert supremum_metric.check_symmetry([-1, -2, -3], [-4, -5, -6]) is True
    assert supremum_metric.check_symmetry(5, 10) is True


@pytest.mark.unit
def test_check_triangle_inequality(supremum_metric):
    """Test the check_triangle_inequality method."""
    # The supremum metric should satisfy the triangle inequality
    x = [1, 2, 3]
    y = [4, 5, 6]
    z = [7, 8, 9]
    assert supremum_metric.check_triangle_inequality(x, y, z) is True

    x = 1
    y = 5
    z = 10
    assert supremum_metric.check_triangle_inequality(x, y, z) is True

    # Test with numpy arrays
    x = np.array([1, 2, 3])
    y = np.array([4, 5, 6])
    z = np.array([7, 8, 9])
    assert supremum_metric.check_triangle_inequality(x, y, z) is True


@pytest.mark.unit
def test_calculate_supremum_helper(supremum_metric):
    """Test the _calculate_supremum helper method."""
    x = [1, 2, 3]
    y = [4, 6, 5]

    # Access the private method for testing
    result = supremum_metric._calculate_supremum(x, y)
    assert result == 4.0

    # Test with numpy arrays
    x_np = np.array(x)
    y_np = np.array(y)
    result = supremum_metric._calculate_supremum(x_np, y_np)
    assert result == 4.0

    # Test with empty arrays
    result = supremum_metric._calculate_supremum([], [])
    assert result == 0.0


@pytest.mark.unit
def test_edge_cases(supremum_metric):
    """Test edge cases for the SupremumMetric."""
    # Empty arrays should return 0
    assert supremum_metric.distance([], []) == 0.0

    # Arrays with zeros
    assert supremum_metric.distance([0, 0, 0], [0, 0, 0]) == 0.0

    # Negative numbers
    assert supremum_metric.distance([-1, -2, -3], [-4, -5, -6]) == 3.0

    # Very large numbers
    large_x = [1e10, 2e10, 3e10]
    large_y = [4e10, 5e10, 6e10]
    assert supremum_metric.distance(large_x, large_y) == 3e10


@pytest.mark.unit
def test_with_mock_vector_objects_distance(supremum_metric):
    """Test the distance method with mock vector objects."""

    class VectorWithShape:
        def __init__(self, data):
            self.data = data
            self.shape = (len(data),)

        def to_array(self):
            return self.data

    x = VectorWithShape([1, 2, 3])
    y = VectorWithShape([4, 5, 7])

    result = supremum_metric.distance(x, y)
    assert result == 4.0
