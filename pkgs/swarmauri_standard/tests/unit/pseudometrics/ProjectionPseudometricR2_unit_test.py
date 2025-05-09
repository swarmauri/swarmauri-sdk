import pytest
import logging
from swarmauri_standard.pseudometrics.ProjectionPseudometricR2 import ProjectionPseudometricR2

@pytest.fixture
def projection_pseudometric_r2():
    """Fixture to provide a ProjectionPseudometricR2 instance with different projection axes"""
    return ProjectionPseudometricR2(projection_axis="x")

@pytest.fixture(params=["x", "y"])
def projection_pseudometric_r2_parameterized(request):
    """Fixture to provide ProjectionPseudometricR2 instances with different projection axes"""
    return ProjectionPseudometricR2(projection_axis=request.param)

@pytest.mark.unit
def test_resource():
    """Test the resource property of the ProjectionPseudometricR2 class"""
    assert ProjectionPseudometricR2.resource == "Pseudometric"

@pytest.mark.unit
def test_type(projection_pseudometric_r2_parameterized):
    """Test the type property of the ProjectionPseudometricR2 class"""
    assert projection_pseudometric_r2_parameterized.__class__.__name__ == "ProjectionPseudometricR2"

@pytest.mark.unit
def test_initialization(projection_pseudometric_r2_parameterized):
    """Test the initialization of the ProjectionPseudometricR2 class"""
    assert hasattr(projection_pseudometric_r2_parameterized, "projection_axis")
    assert projection_pseudometric_r2_parameterized.projection_axis in ("x", "y")

@pytest.mark.unit
def test_str_repr(projection_pseudometric_r2_parameterized):
    """Test the string representation of the ProjectionPseudometricR2 class"""
    assert str(projection_pseudometric_r2_parameterized).startswith("ProjectionPseudometricR2")
    assert repr(projection_pseudometric_r2_parameterized) == str(projection_pseudometric_r2_parameterized)

@pytest.mark.unit
def test_distance(projection_pseudometric_r2_parameterized):
    """Test the distance calculation of the ProjectionPseudometricR2 class"""
    projection_pseudometric = projection_pseudometric_r2_parameterized
    
    # Test with valid points
    x = (1.0, 2.0)
    y = (3.0, 4.0)
    
    if projection_pseudometric.projection_axis == "x":
        expected_distance = abs(x[0] - y[0])
    else:
        expected_distance = abs(x[1] - y[1])
        
    assert projection_pseudometric.distance(x, y) == expected_distance
    
    # Test with invalid points
    with pytest.raises(ValueError):
        projection_pseudometric.distance((1.0,), (2.0, 3.0))
    
@pytest.mark.unit
def test_non_negativity(projection_pseudometric_r2_parameterized):
    """Test the non-negativity property of the ProjectionPseudometricR2 class"""
    projection_pseudometric = projection_pseudometric_r2_parameterized
    x = (1.0, 2.0)
    y = (3.0, 4.0)
    assert projection_pseudometric.check_non_negativity(x, y)

@pytest.mark.unit
def test_symmetry(projection_pseudometric_r2_parameterized):
    """Test the symmetry property of the ProjectionPseudometricR2 class"""
    projection_pseudometric = projection_pseudometric_r2_parameterized
    x = (1.0, 2.0)
    y = (3.0, 4.0)
    assert projection_pseudometric.check_symmetry(x, y)

@pytest.mark.unit
def test_triangle_inequality(projection_pseudometric_r2_parameterized):
    """Test the triangle inequality property of the ProjectionPseudometricR2 class"""
    projection_pseudometric = projection_pseudometric_r2_parameterized
    x = (1.0, 2.0)
    y = (3.0, 4.0)
    z = (5.0, 6.0)
    assert projection_pseudometric.check_triangle_inequality(x, y, z)

@pytest.mark.unit
def test_weak_identity(projection_pseudometric_r2_parameterized):
    """Test the weak identity property of the ProjectionPseudometricR2 class"""
    projection_pseudometric = projection_pseudometric_r2_parameterized
    x = (1.0, 2.0)
    y = (1.0, 3.0)
    assert projection_pseudometric.check_weak_identity(x, y)

@pytest.mark.unit
def test_invalid_axis():
    """Test invalid projection axis during initialization"""
    with pytest.raises(ValueError):
        ProjectionPseudometricR2(projection_axis="z")