import pytest
from swarmauri_standard.seminorms.ZeroSeminorm import ZeroSeminorm
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix

pytestmark = pytest.mark.unit


@pytest.fixture
def zero_seminorm_instance():
    """Fixture to provide a ZeroSeminorm instance for testing."""
    return ZeroSeminorm()


def test_resource(zero_seminorm_instance):
    """Tests that the resource type is correctly set."""
    assert zero_seminorm_instance.resource == "seminorm"


def test_type(zero_seminorm_instance):
    """Tests that the type is correctly set to 'ZeroSeminorm'."""
    assert zero_seminorm_instance.type == "ZeroSeminorm"


@pytest.mark.parametrize(
    "input_type",
    [
        (IVector()),
        (IMatrix()),
        ("test_string"),
        (lambda x: x),
        ([1, 2, 3]),
        (("a", "b", "c")),
    ],
)
def test_compute(input_type, zero_seminorm_instance):
    """Tests that the compute method returns 0.0 for various input types."""
    result = zero_seminorm_instance.compute(input_type)
    assert result == 0.0


def test_check_triangle_inequality(zero_seminorm_instance):
    """Tests the triangle inequality check."""
    a = IVector()
    b = IMatrix()
    result = zero_seminorm_instance.check_triangle_inequality(a, b)
    assert result is True


@pytest.mark.parametrize("scalar", [1, -1, 0, 2.5])
def test_check_scalar_homogeneity(zero_seminorm_instance, scalar):
    """Tests scalar homogeneity with different scalar values."""
    a = IVector()
    result = zero_seminorm_instance.check_scalar_homogeneity(a, scalar)
    assert result is True
