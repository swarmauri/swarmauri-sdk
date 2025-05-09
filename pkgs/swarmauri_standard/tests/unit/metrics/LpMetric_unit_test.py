import pytest
from swarmauri_standard.metrics.LpMetric import LpMetric
from swarmauri_base.exceptions import MetricViolationError


@pytest.fixture
def lp_metric():
    return LpMetric(p=2.0)


@pytest.fixture(params=[2.0, 1.5, 3.0])
def lp_metric_var_p(request):
    return LpMetric(p=request.param)


@pytest.mark.unit
class TestLpMetric:
    """Unit tests for the LpMetric class."""

    def test_initialization(self, lp_metric_var_p):
        """Test that the LpMetric instance is correctly initialized."""
        assert lp_metric_var_p.p == lp_metric_var_p.norm.p
        with pytest.raises(ValueError):
            LpMetric(p=-1.0)
        with pytest.raises(ValueError):
            LpMetric(p=1.0)
        with pytest.raises(ValueError):
            LpMetric(p=float("inf"))
        with pytest.raises(ValueError):
            LpMetric(p=None)

    def test_logging(self, lp_metric, caplog):
        """Test that appropriate logging occurs during distance calculation."""
        lp_metric.distance([1, 2], [3, 4])
        assert "Calculating L2.0 distance" in caplog.text

    def test_is_valid(self, lp_metric):
        """Test the is_valid method for different input types."""
        assert lp_metric.is_valid(1)
        assert lp_metric.is_valid([1.0, 2.0])
        assert not lp_metric.is_valid(float("nan"))
        assert not lp_metric.is_valid([float("inf"), 2.0])
        assert not lp_metric.is_valid(None)

    def test_resource_and_type(self, lp_metric):
        """Test that resource and type attributes are correctly set."""
        assert LpMetric.resource == "Metric"
        assert lp_metric.type == "LpMetric"

    def test_repr(self, lp_metric):
        """Test the string representation of the LpMetric instance."""
        assert str(lp_metric) == f"LpMetric(p={lp_metric.p})"

    def test_distance_vector_and_scalar(self, lp_metric):
        """Test distance calculation with both vector and scalar inputs."""
        # Vector vs Vector
        d = lp_metric.distance([1.0, 2.0], [3.0, 4.0])
        assert d >= 0.0

        # Vector vs Scalar
        d = lp_metric.distance([1.0, 2.0], 3.0)
        assert d >= 0.0

        # Scalar vs Vector
        d = lp_metric.distance(3.0, [4.0, 5.0])
        assert d >= 0.0

        # Scalar vs Scalar
        d = lp_metric.distance(3.0, 4.0)
        assert d >= 0.0

    def test_identity_of_indiscernibles(self, lp_metric):
        """Test the identity of indiscernibles axiom."""
        point = [1.0, 2.0]
        d = lp_metric.distance(point, point)
        assert d == 0.0

        with pytest.raises(MetricViolationError):
            lp_metric.distance([1.0, 2.0], [1.0, 3.0])
            lp_metric.check_identity([1.0, 2.0], [1.0, 2.0])

    def test_symmetry(self, lp_metric):
        """Test the symmetry axiom."""
        d_xy = lp_metric.distance([1.0, 2.0], [3.0, 4.0])
        d_yx = lp_metric.distance([3.0, 4.0], [1.0, 2.0])
        assert d_xy == d_yx

    def test_triangle_inequality(self, lp_metric):
        """Test the triangle inequality."""
        x = [0.0, 0.0]
        y = [1.0, 0.0]
        z = [0.0, 1.0]

        d_xy = lp_metric.distance(x, y)
        d_yz = lp_metric.distance(y, z)
        d_xz = lp_metric.distance(x, z)

        assert d_xz <= d_xy + d_yz
