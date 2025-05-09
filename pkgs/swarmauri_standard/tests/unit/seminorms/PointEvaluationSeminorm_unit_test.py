import pytest
import logging
from swarmauri_standard.swarmauri_standard.seminorms.PointEvaluationSeminorm import (
    PointEvaluationSeminorm,
)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def point_evaluation_seminorm():
    """Fixture to provide a default PointEvaluationSeminorm instance."""
    return PointEvaluationSeminorm()


@pytest.mark.unit
def test_point_evaluation_seminorm_resource(point_evaluation_seminorm):
    """Test that the resource attribute is correctly set."""
    assert point_evaluation_seminorm.resource == "Seminorm"


@pytest.mark.unit
def test_point_evaluation_seminorm_type():
    """Test that the type attribute is correctly set."""
    assert PointEvaluationSeminorm.type == "PointEvaluationSeminorm"


@pytest.mark.unit
def test_point_evaluation_seminorm_compute_callable(point_evaluation_seminorm):
    """Test computation with a callable input."""
    # Test with a simple function
    result = point_evaluation_seminorm.compute(lambda x: x)
    assert result == 0.0


@pytest.mark.unit
def test_point_evaluation_seminorm_compute_vector():
    """Test computation with a vector input."""
    seminorm = PointEvaluationSeminorm(evaluation_point=(0,))
    result = seminorm.compute([1, 2, 3])
    assert result == 1.0


@pytest.mark.unit
def test_point_evaluation_seminorm_compute_invalid_input():
    """Test that invalid input raises ValueError."""
    seminorm = PointEvaluationSeminorm()
    with pytest.raises(ValueError):
        seminorm.compute("invalid_input")


@pytest.mark.unit
def test_point_evaluation_seminorm_triangle_inequality():
    """Test the triangle inequality property."""
    seminorm = PointEvaluationSeminorm(evaluation_point=(0,))

    # Test with simple functions
    f = lambda x, y: x
    g = lambda x, y: y

    seminorm_f = seminorm.compute(f)
    seminorm_g = seminorm.compute(g)
    seminorm_f_plus_g = seminorm.compute(lambda x, y: f(x, y) + g(x, y))

    assert seminorm_f_plus_g <= seminorm_f + seminorm_g


@pytest.mark.unit
def test_point_evaluation_seminorm_scalar_homogeneity():
    """Test scalar homogeneity property."""
    seminorm = PointEvaluationSeminorm(evaluation_point=(0,))

    # Test with scalar multiplication
    f = lambda x: x
    scalar = 2.0

    seminorm_f = seminorm.compute(f)
    seminorm_scaled_f = seminorm.compute(lambda x: scalar * f(x))

    assert seminorm_scaled_f == scalar * seminorm_f


@pytest.mark.unit
def test_point_evaluation_seminorm_zero_scalar():
    """Test scalar homogeneity with zero scalar."""
    seminorm = PointEvaluationSeminorm(evaluation_point=(0,))

    # Test with zero scalar
    f = lambda x: x
    scalar = 0.0

    seminorm_f = seminorm.compute(f)
    seminorm_scaled_f = seminorm.compute(lambda x: scalar * f(x))

    assert seminorm_scaled_f == scalar * seminorm_f


@pytest.mark.unit
def test_point_evaluation_seminorm_negative_scalar():
    """Test scalar homogeneity with negative scalar."""
    seminorm = PointEvaluationSeminorm(evaluation_point=(0,))

    # Test with negative scalar
    f = lambda x: x
    scalar = -1.0

    seminorm_f = seminorm.compute(f)
    seminorm_scaled_f = seminorm.compute(lambda x: scalar * f(x))

    assert seminorm_scaled_f == scalar * seminorm_f
