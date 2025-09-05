import logging
from unittest.mock import MagicMock, Mock

import numpy as np
import pytest
from swarmauri_core.matrices.IMatrix import IMatrix

from swarmauri_standard.metrics.LpMetric import LpMetric
from swarmauri_standard.vectors.Vector import Vector

# Configure logging
logger = logging.getLogger(__name__)


@pytest.fixture
def vectors():
    """
    Create a set of test vectors.

    Returns
    -------
    Tuple[List[float], List[float], Vector, Vector]
        Tuple containing two lists and two Vector instances
    """
    v1 = [1, 2, 3]
    v2 = [4, 5, 6]
    real_v1 = Vector(value=[1, 2, 3])
    real_v2 = Vector(value=[4, 5, 6])
    return v1, v2, real_v1, real_v2


@pytest.fixture
def lp_metric_2():
    """
    Create an instance of LpMetric with p=2 (Euclidean distance).

    Returns
    -------
    LpMetric
        An instance of LpMetric with p=2
    """
    return LpMetric(p=2)


@pytest.fixture
def lp_metric_3():
    """
    Create an instance of LpMetric with p=3.

    Returns
    -------
    LpMetric
        An instance of LpMetric with p=3
    """
    return LpMetric(p=3)


@pytest.fixture
def matrices():
    """
    Create a set of test matrices.

    Returns
    -------
    Tuple[List[List[float]], List[List[float]], MockMatrix, MockMatrix]
        Tuple containing two 2D lists and two MockMatrix instances
    """
    mock_m1 = MagicMock(spec=IMatrix)
    mock_m2 = MagicMock(spec=IMatrix)

    m1 = [[1, 2], [3, 4]]
    m2 = [[5, 6], [7, 8]]
    mock_m1.to_array = Mock(return_value=np.array(m1))
    mock_m2.to_array = Mock(return_value=np.array(m2))
    return m1, m2, mock_m1, mock_m2


@pytest.mark.unit
def test_lp_metric_initialization():
    """Test LpMetric initialization with various p values."""
    # Valid p values
    metric_2 = LpMetric(p=2)
    assert metric_2.p == 2
    assert metric_2.type == "LpMetric"

    metric_3_5 = LpMetric(p=3.5)
    assert metric_3_5.p == 3.5

    # Invalid p values
    with pytest.raises(ValueError):
        LpMetric(p=1)  # p must be > 1

    with pytest.raises(ValueError):
        LpMetric(p=0)  # p must be > 1

    with pytest.raises(ValueError):
        LpMetric(p=-2)  # p must be > 1

    with pytest.raises(ValueError):
        LpMetric(p=float("inf"))  # p must be finite


@pytest.mark.unit
def test_resource_type():
    """Test that the resource type is correctly set."""
    metric = LpMetric(p=2)
    assert metric.resource == "Metric"


@pytest.mark.unit
def test_convert_to_array(lp_metric_2, vectors, matrices):
    """Test the _convert_to_array method with different input types."""
    v1, v2, mock_v1, mock_v2 = vectors
    m1, m2, mock_m1, mock_m2 = matrices

    # Test with lists
    np.testing.assert_array_equal(
        lp_metric_2._convert_to_array(v1), np.array([1, 2, 3])
    )

    # Test with IVector implementation
    np.testing.assert_array_equal(
        lp_metric_2._convert_to_array(mock_v1), np.array([1, 2, 3])
    )

    # Test with IMatrix implementation
    np.testing.assert_array_equal(
        lp_metric_2._convert_to_array(mock_m1), np.array([1, 2, 3, 4])
    )

    # Test with scalar values
    np.testing.assert_array_equal(lp_metric_2._convert_to_array(5), np.array([5]))

    # Test with string
    np.testing.assert_array_equal(
        lp_metric_2._convert_to_array("abc"),
        np.array([97, 98, 99]),  # ASCII values
    )

    # Test with unsupported type
    with pytest.raises(TypeError):
        lp_metric_2._convert_to_array({1: 2, 3: 4})  # Dictionary is not supported


@pytest.mark.unit
@pytest.mark.parametrize(
    "p,expected",
    [
        (2, 5.196152422706632),  # Euclidean distance
        (3, 4.326748710922225),  # p=3 distance
        (5, 3.737192818846552),  # p=5 distance - UPDATED value
    ],
)
def test_distance_with_lists(p, expected):
    """Test distance calculation with list inputs for different p values."""
    metric = LpMetric(p=p)
    v1 = [1, 2, 3]
    v2 = [4, 5, 6]

    result = metric.distance(v1, v2)
    assert abs(result - expected) < 1e-10


@pytest.mark.unit
def test_distance_with_vectors(lp_metric_2, vectors):
    """Test distance calculation with IVector implementations."""
    _, _, mock_v1, mock_v2 = vectors

    result = lp_metric_2.distance(mock_v1, mock_v2)
    expected = 5.196152422706632  # Euclidean distance between [1,2,3] and [4,5,6]
    assert abs(result - expected) < 1e-10


