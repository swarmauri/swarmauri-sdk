import pytest
import numpy as np
from swarmauri_standard.swarmauri_standard.metrics.FrobeniusMetric import (
    FrobeniusMetric,
)
import logging


@pytest.mark.unit
class TestFrobeniusMetric:
    """Unit test class for FrobeniusMetric class."""

    def test_distance_numpy_arrays(self):
        """Test distance computation with numpy arrays."""
        # Arrange
        x = np.array([[1, 2], [3, 4]])
        y = np.array([[1, 2], [3, 4]])

        # Act
        distance = FrobeniusMetric().distance(x, y)

        # Assert
        assert distance == 0.0
        assert isinstance(distance, float)

    def test_distance_list_input(self):
        """Test distance computation with list inputs."""
        # Arrange
        x = [[1, 2], [3, 4]]
        y = [[1, 2], [3, 4]]

        # Act
        distance = FrobeniusMetric().distance(x, y)

        # Assert
        assert distance == 0.0
        assert isinstance(distance, float)

    def test_distance_tuple_input(self):
        """Test distance computation with tuple inputs."""
        # Arrange
        x = ((1, 2), (3, 4))
        y = ((1, 2), (3, 4))

        # Act
        distance = FrobeniusMetric().distance(x, y)

        # Assert
        assert distance == 0.0
        assert isinstance(distance, float)

    def test_distances_single_input(self):
        """Test distances method with single input."""
        # Arrange
        x = np.array([[1, 2], [3, 4]])
        y = np.array([[1, 2], [3, 4]])

        # Act
        distance = FrobeniusMetric().distances(x, y)

        # Assert
        assert distance == 0.0
        assert isinstance(distance, float)

    def test_distances_multiple_inputs(self):
        """Test distances method with multiple inputs."""
        # Arrange
        x = np.array([[1, 2], [3, 4]])
        y_list = [np.array([[1, 2], [3, 4]]), np.array([[2, 3], [4, 5]])]

        # Act
        distances = FrobeniusMetric().distances(x, y_list)

        # Assert
        assert len(distances) == 2
        assert isinstance(distances, list)
        assert all(isinstance(d, float) for d in distances)

    def test_check_non_negativity(self):
        """Test non-negativity property."""
        # Arrange
        x = np.array([[1, 2], [3, 4]])
        y = np.array([[1, 2], [3, 4]])

        # Act
        result = FrobeniusMetric().check_non_negativity(x, y)

        # Assert
        assert result is True

    def test_check_identity(self):
        """Test identity property."""
        # Arrange
        x = np.array([[1, 2], [3, 4]])
        y = np.array([[1, 2], [3, 4]])

        # Act
        result = FrobeniusMetric().check_identity(x, y)

        # Assert
        assert result is True

    def test_check_symmetry(self):
        """Test symmetry property."""
        # Arrange
        x = np.array([[1, 2], [3, 4]])
        y = np.array([[2, 3], [4, 5]])

        # Act
        result = FrobeniusMetric().check_symmetry(x, y)

        # Assert
        assert result is True

    def test_check_triangle_inequality(self):
        """Test triangle inequality property."""
        # Arrange
        x = np.array([[1, 2], [3, 4]])
        y = np.array([[2, 3], [4, 5]])
        z = np.array([[3, 4], [5, 6]])

        # Act
        result = FrobeniusMetric().check_triangle_inequality(x, y, z)

        # Assert
        assert result is True


@pytest.fixture
def random_matrices():
    """Fixture to generate random matrix pairs."""
    np.random.seed(42)
    x = np.random.rand(3, 3)
    y = np.random.rand(3, 3)
    return x, y


@pytest.fixture
def zero_matrix():
    """Fixture to generate zero matrices."""
    return np.zeros((3, 3))


@pytest.fixture
def different_matrices():
    """Fixture to generate different matrix pairs."""
    x = np.array([[1, 2], [3, 4]])
    y = np.array([[2, 3], [4, 5]])
    return x, y


# Setup logging
logging.basicConfig(level=logging.DEBUG)
