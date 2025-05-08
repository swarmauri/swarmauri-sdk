import pytest
import numpy as np
import logging
from swarmauri_standard.pseudometrics.ProjectionPseudometricR2 import ProjectionPseudometricR2

# Setup logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture
def x_axis_pseudometric():
    """
    Fixture that returns a ProjectionPseudometricR2 instance with x-axis projection.
    
    Returns:
        ProjectionPseudometricR2: A pseudometric instance that projects onto the x-axis
    """
    return ProjectionPseudometricR2(projection_axis=0)

@pytest.fixture
def y_axis_pseudometric():
    """
    Fixture that returns a ProjectionPseudometricR2 instance with y-axis projection.
    
    Returns:
        ProjectionPseudometricR2: A pseudometric instance that projects onto the y-axis
    """
    return ProjectionPseudometricR2(projection_axis=1)

@pytest.fixture
def sample_points():
    """
    Fixture that returns a list of sample 2D points for testing.
    
    Returns:
        list: A list of 2D points
    """
    return [
        [0, 0],
        [1, 0],
        [0, 1],
        [1, 1],
        [2, 3],
        [-1, 4]
    ]

@pytest.mark.unit
def test_initialization():
    """Test that the pseudometric initializes correctly with default parameters."""
    pm = ProjectionPseudometricR2()
    assert pm.projection_axis == 0  # Default should be x-axis
    assert pm.type == "ProjectionPseudometricR2"
    
    pm_y = ProjectionPseudometricR2(projection_axis=1)
    assert pm_y.projection_axis == 1

@pytest.mark.unit
def test_initialization_invalid_axis():
    """Test that initialization with invalid projection axis raises ValueError."""
    with pytest.raises(ValueError, match="projection_axis must be 0 .x-axis. or 1 .y-axis"):
        ProjectionPseudometricR2(projection_axis=2)
    
    with pytest.raises(ValueError):
        ProjectionPseudometricR2(projection_axis=-1)

@pytest.mark.unit
def test_get_projection_axis_name(x_axis_pseudometric, y_axis_pseudometric):
    """Test that get_projection_axis_name returns the correct axis name."""
    assert x_axis_pseudometric.get_projection_axis_name() == 'x'
    assert y_axis_pseudometric.get_projection_axis_name() == 'y'

@pytest.mark.unit
def test_set_projection_axis(x_axis_pseudometric):
    """Test that set_projection_axis correctly changes the projection axis."""
    assert x_axis_pseudometric.projection_axis == 0
    x_axis_pseudometric.set_projection_axis(1)
    assert x_axis_pseudometric.projection_axis == 1
    assert x_axis_pseudometric.get_projection_axis_name() == 'y'
    
    # Test invalid axis
    with pytest.raises(ValueError):
        x_axis_pseudometric.set_projection_axis(2)

@pytest.mark.unit
@pytest.mark.parametrize("point,is_valid", [
    ([0, 0], True),
    ((1, 2), True),
    (np.array([3, 4]), True),
    ([1, 2, 3], False),
    ([1], False),
    (np.array([[1, 2]]), False)
])
def test_validate_point(x_axis_pseudometric, point, is_valid):
    """Test that _validate_point correctly validates 2D points."""
    if is_valid:
        result = x_axis_pseudometric._validate_point(point)
        assert isinstance(result, np.ndarray)
        assert result.shape == (2,)
    else:
        with pytest.raises(ValueError, match="Points must be 2-dimensional"):
            x_axis_pseudometric._validate_point(point)

@pytest.mark.unit
@pytest.mark.parametrize("x,y,expected_x,expected_y", [
    ([0, 0], [1, 0], 1.0, 0.0),
    ([0, 0], [0, 1], 0.0, 1.0),
    ([1, 2], [3, 4], 2.0, 2.0),
    ([5, 6], [5, 10], 0.0, 4.0),
    ([-1, -2], [3, -2], 4.0, 0.0)
])
def test_distance(x_axis_pseudometric, y_axis_pseudometric, x, y, expected_x, expected_y):
    """Test that distance correctly calculates the projected distance."""
    assert x_axis_pseudometric.distance(x, y) == expected_x
    assert y_axis_pseudometric.distance(x, y) == expected_y

@pytest.mark.unit
def test_distance_symmetry(x_axis_pseudometric, sample_points):
    """Test that the distance function is symmetric: d(x,y) = d(y,x)."""
    for p1 in sample_points:
        for p2 in sample_points:
            d1 = x_axis_pseudometric.distance(p1, p2)
            d2 = x_axis_pseudometric.distance(p2, p1)
            assert d1 == d2

@pytest.mark.unit
def test_distance_non_negativity(x_axis_pseudometric, sample_points):
    """Test that the distance function is non-negative: d(x,y) ≥ 0."""
    for p1 in sample_points:
        for p2 in sample_points:
            assert x_axis_pseudometric.distance(p1, p2) >= 0

