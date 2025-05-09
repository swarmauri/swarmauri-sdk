```python
import pytest
import logging
from swarmauri_standard.swarmauri_standard.metrics.SupremumMetric import SupremumMetric

@pytest.mark.unit
class TestSupremumMetric:
    """Unit test class for SupremumMetric class."""

    def test_resource_attribute(self):
        """Test the resource attribute of the SupremumMetric class."""
        assert SupremumMetric.resource == "Metric"

    def test_type_attribute(self):
        """Test the type attribute of the SupremumMetric class."""
        assert SupremumMetric.type == "SupremumMetric"

    def test_initialization(self, caplog):
        """Test the initialization of the SupremumMetric class."""
        with caplog.at_level(logging.DEBUG):
            supremum_metric = SupremumMetric()
            assert "SupremumMetric instance initialized" in caplog.text

    @pytest.mark.parametrize("x,y,expected_distance", [
        ((1, 2, 3), (1, 2, 3), 0.0),
        ((0, 0), (1, 1), 1.0),
        ((-1, 2), (3, -2), 4.0)
    ])
    def test_distance(self, x, y, expected_distance):
        """Test the distance method with various inputs."""
        supremum_metric = SupremumMetric()
        assert supremum_metric.distance(x, y) == expected_distance

    @pytest.mark.parametrize("x,y_list,expected_distances", [
        ((1, 2), [(1, 2), (3, 4)], [0.0, 2.0]),
        ((0, 0, 0), (0, 0, 0), 0.0)
    ])
    def test_distances(self, x, y_list, expected_distances):
        """Test the distances method with single and multiple points."""
        supremum_metric = SupremumMetric()
        if isinstance(y_list, list):
            distances = supremum_metric.distances(x, y_list)
            assert isinstance(distances, list)
        else:
            distances = supremum_metric.distances(x, y_list)
            assert isinstance(distances, float)
        assert distances == expected_distances

    def test_non_negativity(self):
        """Test the non-negativity axiom."""
        supremum_metric = SupremumMetric()
        distance = supremum_metric.distance((1, 2), (3, 4))
        assert distance >= 0.0

    def test_identity(self):
        """Test the identity of indiscernibles axiom."""
        supremum_metric = SupremumMetric()
        assert supremum_metric.check_identity((1, 2), (1, 2))

    def test_symmetry(self):
        """Test the symmetry axiom."""
        supremum_metric = SupremumMetric()
        assert supremum_metric.check_symmetry((1, 2), (3, 4)) == \
               supremum_metric.check_symmetry((3, 4), (1, 2))

    def test_triangle_inequality(self):
        """Test the triangle inequality axiom."""
        supremum_metric = SupremumMetric()
        x = (1, 2)
        y = (3, 4)
        z = (5, 6)
        d_xy = supremum_metric.distance(x, y)
        d_yz = supremum_metric.distance(y, z)
        d_xz = supremum_metric.distance(x, z)
        assert d_xz <= d_xy + d_yz
```

```python
import pytest
import logging
from swarmauri_standard.swarmauri_standard.metrics.SupremumMetric import SupremumMetric

@pytest.mark.unit
class TestSupremumMetric:
    """Unit test class for SupremumMetric class."""

    def test_resource_attribute(self):
        """Test the resource attribute of the SupremumMetric class."""
        assert SupremumMetric.resource == "Metric"

    def test_type_attribute(self):
        """Test the type attribute of the SupremumMetric class."""
        assert SupremumMetric.type == "SupremumMetric"

    def test_initialization(self, caplog):
        """Test the initialization of the SupremumMetric class."""
        with caplog.at_level(logging.DEBUG):
            supremum_metric = SupremumMetric()
            assert "SupremumMetric instance initialized" in caplog.text

    @pytest.mark.parametrize("x,y,expected_distance", [
        ((1, 2, 3), (1, 2, 3), 0.0),
        ((0, 0), (1, 1), 1.0),
        ((-1, 2), (3, -2), 4.0)
    ])
    def test_distance(self, x, y, expected_distance):
        """Test the distance method with various inputs."""
        supremum_metric = SupremumMetric()
        assert supremum_metric.distance(x, y) == expected_distance

    @pytest.mark.parametrize("x,y_list,expected_distances", [
        ((1, 2), [(1, 2), (3, 4)], [0.0, 2.0]),
        ((0, 0, 0), (0, 0, 0), 0.0)
    ])
    def test_distances(self, x, y_list, expected_distances):
        """Test the distances method with single and multiple points."""
        supremum_metric = SupremumMetric()
        if isinstance(y_list, list):
            distances = supremum_metric.distances(x, y_list)
            assert isinstance(distances, list)
        else:
            distances = supremum_metric.distances(x, y_list)
            assert isinstance(distances, float)
        assert distances == expected_distances

    def test_non_negativity(self):
        """Test the non-negativity axiom."""
        supremum_metric = SupremumMetric()
        distance = supremum_metric.distance((1, 2), (3, 4))
        assert distance >= 0.0

    def test_identity(self):
        """Test the identity of indiscernibles axiom."""
        supremum_metric = SupremumMetric()
        assert supremum_metric.check_identity((1, 2), (1, 2))

    def test_symmetry(self):
        """Test the symmetry axiom."""
        supremum_metric = SupremumMetric()
        assert supremum_metric.check_symmetry((1, 2), (3, 4)) == \
               supremum_metric.check_symmetry((3, 4), (1, 2))

    def test_triangle_inequality(self):
        """Test the triangle inequality axiom."""
        supremum_metric = SupremumMetric()
        x = (1, 2)
        y = (3, 4)
        z = (5, 6)
        d_xy = supremum_metric.distance(x, y)
        d_yz = supremum_metric.distance(y, z)
        d_xz = supremum_metric.distance(x, z)
        assert d_xz <= d_xy + d_yz
```