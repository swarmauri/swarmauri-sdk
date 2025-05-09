import pytest
from swarmauri_standard.swarmauri_standard.metrics.EuclideanMetric import (
    EuclideanMetric,
)
import logging


@pytest.mark.unit
class TestEuclideanMetric:
    """Unit tests for the EuclideanMetric class."""

    @pytest.fixture
    def euclidean_metric(self):
        """Fixture to provide a EuclideanMetric instance."""
        return EuclideanMetric()

    @pytest.mark.unit
    def test_resource(self):
        """Test the resource property."""
        assert EuclideanMetric.resource == "metric"

    @pytest.mark.unit
    def test_type(self):
        """Test the type property."""
        assert EuclideanMetric.type == "EuclideanMetric"

    @pytest.mark.unit
    def test_init(euclidean_metric):
        """Test the initialization of EuclideanMetric."""
        assert isinstance(euclidean_metric, EuclideanMetric)
        assert hasattr(euclidean_metric, "norm")

    @pytest.mark.unit
    def test_distance(euclidean_metric):
        """Test the distance method with valid vectors."""
        x = [1, 2, 3]
        y = [4, 5, 6]
        result = euclidean_metric.distance(x, y)
        assert isinstance(result, float)
        assert result > 0

    @pytest.mark.unit
    def test_distance_same_vectors(euclidean_metric):
        """Test the distance method with identical vectors."""
        x = [1, 2, 3]
        y = [1, 2, 3]
        result = euclidean_metric.distance(x, y)
        assert result == 0.0

    @pytest.mark.unit
    def test_distance_different_shapes(euclidean_metric):
        """Test the distance method with vectors of different shapes."""
        x = [1, 2]
        y = [3, 4, 5]
        with pytest.raises(ValueError):
            euclidean_metric.distance(x, y)

    @pytest.mark.unit
    def test_distances_single_vector(euclidean_metric):
        """Test the distances method with a single vector."""
        x = [1, 2, 3]
        y = [4, 5, 6]
        result = euclidean_metric.distances(x, y)
        assert isinstance(result, float)

    @pytest.mark.unit
    def test_distances_multiple_vectors(euclidean_metric):
        """Test the distances method with multiple vectors."""
        x = [1, 2, 3]
        y_list = [[4, 5, 6], [7, 8, 9]]
        result = euclidean_metric.distances(x, y_list)
        assert isinstance(result, list)
        assert len(result) == 2

    @pytest.mark.unit
    def test_check_non_negativity(euclidean_metric):
        """Test the non-negativity axiom."""
        x = [1, 2, 3]
        y = [4, 5, 6]
        result = euclidean_metric.check_non_negativity(x, y)
        assert result is True

    @pytest.mark.unit
    def test_check_identity(euclidean_metric):
        """Test the identity axiom."""
        x = [1, 2, 3]
        y = [1, 2, 3]
        result = euclidean_metric.check_identity(x, y)
        assert result is True

    @pytest.mark.unit
    def test_check_symmetry(euclidean_metric):
        """Test the symmetry axiom."""
        x = [1, 2, 3]
        y = [4, 5, 6]
        result = euclidean_metric.check_symmetry(x, y)
        assert result is True

    @pytest.mark.unit
    def test_check_triangle_inequality(euclidean_metric):
        """Test the triangle inequality axiom."""
        x = [1, 2, 3]
        y = [4, 5, 6]
        z = [7, 8, 9]
        result = euclidean_metric.check_triangle_inequality(x, y, z)
        assert result is True
