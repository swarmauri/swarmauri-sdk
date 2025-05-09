import pytest
import numpy as np
from swarmauri_standard.metrics.FrobeniusMetric import FrobeniusMetric


@pytest.mark.unit
class TestFrobeniusMetric:
    """Unit tests for the FrobeniusMetric class."""

    def test_distance(self):
        """Test the distance method with various inputs."""
        # Test with numpy arrays
        x = np.array([[1, 2], [3, 4]])
        y = np.array([[1, 2], [3, 4]])
        assert FrobeniusMetric().distance(x, y) == 0.0

        x = np.array([[1, 2], [3, 4]])
        y = np.array([[1, 2], [3, 5]])
        assert FrobeniusMetric().distance(x, y) == 1.0

        # Test with vectors
        x = np.array([1, 2, 3])
        y = np.array([1, 2, 3])
        assert FrobeniusMetric().distance(x, y) == 0.0

        # Test with different shapes
        x = np.array([[1, 2], [3, 4]])
        y = np.array([[1, 2, 3], [4, 5, 6]])
        with pytest.raises(ValueError):
            FrobeniusMetric().distance(x, y)

    def test_distances(self):
        """Test the distances method with multiple inputs."""
        x_list = [np.array([[1, 2], [3, 4]]), np.array([[5, 6], [7, 8]])]
        y_list = [np.array([[1, 2], [3, 4]]), np.array([[5, 6], [7, 8]])]
        result = FrobeniusMetric().distances(x_list, y_list)
        assert len(result) == 2
        assert all(isinstance(item, float) for sublist in result for item in sublist)

    def test_check_non_negativity(self):
        """Test the non-negativity check."""
        x = np.array([[1, 2], [3, 4]])
        y = np.array([[1, 2], [3, 4]])
        FrobeniusMetric().check_non_negativity(x, y)

    def test_check_identity(self):
        """Test the identity of indiscernibles check."""
        x = np.array([[1, 2], [3, 4]])
        y = np.array([[1, 2], [3, 4]])
        FrobeniusMetric().check_identity(x, y)

        x = np.array([[1, 2], [3, 4]])
        y = np.array([[1, 2], [3, 5]])
        with pytest.raises(ValueError):
            FrobeniusMetric().check_identity(x, y)

    def test_check_symmetry(self):
        """Test the symmetry axiom."""
        x = np.array([[1, 2], [3, 4]])
        y = np.array([[1, 2], [3, 5]])
        FrobeniusMetric().check_symmetry(x, y)

    def test_check_triangle_inequality(self):
        """Test the triangle inequality axiom."""
        x = np.array([[1, 2], [3, 4]])
        y = np.array([[1, 2], [3, 5]])
        z = np.array([[1, 2], [3, 6]])
        FrobeniusMetric().check_triangle_inequality(x, y, z)

    def test_string_representation(self):
        """Test the string representation methods."""
        metric = FrobeniusMetric()
        assert str(metric) == "FrobeniusMetric()"
        assert repr(metric) == "FrobeniusMetric()"