@pytest.mark.unit
def test_distance_with_matrices(lp_metric_2, matrices):
    """Test distance calculation with IMatrix implementations."""
    _, _, mock_m1, mock_m2 = matrices

    result = lp_metric_2.distance(mock_m1, mock_m2)
    expected = 8.0  # Euclidean distance between flattened matrices
    assert abs(result - expected) < 1e-10


@pytest.mark.unit
def test_distance_with_incompatible_shapes():
    """Test distance calculation with incompatible shapes."""
    metric = LpMetric(p=2)
    v1 = [1, 2, 3]
    v2 = [4, 5]

    with pytest.raises(ValueError):
        metric.distance(v1, v2)


@pytest.mark.unit
def test_distances_with_lists(lp_metric_2):
    """Test distances calculation with lists of points."""
    points_x = [[1, 2], [3, 4]]
    points_y = [[5, 6], [7, 8]]

    # Test pairwise distances
    result = lp_metric_2.distances(points_x, points_y)
    expected = [
        [5.656854249492381, 8.48528137423857],
        [2.8284271247461903, 5.656854249492381],
    ]

    assert len(result) == len(expected)
    for i in range(len(result)):
        for j in range(len(result[i])):
            assert abs(result[i][j] - expected[i][j]) < 1e-10

    # Test with single point in x
    result = lp_metric_2.distances([[1, 2]], points_y)
    expected = [5.656854249492381, 8.48528137423857]

    assert len(result) == len(expected)
    for i in range(len(result)):
        assert abs(result[i] - expected[i]) < 1e-10

    # Test with single point in y
    result = lp_metric_2.distances(points_x, [[5, 6]])
    expected = [5.656854249492381, 2.8284271247461903]

    assert len(result) == len(expected)
    for i in range(len(result)):
        assert abs(result[i] - expected[i]) < 1e-10


@pytest.mark.unit
def test_distances_with_vectors(lp_metric_2, vectors):
    """Test distances calculation with IVector implementations."""
    _, _, mock_v1, mock_v2 = vectors

    result = lp_metric_2.distances(mock_v1, mock_v2)
    expected = 5.196152422706632  # Same as distance for single vectors
    assert abs(result - expected) < 1e-10


@pytest.mark.unit
def test_check_non_negativity(lp_metric_2, vectors):
    """Test non-negativity axiom check."""
    v1, v2, _, _ = vectors

    # Distance should always be non-negative
    assert lp_metric_2.check_non_negativity(v1, v2) is True
    assert lp_metric_2.check_non_negativity(v1, v1) is True  # Same point


@pytest.mark.unit
def test_check_identity_of_indiscernibles(lp_metric_2, vectors):
    """Test identity of indiscernibles axiom check."""
    v1, v2, _, _ = vectors

    # Use a different assertion style
    assert lp_metric_2.check_identity_of_indiscernibles(v1, v1)
    assert lp_metric_2.check_identity_of_indiscernibles(v1, v2)


@pytest.mark.unit
def test_check_symmetry(lp_metric_2, vectors):
    """Test symmetry axiom check."""
    v1, v2, _, _ = vectors

    # Distance should be the same in both directions
    assert lp_metric_2.check_symmetry(v1, v2)


@pytest.mark.unit
def test_check_triangle_inequality(lp_metric_2):
    """Test triangle inequality axiom check."""
    v1 = [1, 2, 3]
    v2 = [4, 5, 6]
    v3 = [7, 8, 9]

    # Triangle inequality should hold
    assert lp_metric_2.check_triangle_inequality(v1, v2, v3) is True


@pytest.mark.unit
def test_get_norm(lp_metric_2, lp_metric_3):
    """Test getting the corresponding norm."""
    norm2 = lp_metric_2.get_norm()
    assert norm2.p == 2

    norm3 = lp_metric_3.get_norm()
    assert norm3.p == 3


@pytest.mark.unit
def test_edge_cases(lp_metric_2):
    """Test edge cases for distance calculation."""
    # Distance between identical points should be 0
    assert lp_metric_2.distance([0, 0, 0], [0, 0, 0]) == 0

    # Distance between a point and itself should be 0
    point = [1.5, 2.5, 3.5]
    assert lp_metric_2.distance(point, point) == 0

    # Test with very small values
    v1 = [1e-10, 2e-10, 3e-10]
    v2 = [4e-10, 5e-10, 6e-10]
    result = lp_metric_2.distance(v1, v2)
    expected = 5.196152422706632e-10
    assert abs(result - expected) < 1e-20


@pytest.mark.unit
def test_serialization():
    """Test serialization and deserialization of LpMetric."""
    original = LpMetric(p=2.5)
    json_str = original.model_dump_json()
    deserialized = LpMetric.model_validate_json(json_str)

    assert deserialized.p == original.p
    assert deserialized.type == original.type
    assert deserialized.resource == original.resource