@pytest.mark.unit
def test_triangle_inequality(x_axis_pseudometric, sample_points):
    """Test that the distance function satisfies the triangle inequality: d(x,z) ≤ d(x,y) + d(y,z)."""
    for p1 in sample_points:
        for p2 in sample_points:
            for p3 in sample_points:
                d_xz = x_axis_pseudometric.distance(p1, p3)
                d_xy = x_axis_pseudometric.distance(p1, p2)
                d_yz = x_axis_pseudometric.distance(p2, p3)
                assert d_xz <= d_xy + d_yz + 1e-10  # Adding small epsilon for floating point comparison

@pytest.mark.unit
def test_batch_distance(x_axis_pseudometric):
    """Test that batch_distance correctly calculates distances for multiple pairs."""
    xs = [[0, 0], [1, 2], [3, 4]]
    ys = [[1, 0], [2, 3], [3, 5]]
    
    expected = [1.0, 1.0, 0.0]  # For x-axis projection
    result = x_axis_pseudometric.batch_distance(xs, ys)
    
    assert len(result) == len(expected)
    for r, e in zip(result, expected):
        assert r == e

@pytest.mark.unit
def test_batch_distance_different_lengths(x_axis_pseudometric):
    """Test that batch_distance raises ValueError for lists of different lengths."""
    xs = [[0, 0], [1, 2]]
    ys = [[1, 0], [2, 3], [3, 5]]
    
    with pytest.raises(ValueError, match="Input lists must have the same length"):
        x_axis_pseudometric.batch_distance(xs, ys)

@pytest.mark.unit
def test_batch_distance_invalid_points(x_axis_pseudometric):
    """Test that batch_distance raises ValueError for invalid points."""
    xs = [[0, 0], [1, 2, 3]]  # Second point is invalid
    ys = [[1, 0], [2, 3]]
    
    with pytest.raises(ValueError, match="Points must be 2-dimensional"):
        x_axis_pseudometric.batch_distance(xs, ys)

@pytest.mark.unit
def test_pairwise_distances(x_axis_pseudometric, sample_points):
    """Test that pairwise_distances correctly calculates all pairwise distances."""
    result = x_axis_pseudometric.pairwise_distances(sample_points)
    
    # Verify dimensions
    assert len(result) == len(sample_points)
    for row in result:
        assert len(row) == len(sample_points)
    
    # Verify specific distances (for x-axis projection)
    # Diagonal should be all zeros
    for i in range(len(sample_points)):
        assert result[i][i] == 0.0
    
    # Check a few specific values
    assert result[0][1] == 1.0  # [0,0] to [1,0]
    assert result[0][2] == 0.0  # [0,0] to [0,1]
    assert result[1][4] == 1.0  # [1,0] to [2,3]
    
    # Verify symmetry
    for i in range(len(sample_points)):
        for j in range(len(sample_points)):
            assert result[i][j] == result[j][i]

@pytest.mark.unit
def test_pairwise_distances_invalid_points(x_axis_pseudometric):
    """Test that pairwise_distances raises ValueError for invalid points."""
    invalid_points = [[0, 0], [1, 2], [3, 4, 5]]  # Third point is invalid
    
    with pytest.raises(ValueError, match="Points must be 2-dimensional"):
        x_axis_pseudometric.pairwise_distances(invalid_points)

@pytest.mark.unit
def test_pseudometric_properties(x_axis_pseudometric, sample_points):
    """Test that the pseudometric satisfies the required properties."""
    # Test identity of non-discernibles is NOT satisfied (pseudometric property)
    # Points with same x-coordinate but different y-coordinate should have distance 0
    p1 = [1, 0]
    p2 = [1, 5]  # Different point but same x-coordinate
    assert x_axis_pseudometric.distance(p1, p2) == 0.0

@pytest.mark.unit
def test_component_registration():
    """Test that the component is properly registered."""
    from swarmauri_base.ComponentBase import ComponentBase
    from swarmauri_base.pseudometrics.PseudometricBase import PseudometricBase
    
    # Verify the class is registered with the correct base class
    assert ProjectionPseudometricR2 in ComponentBase._registered_types[PseudometricBase]
    
    # Verify the type string is correctly registered
    registry_entry = None
    for cls in ComponentBase._registered_types[PseudometricBase]:
        if cls.__name__ == "ProjectionPseudometricR2":
            registry_entry = cls
            break
    
    assert registry_entry is not None
    assert registry_entry.type == "ProjectionPseudometricR2"

@pytest.mark.unit
def test_serialization():
    """Test that the pseudometric can be serialized and deserialized."""
    pm = ProjectionPseudometricR2(projection_axis=1)
    
    # Serialize
    json_data = pm.model_dump_json()
    
    # Deserialize
    pm_restored = ProjectionPseudometricR2.model_validate_json(json_data)
    
    # Verify properties are preserved
    assert pm_restored.projection_axis