import pytest
from swarmauri_standard.metrics.SobolevMetric import SobolevMetric


@pytest.fixture
def sobolev_metric(order: int = 1):
    """Fixture to create a SobolevMetric instance with specified order."""
    return SobolevMetric(order=order)


def test_type():
    """Test that the type is correctly set to 'SobolevMetric'."""
    assert SobolevMetric.type == "SobolevMetric"


def test_resource():
    """Test that the resource is correctly set."""
    assert SobolevMetric.resource == "Metric"


def test_order_initialization(sobolev_metric):
    """Test that the order is correctly initialized."""
    assert sobolev_metric.order == 1
    # Test with different order
    sobolev_metric = SobolevMetric(order=2)
    assert sobolev_metric.order == 2


def test_non_negativity_axiom(sobolev_metric):
    """Test the non-negativity axiom."""

    # Test with simple functions
    def f(x):
        return x

    def g(x):
        return x

    distance = sobolev_metric.distance(f, g)
    assert distance >= 0

    # Test with different functions
    def f(x):
        return x

    def g(x):
        return -x

    distance = sobolev_metric.distance(f, g)
    assert distance >= 0


def test_identity_axiom(sobolev_metric):
    """Test the identity of indiscernibles axiom."""

    # Test with identical functions
    def f(x):
        return x

    def g(x):
        return x

    distance = sobolev_metric.distance(f, g)
    assert distance == 0

    # Test with different functions
    def f(x):
        return x

    def g(x):
        return x + 1

    distance = sobolev_metric.distance(f, g)
    assert distance != 0


def test_symmetry_axiom(sobolev_metric):
    """Test the symmetry axiom."""

    def f(x):
        return x

    def g(x):
        return x + 1

    distance_fg = sobolev_metric.distance(f, g)
    distance_gf = sobolev_metric.distance(g, f)
    assert distance_fg == distance_gf


def test_triangle_inequality(sobolev_metric):
    """Test the triangle inequality."""

    def f(x):
        return x

    def g(x):
        return x + 1

    def h(x):
        return x + 2

    distance_fg = sobolev_metric.distance(f, g)
    distance_gh = sobolev_metric.distance(g, h)
    distance_fh = sobolev_metric.distance(f, h)

    assert distance_fh <= distance_fg + distance_gh


def test_multiple_orders(sobolev_metric):
    """Test different orders of the Sobolev metric."""
    # Test with order=1
    sobolev_metric = SobolevMetric(order=1)

    def f(x):
        return x

    def g(x):
        return x + 1

    distance = sobolev_metric.distance(f, g)
    assert distance >= 0

    # Test with order=2
    sobolev_metric = SobolevMetric(order=2)
    distance = sobolev_metric.distance(f, g)
    assert distance >= 0


def test_invalid_order():
    """Test that invalid order raises ValueError."""
    with pytest.raises(ValueError):
        SobolevMetric(order=-1)
