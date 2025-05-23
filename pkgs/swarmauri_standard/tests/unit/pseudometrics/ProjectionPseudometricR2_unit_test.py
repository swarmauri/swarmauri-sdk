import logging
from typing import List, Tuple

import numpy as np
import pytest

from swarmauri_standard.pseudometrics.ProjectionPseudometricR2 import (
    ProjectionPseudometricR2,
)

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture
def x_axis_projection():
    """
    Fixture for creating a ProjectionPseudometricR2 with x-axis projection.

    Returns
    -------
    ProjectionPseudometricR2
        A pseudometric that projects onto the x-axis
    """
    return ProjectionPseudometricR2(projection_axis=0)


@pytest.fixture
def y_axis_projection():
    """
    Fixture for creating a ProjectionPseudometricR2 with y-axis projection.

    Returns
    -------
    ProjectionPseudometricR2
        A pseudometric that projects onto the y-axis
    """
    return ProjectionPseudometricR2(projection_axis=1)


@pytest.fixture
def sample_points() -> List[Tuple[float, float]]:
    """
    Fixture providing a list of 2D points for testing.

    Returns
    -------
    List[Tuple[float, float]]
        A list of 2D points
    """
    return [(0, 0), (1, 0), (0, 1), (1, 1), (2, 3), (3, 2)]


@pytest.mark.unit
def test_initialization():
    """Test initialization of ProjectionPseudometricR2."""
    # Test default initialization
    pm = ProjectionPseudometricR2()
    assert pm.projection_axis == 0
    assert pm.type == "ProjectionPseudometricR2"

    # Test x-axis initialization
    pm = ProjectionPseudometricR2(projection_axis=0)
    assert pm.projection_axis == 0

    # Test y-axis initialization
    pm = ProjectionPseudometricR2(projection_axis=1)
    assert pm.projection_axis == 1

    # Test invalid axis initialization
    with pytest.raises(ValueError):
        ProjectionPseudometricR2(projection_axis=2)

    with pytest.raises(ValueError):
        ProjectionPseudometricR2(projection_axis=-1)


@pytest.mark.unit
@pytest.mark.parametrize(
    "point_format",
    [
        "tuple",
        "list",
        "numpy_array",
        "string",
    ],
)
def test_validate_and_extract_coordinates(x_axis_projection, point_format):
    """Test coordinate extraction from different point formats."""
    # Define point in different formats
    if point_format == "tuple":
        point = (2.5, 3.5)
    elif point_format == "list":
        point = [2.5, 3.5]
    elif point_format == "numpy_array":
        point = np.array([2.5, 3.5])
    elif point_format == "string":
        point = "2.5, 3.5"

    # Extract coordinates
    coords = x_axis_projection._validate_and_extract_coordinates(point)

    # Check if coordinates are extracted correctly
    assert isinstance(coords, tuple)
    assert len(coords) == 2
    assert coords[0] == 2.5
    assert coords[1] == 3.5


@pytest.mark.unit
def test_validate_and_extract_coordinates_errors(x_axis_projection):
    """Test error handling in coordinate extraction."""
    # Test with invalid dimensions
    with pytest.raises(ValueError):
        x_axis_projection._validate_and_extract_coordinates([1, 2, 3])

    # Test with invalid string format
    with pytest.raises(ValueError):
        x_axis_projection._validate_and_extract_coordinates("1,2,3")

    # Test with unsupported type
    with pytest.raises(TypeError):
        x_axis_projection._validate_and_extract_coordinates(123)


@pytest.mark.unit
def test_distance_x_axis(x_axis_projection, sample_points):
    """Test distance calculation with x-axis projection."""
    # Test with points having same x-coordinate
    assert x_axis_projection.distance((0, 0), (0, 5)) == 0
    assert x_axis_projection.distance((2, 3), (2, 7)) == 0

    # Test with points having different x-coordinates
    assert x_axis_projection.distance((0, 0), (3, 0)) == 3
    assert x_axis_projection.distance((1, 5), (4, 2)) == 3

    # Test with negative coordinates
    assert x_axis_projection.distance((-2, 0), (3, 0)) == 5
    assert x_axis_projection.distance((-2, -3), (-5, -1)) == 3


@pytest.mark.unit
def test_distance_y_axis(y_axis_projection, sample_points):
    """Test distance calculation with y-axis projection."""
    # Test with points having same y-coordinate
    assert y_axis_projection.distance((0, 0), (5, 0)) == 0
    assert y_axis_projection.distance((3, 2), (7, 2)) == 0

    # Test with points having different y-coordinates
    assert y_axis_projection.distance((0, 0), (0, 3)) == 3
    assert y_axis_projection.distance((5, 1), (2, 4)) == 3

    # Test with negative coordinates
    assert y_axis_projection.distance((0, -2), (0, 3)) == 5
    assert y_axis_projection.distance((-3, -2), (-1, -5)) == 3


