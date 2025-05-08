import logging
import pytest
import numpy as np
from typing import Callable, Any, Union
from swarmauri_standard.seminorms.PointEvaluationSeminorm import PointEvaluationSeminorm

# Set up logging
logger = logging.getLogger(__name__)

@pytest.fixture
def point_evaluation_seminorm():
    """
    Fixture that returns a PointEvaluationSeminorm instance with evaluation point 0.
    
    Returns
    -------
    PointEvaluationSeminorm
        An instance of PointEvaluationSeminorm with point=0.
    """
    return PointEvaluationSeminorm(point=0)

@pytest.fixture
def sample_functions():
    """
    Fixture that returns a set of sample functions for testing.
    
    Returns
    -------
    dict
        Dictionary containing various test functions.
    """
    return {
        'constant': lambda x: 5,
        'linear': lambda x: 2*x + 1,
        'quadratic': lambda x: x**2,
        'sine': lambda x: np.sin(x),
        'complex': lambda x: 3 + 4j if x == 0 else 1 + 1j,
        'zero': lambda x: 0
    }

@pytest.mark.unit
def test_initialization():
    """Test that the PointEvaluationSeminorm initializes correctly with different point types."""
    # Test with different point types
    points = [0, 1.5, (1, 2), "test_point", [1, 2, 3]]
    
    for point in points:
        seminorm = PointEvaluationSeminorm(point=point)
        assert seminorm.point == point
        assert seminorm.type == "PointEvaluationSeminorm"

@pytest.mark.unit
def test_resource_and_type():
    """Test that the resource and type attributes are set correctly."""
    seminorm = PointEvaluationSeminorm(point=0)
    assert seminorm.type == "PointEvaluationSeminorm"
    # Resource is inherited from SeminormBase
    assert hasattr(seminorm, "resource")

@pytest.mark.unit
def test_evaluate(point_evaluation_seminorm, sample_functions):
    """Test the evaluate method with various functions."""
    # Test evaluation of different functions at point 0
    assert point_evaluation_seminorm.evaluate(sample_functions['constant']) == 5.0
    assert point_evaluation_seminorm.evaluate(sample_functions['linear']) == 1.0
    assert point_evaluation_seminorm.evaluate(sample_functions['quadratic']) == 0.0
    assert point_evaluation_seminorm.evaluate(sample_functions['sine']) == 0.0
    assert point_evaluation_seminorm.evaluate(sample_functions['complex']) == 5.0  # |3 + 4j| = 5
    assert point_evaluation_seminorm.evaluate(sample_functions['zero']) == 0.0

@pytest.mark.unit
def test_evaluate_with_different_points():
    """Test evaluate method with different evaluation points."""
    # Test with point = 1
    seminorm_at_1 = PointEvaluationSeminorm(point=1)
    assert seminorm_at_1.evaluate(lambda x: x**2) == 1.0
    assert seminorm_at_1.evaluate(lambda x: 2*x + 1) == 3.0
    
    # Test with point = -1
    seminorm_at_neg1 = PointEvaluationSeminorm(point=-1)
    assert seminorm_at_neg1.evaluate(lambda x: x**2) == 1.0
    assert seminorm_at_neg1.evaluate(lambda x: 2*x + 1) == 1.0  # |-1| = 1

@pytest.mark.unit
def test_evaluate_error_handling():
    """Test error handling in the evaluate method."""
    seminorm = PointEvaluationSeminorm(point=0)
    
    # Function that raises an exception
    def problematic_function(x):
        raise ValueError("Test error")
    
    with pytest.raises(ValueError):
        seminorm.evaluate(problematic_function)

@pytest.mark.unit
def test_scale(point_evaluation_seminorm, sample_functions):
    """Test the scale method."""
    # Test scaling with different alpha values
    assert point_evaluation_seminorm.scale(sample_functions['constant'], 2) == 10.0
    assert point_evaluation_seminorm.scale(sample_functions['linear'], 3) == 3.0
    assert point_evaluation_seminorm.scale(sample_functions['quadratic'], 5) == 0.0
    
    # Test with negative alpha
    assert point_evaluation_seminorm.scale(sample_functions['constant'], -2) == 10.0
    
    # Test with zero alpha
    assert point_evaluation_seminorm.scale(sample_functions['constant'], 0) == 0.0

