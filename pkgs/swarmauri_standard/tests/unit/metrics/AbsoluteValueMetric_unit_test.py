import logging

import numpy as np
import pytest
from swarmauri_base.ComponentBase import ResourceTypes
from swarmauri_base.metrics.MetricBase import MetricBase

from swarmauri_standard.metrics.AbsoluteValueMetric import AbsoluteValueMetric
from swarmauri_standard.vectors.Vector import Vector

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def vector_pair():
    """
    Fixture providing a pair of Vector instances for testing.

    Returns
    -------
    Tuple[Vector, Vector]
        A pair of Vector instances
    """
    vec1 = Vector(value=[1, 2, 3])
    vec2 = Vector(value=[4, 5, 6])
    return vec1, vec2


@pytest.fixture
def metric():
    """
    Fixture that provides an instance of AbsoluteValueMetric.

    Returns
    -------
    AbsoluteValueMetric
        A fresh instance of the AbsoluteValueMetric class
    """
    return AbsoluteValueMetric()


@pytest.mark.unit
def test_inheritance():
    """Test that AbsoluteValueMetric inherits from MetricBase."""
    metric = AbsoluteValueMetric()
    assert isinstance(metric, MetricBase)


@pytest.mark.unit
def test_type_and_resource():
    """Test that type and resource attributes are correctly set."""
    metric = AbsoluteValueMetric()
    assert metric.type == "AbsoluteValueMetric"
    assert metric.resource == ResourceTypes.METRIC.value


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y, expected",
    [
        (5, 10, 5),
        (10, 5, 5),
        (0, 0, 0),
        (-5, 5, 10),
        (3.14, 2.71, 0.43),
    ],
)
def test_distance(metric, x, y, expected):
    """
    Test the distance method with various inputs.

    Parameters
    ----------
    metric : AbsoluteValueMetric
        The metric instance from the fixture
    x : float
        First input value
    y : float
        Second input value
    expected : float
        Expected distance result
    """
    result = metric.distance(x, y)
    assert abs(result - expected) < 1e-10


@pytest.mark.unit
def test_distance_invalid_input(metric):
    """Test that distance method raises TypeError for non-numeric inputs."""
    with pytest.raises(TypeError):
        metric.distance("a", 5)

    with pytest.raises(TypeError):
        metric.distance(5, "b")

    with pytest.raises(TypeError):
        metric.distance([1, 2], 5)


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y, expected",
    [
        ([1], [2, 3, 4], [1, 2, 3]),
        ([1, 2, 3], [5], [4, 3, 2]),
        ([1, 2], [3, 4], [[2, 3], [1, 2]]),
    ],
)
def test_distances(metric, x, y, expected):
    """
    Test the distances method with various inputs.

    Parameters
    ----------
    metric : AbsoluteValueMetric
        The metric instance from the fixture
    x : List[float]
        First input collection
    y : List[float]
        Second input collection
    expected : Union[List[float], List[List[float]]]
        Expected distances result
    """
    result = metric.distances(x, y)

    # Flatten lists for comparison if they are nested
    if isinstance(result[0], list):
        assert len(result) == len(expected)
        for i in range(len(result)):
            for j in range(len(result[i])):
                assert abs(result[i][j] - expected[i][j]) < 1e-10
    else:
        assert len(result) == len(expected)
        for i in range(len(result)):
            assert abs(result[i] - expected[i]) < 1e-10


@pytest.mark.unit
def test_distances_with_numpy_arrays(metric):
    """Test the distances method with numpy arrays as input."""
    x = np.array([1, 2, 3])
    y = np.array([4, 5, 6])

    result = metric.distances(x, y)
    expected = [[3, 4, 5], [2, 3, 4], [1, 2, 3]]

    assert len(result) == len(expected)
    for i in range(len(result)):
        for j in range(len(result[i])):
            assert abs(result[i][j] - expected[i][j]) < 1e-10


