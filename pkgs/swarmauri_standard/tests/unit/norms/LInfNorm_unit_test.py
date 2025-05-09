import pytest
import logging
from swarmauri_standard.norms.LInfNorm import LInfNorm

@pytest.fixture
def linf_norm_instance():
    """Fixture to provide a fresh LInfNorm instance for each test."""
    return LInfNorm()

@pytest.mark.unit
def test_resource_type(linf_norm_instance):
    """Test that the resource type is correctly set."""
    assert linf_norm_instance.resource == "LInfNorm"

@pytest.mark.unit
def test_type(linf_norm_instance):
    """Test that the type string is correctly implemented."""
    assert linf_norm_instance.type == "LInfNorm"

@pytest.mark.unit
@pytest.mark.parametrize("input_data,expected_output", [
    ([1.0, 2.0, 3.0], 3.0),
    ((-5.0, 3.0, 2.0), 5.0),
    ("1.0 2.0 3.0", 3.0),
    (lambda: [1.0, 2.0, 3.0], 3.0)
])
def test_compute(linf_norm_instance, input_data, expected_output):
    """Test the compute method with different input types."""
    assert linf_norm_instance.compute(input_data) == expected_output

@pytest.mark.unit
def test_compute_invalid_input(linf_norm_instance):
    """Test that compute raises ValueError for invalid input types."""
    with pytest.raises(ValueError):
        linf_norm_instance.compute("invalid_string")

@pytest.mark.unit
def test_compute_callable_input(linf_norm_instance):
    """Test compute with a callable that returns a sequence."""
    def test_callable():
        return [1.0, 2.0, 3.0]
    assert linf_norm_instance.compute(test_callable) == 3.0

@pytest.mark.unit
def test_check_non_negativity(linf_norm_instance):
    """Test the non-negativity property."""
    assert linf_norm_instance.check_non_negativity([1.0, 2.0, 3.0]) is True

@pytest.mark.unit
def test_check_triangle_inequality(linf_norm_instance):
    """Test the triangle inequality property."""
    x = [1.0, 2.0]
    y = [2.0, 3.0]
    assert linf_norm_instance.check_triangle_inequality(x, y) is True

@pytest.mark.unit
def test_check_absolute_homogeneity(linf_norm_instance):
    """Test the absolute homogeneity property."""
    x = [1.0, 2.0]
    alpha = 2.0
    assert linf_norm_instance.check_absolute_homogeneity(x, alpha) is True

@pytest.mark.unit
def test_check_definiteness(linf_norm_instance):
    """Test the definiteness property."""
    zero_vector = [0.0, 0.0]
    non_zero_vector = [1.0, 2.0]
    assert linf_norm_instance.check_definiteness(zero_vector) is True
    assert linf_norm_instance.check_definiteness(non_zero_vector) is True

@pytest.mark.unit
def test_compute_returns_zero_only_for_zero_input(linf_norm_instance):
    """Test that compute returns zero only for zero input."""
    zero_input = [0.0, 0.0]
    non_zero_input = [1.0, 2.0]
    assert linf_norm_instance.compute(zero_input) == 0.0
    assert linf_norm_instance.compute(non_zero_input) != 0.0

logger = logging.getLogger(__name__)