@pytest.mark.unit
def test_triangle_inequality(point_evaluation_seminorm):
    """Test that the triangle inequality holds for various function pairs."""
    # Define test functions
    f = lambda x: 3*x + 2
    g = lambda x: x**2 - 1
    h = lambda x: np.sin(x)
    
    # Test triangle inequality for different function combinations
    assert point_evaluation_seminorm.triangle_inequality(f, g)
    assert point_evaluation_seminorm.triangle_inequality(f, h)
    assert point_evaluation_seminorm.triangle_inequality(g, h)
    
    # Test with complex-valued functions
    complex_f = lambda x: 1 + 2j if x == 0 else 0
    complex_g = lambda x: 3 - 1j if x == 0 else 0
    assert point_evaluation_seminorm.triangle_inequality(complex_f, complex_g)

@pytest.mark.unit
def test_is_zero(point_evaluation_seminorm, sample_functions):
    """Test the is_zero method with different functions and tolerances."""
    # Functions that are zero at the evaluation point
    assert point_evaluation_seminorm.is_zero(sample_functions['quadratic'])
    assert point_evaluation_seminorm.is_zero(sample_functions['sine'])
    assert point_evaluation_seminorm.is_zero(sample_functions['zero'])
    
    # Functions that are not zero at the evaluation point
    assert not point_evaluation_seminorm.is_zero(sample_functions['constant'])
    assert not point_evaluation_seminorm.is_zero(sample_functions['linear'])
    
    # Test with custom tolerance
    almost_zero = lambda x: 1e-5 if x == 0 else 1
    assert not point_evaluation_seminorm.is_zero(almost_zero, tolerance=1e-6)
    assert point_evaluation_seminorm.is_zero(almost_zero, tolerance=1e-4)

@pytest.mark.unit
def test_is_definite(point_evaluation_seminorm):
    """Test that is_definite correctly returns False for PointEvaluationSeminorm."""
    # Point evaluation seminorms are not definite
    assert not point_evaluation_seminorm.is_definite()

@pytest.mark.unit
def test_serialization():
    """Test serialization and deserialization of PointEvaluationSeminorm."""
    original = PointEvaluationSeminorm(point=3.14)
    json_str = original.model_dump_json()
    
    # Deserialize
    deserialized = PointEvaluationSeminorm.model_validate_json(json_str)
    
    # Check that the deserialized object has the same properties
    assert deserialized.point == original.point
    assert deserialized.type == original.type

@pytest.mark.unit
@pytest.mark.parametrize("point,function,expected", [
    (0, lambda x: x**2, 0.0),
    (1, lambda x: x**2, 1.0),
    (2, lambda x: x**2, 4.0),
    (0, lambda x: 2*x + 1, 1.0),
    (1, lambda x: 2*x + 1, 3.0),
    (-1, lambda x: 2*x + 1, 1.0),
])
def test_parametrized_evaluate(point, function, expected):
    """Parametrized test for evaluate method with different points and functions."""
    seminorm = PointEvaluationSeminorm(point=point)
    result = seminorm.evaluate(function)
    assert pytest.approx(result) == expected

@pytest.mark.unit
def test_with_custom_point_types():
    """Test the seminorm with custom point types."""
    # Test with tuple point
    tuple_point = (1, 2, 3)
    tuple_seminorm = PointEvaluationSeminorm(point=tuple_point)
    assert tuple_seminorm.evaluate(lambda p: sum(p)) == 6.0
    
    # Test with dict point
    dict_point = {"x": 1, "y": 2}
    dict_seminorm = PointEvaluationSeminorm(point=dict_point)
    assert dict_seminorm.evaluate(lambda p: p["x"] + p["y"]) == 3.0