@pytest.mark.unit
def test_distances_invalid_input(metric):
    """Test that distances method raises appropriate errors for invalid inputs."""
    with pytest.raises(TypeError):
        metric.distances("a", [1, 2, 3])

    with pytest.raises(TypeError):
        metric.distances([1, 2, 3], "b")


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y",
    [
        (5, 10),
        (0, 0),
        (-5, 5),
        (3.14, 2.71),
    ],
)
def test_check_non_negativity(metric, x, y):
    """
    Test the check_non_negativity method.

    Parameters
    ----------
    metric : AbsoluteValueMetric
        The metric instance from the fixture
    x : float
        First input value
    y : float
        Second input value
    """
    assert metric.check_non_negativity(x, y) is True


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y, expected",
    [
        (5, 5, True),
        (5, 10, True),
        (3.14, 3.14, True),
        (0, 0, True),
    ],
)
def test_check_identity_of_indiscernibles(metric, x, y, expected):
    """
    Test the check_identity_of_indiscernibles method.

    Parameters
    ----------
    metric : AbsoluteValueMetric
        The metric instance from the fixture
    x : float
        First input value
    y : float
        Second input value
    expected : bool
        Expected result
    """
    assert metric.check_identity_of_indiscernibles(x, y) is expected


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y",
    [
        (5, 10),
        (10, 5),
        (0, 0),
        (-5, 5),
        (5, -5),
        (3.14, 2.71),
    ],
)
def test_check_symmetry(metric, x, y):
    """
    Test the check_symmetry method.

    Parameters
    ----------
    metric : AbsoluteValueMetric
        The metric instance from the fixture
    x : float
        First input value
    y : float
        Second input value
    """
    assert metric.check_symmetry(x, y) is True


@pytest.mark.unit
@pytest.mark.parametrize(
    "x, y, z",
    [
        (0, 5, 10),
        (10, 5, 0),
        (0, 0, 0),
        (-5, 0, 5),
        (3.14, 2.71, 1.41),
    ],
)
def test_check_triangle_inequality(metric, x, y, z):
    """
    Test the check_triangle_inequality method.

    Parameters
    ----------
    metric : AbsoluteValueMetric
        The metric instance from the fixture
    x : float
        First input value
    y : float
        Second input value
    z : float
        Third input value
    """
    assert metric.check_triangle_inequality(x, y, z) is True


@pytest.mark.unit
@pytest.mark.parametrize(
    "input_val, expected",
    [
        (5, [5.0]),
        ([1, 2, 3], [1.0, 2.0, 3.0]),
        (np.array([1, 2, 3]), [1.0, 2.0, 3.0]),
    ],
)
def test_to_list(metric, input_val, expected):
    """
    Test the _to_list private method.

    Parameters
    ----------
    metric : AbsoluteValueMetric
        The metric instance from the fixture
    input_val : Union[float, List[float], np.ndarray]
        Input value to convert
    expected : List[float]
        Expected result
    """
    result = metric._to_list(input_val)
    assert result == expected


@pytest.mark.unit
def test_to_list_invalid_input(metric):
    """Test that _to_list method raises appropriate errors for invalid inputs."""
    with pytest.raises(TypeError):
        metric._to_list("not a number")

    with pytest.raises(TypeError):
        metric._to_list(["a", "b", "c"])


@pytest.mark.unit
def test_serialization():
    """Test serialization and deserialization of AbsoluteValueMetric."""
    metric = AbsoluteValueMetric()
    json_str = metric.model_dump_json()

    # Deserialize
    deserialized = AbsoluteValueMetric.model_validate_json(json_str)

    # Check that the deserialized object is an instance of AbsoluteValueMetric
    assert isinstance(deserialized, AbsoluteValueMetric)
    assert deserialized.type == "AbsoluteValueMetric"
    assert deserialized.resource == ResourceTypes.METRIC.value


@pytest.mark.unit
def test_vector_input(metric, vector_pair):
    """
    Test the distances method with actual Vector inputs.

    Parameters
    ----------
    metric : AbsoluteValueMetric
        The metric instance from the fixture
    vector_pair : Tuple[Vector, Vector]
        Pair of Vector instances
    """
    vec1, vec2 = vector_pair

    # Test distances with Vector class
    result = metric.distances(vec1, vec2)
    expected = [[3, 4, 5], [2, 3, 4], [1, 2, 3]]

    assert len(result) == len(expected)
    for i in range(len(result)):
        for j in range(len(result[i])):
            assert abs(result[i][j] - expected[i][j]) < 1e-10
