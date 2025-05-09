import pytest
from swarmauri_standard.pseudometrics.ProjectionPseudometricR2 import ProjectionPseudometricR2
from typing import Sequence, Any
import logging

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.mark.unit
def test_default_initialization():
    """
    Test that the ProjectionPseudometricR2 initializes correctly with default parameters.
    """
    pm = ProjectionPseudometricR2()
    assert pm.projection_axis == 'x'
    assert pm.resource == "pseudometric"

@pytest.mark.unit
def test_custom_initialization():
    """
    Test that the ProjectionPseudometricR2 initializes correctly with custom parameters.
    """
    pm = ProjectionPseudometricR2(projection_axis='y')
    assert pm.projection_axis == 'y'
    assert pm.resource == "pseudometric"

@pytest.mark.unit
def test_distance_calculation():
    """
    Test that the distance calculation works correctly for various inputs.
    """
    pm_x = ProjectionPseudometricR2(projection_axis='x')
    pm_y = ProjectionPseudometricR2(projection_axis='y')

    # Test x-axis projection
    assert pm_x.distance((1, 2), (3, 4)) == 2.0
    assert pm_x.distance((5.5, 3), (8.5, 4)) == 3.0

    # Test y-axis projection
    assert pm_y.distance((1, 2), (3, 4)) == 2.0
    assert pm_y.distance((5, 3), (5, 6)) == 3.0

@pytest.mark.unit
def test_invalid_input_handling():
    """
    Test that invalid input raises appropriate errors.
    """
    pm = ProjectionPseudometricR2()
    
    # Test invalid projection axis
    with pytest.raises(ValueError):
        ProjectionPseudometricR2(projection_axis='z')

    # Test invalid input points
    with pytest.raises(ValueError):
        pm.distance((1,), (2, 3))

    with pytest.raises(ValueError):
        pm.distance(123, (2, 3))

@pytest.mark.unit
def test_distances_batch_processing():
    """
    Test that batch processing of distances works correctly.
    """
    pm = ProjectionPseudometricR2()
    
    # Test with multiple points
    points = [(1, 2), (3, 4), (5, 6)]
    distances = pm.distances(points, points)
    assert len(distances) == 3
    assert all(isinstance(d, float) for d in distances)

    # Test with mixed projection axes
    pm_y = ProjectionPseudometricR2(projection_axis='y')
    distances_y = pm_y.distances(points, points)
    assert len(distances_y) == 3
    assert all(isinstance(d, float) for d in distances_y)

@pytest.mark.unit
def test_serialization():
    """
    Test that serialization and deserialization work correctly.
    """
    pm = ProjectionPseudometricR2(projection_axis='y')
    
    # Serialize the instance
    serialized = pm.model_dump_json()
    assert isinstance(serialized, dict)
    
    # Deserialize the instance
    deserialized = ProjectionPseudometricR2.model_validate_json(serialized)
    assert isinstance(deserialized, ProjectionPseudometricR2)
    
    # Verify equality after serialization/deserialization
    assert pm == deserialized