@pytest.mark.unit
def test_distances_pairwise(x_axis_projection):
    """Test pairwise distance calculation."""
    xs = [(0, 0), (1, 0), (2, 0)]
    ys = [(0, 1), (1, 2), (3, 3)]

    expected = [
        [0, 1, 3],  # distances from (0,0) to each y
        [1, 0, 2],  # distances from (1,0) to each y
        [2, 1, 1],  # distances from (2,0) to each y
    ]

    result = x_axis_projection.distances(xs, ys)

    # Check dimensions
    assert len(result) == len(xs)
    assert len(result[0]) == len(ys)

    # Check values
    for i in range(len(xs)):
        for j in range(len(ys)):
            assert result[i][j] == expected[i][j]


@pytest.mark.unit
def test_distances_empty(x_axis_projection):
    """Test distance calculation with empty input."""
    assert x_axis_projection.distances([], []) == []
    assert x_axis_projection.distances([(0, 0)], []) == [[]]
    assert x_axis_projection.distances([], [(0, 0)]) == []


@pytest.mark.unit
def test_check_non_negativity(x_axis_projection, sample_points):
    """Test non-negativity property check."""
    # Test all pairs of sample points
    for p1 in sample_points:
        for p2 in sample_points:
            assert x_axis_projection.check_non_negativity(p1, p2) is True


@pytest.mark.unit
def test_check_symmetry(x_axis_projection, sample_points):
    """Test symmetry property check."""
    # Test all pairs of sample points
    for p1 in sample_points:
        for p2 in sample_points:
            assert x_axis_projection.check_symmetry(p1, p2) is True


@pytest.mark.unit
def test_check_triangle_inequality(x_axis_projection, sample_points):
    """Test triangle inequality property check."""
    # Test with a subset of point triples
    for i in range(len(sample_points)):
        for j in range(len(sample_points)):
            for k in range(len(sample_points)):
                p1 = sample_points[i]
                p2 = sample_points[j]
                p3 = sample_points[k]
                assert x_axis_projection.check_triangle_inequality(p1, p2, p3) is True


@pytest.mark.unit
def test_check_weak_identity(x_axis_projection, y_axis_projection):
    """Test weak identity property check."""
    # Points with same x but different y (should have distance 0 in x-projection)
    assert x_axis_projection.check_weak_identity((1, 2), (1, 5)) is True

    # Points with different x (should have distance > 0 in x-projection)
    assert x_axis_projection.check_weak_identity((1, 2), (3, 5)) is True

    # Points with same y but different x (should have distance 0 in y-projection)
    assert y_axis_projection.check_weak_identity((2, 1), (5, 1)) is True

    # Points with different y (should have distance > 0 in y-projection)
    assert y_axis_projection.check_weak_identity((2, 1), (5, 3)) is True

    # Same points (should have distance 0 in both projections)
    assert x_axis_projection.check_weak_identity((1, 1), (1, 1)) is True
    assert y_axis_projection.check_weak_identity((1, 1), (1, 1)) is True


@pytest.mark.unit
def test_pseudometric_properties(x_axis_projection):
    """Test that the implementation satisfies pseudometric properties."""
    points = [(0, 0), (1, 2), (3, 4), (5, 0), (0, 5)]

    # Property 1: d(x,x) = 0 for all x
    for p in points:
        assert x_axis_projection.distance(p, p) == 0

    # Property 2: d(x,y) = d(y,x) for all x,y
    for i, p1 in enumerate(points):
        for j, p2 in enumerate(points):
            assert x_axis_projection.distance(p1, p2) == x_axis_projection.distance(
                p2, p1
            )

    # Property 3: d(x,z) ≤ d(x,y) + d(y,z) for all x,y,z
    for p1 in points:
        for p2 in points:
            for p3 in points:
                d_xz = x_axis_projection.distance(p1, p3)
                d_xy = x_axis_projection.distance(p1, p2)
                d_yz = x_axis_projection.distance(p2, p3)
                assert (
                    d_xz <= d_xy + d_yz + 1e-10
                )  # Adding small tolerance for floating point


@pytest.mark.unit
def test_different_input_formats(x_axis_projection):
    """Test distance calculation with different input formats."""
    # Define points in different formats
    point1_tuple = (1, 2)
    point1_list = [1, 2]
    point1_numpy = np.array([1, 2])
    point1_string = "1, 2"

    point2_tuple = (4, 5)
    point2_list = [4, 5]
    point2_numpy = np.array([4, 5])
    point2_string = "4, 5"

    # Expected distance (in x-axis projection)
    expected_distance = 3

    # Test all combinations of formats
    formats1 = [point1_tuple, point1_list, point1_numpy, point1_string]
    formats2 = [point2_tuple, point2_list, point2_numpy, point2_string]

    for p1 in formats1:
        for p2 in formats2:
            assert x_axis_projection.distance(p1, p2) == expected_distance


@pytest.mark.unit
def test_serialization():
    """Test serialization and deserialization."""
    # Create an instance
    original = ProjectionPseudometricR2(projection_axis=1)

    # Serialize to JSON
    json_str = original.model_dump_json()

    # Deserialize from JSON
    deserialized = ProjectionPseudometricR2.model_validate_json(json_str)

    # Check if properties are preserved
    assert deserialized.projection_axis == original.projection_axis
    assert deserialized.type == original.type
