import logging

import numpy as np
import pytest
from swarmauri_base.metrics.MetricBase import MetricBase

from swarmauri_standard.metrics.FrobeniusMetric import FrobeniusMetric

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def frobenius_metric():
    """
    Fixture providing a FrobeniusMetric instance for testing.

    Returns
    -------
    FrobeniusMetric
        An instance of the FrobeniusMetric class
    """
    return FrobeniusMetric()


@pytest.fixture
def sample_matrices():
    """
    Fixture providing sample matrices for testing.

    Returns
    -------
    tuple
        A tuple containing various test matrices
    """
    # Identity matrix
    matrix_a = np.array([[1.0, 0.0], [0.0, 1.0]])

    # Another matrix
    matrix_b = np.array([[2.0, 1.0], [1.0, 3.0]])

    # Matrix with negative values
    matrix_c = np.array([[-1.0, 2.0], [3.0, -4.0]])

    # Zero matrix
    matrix_zero = np.array([[0.0, 0.0], [0.0, 0.0]])

    return matrix_a, matrix_b, matrix_c, matrix_zero


@pytest.mark.unit
def test_inheritance():
    """Test that FrobeniusMetric inherits from MetricBase."""
    metric = FrobeniusMetric()
    assert isinstance(metric, MetricBase)


@pytest.mark.unit
def test_resource_type():
    """Test that resource type is correctly set."""
    metric = FrobeniusMetric()
    assert metric.resource == "Metric"


@pytest.mark.unit
def test_metric_type():
    """Test that metric type is correctly set."""
    metric = FrobeniusMetric()
    assert metric.type == "FrobeniusMetric"


@pytest.mark.unit
def test_distance_numpy_arrays(frobenius_metric, sample_matrices):
    """Test distance calculation with numpy arrays."""
    matrix_a, matrix_b, _, _ = sample_matrices

    # Calculate expected distance manually
    diff = matrix_a - matrix_b
    expected_distance = np.sqrt(np.sum(diff * diff))

    # Calculate using the metric
    actual_distance = frobenius_metric.distance(matrix_a, matrix_b)

    assert np.isclose(actual_distance, expected_distance)
    # Update this line:
    assert np.isclose(actual_distance, np.sqrt(7))


@pytest.mark.unit
def test_distance_with_lists(frobenius_metric):
    """Test distance calculation with Python lists."""
    matrix_a = [[1.0, 0.0], [0.0, 1.0]]
    matrix_b = [[2.0, 1.0], [1.0, 3.0]]

    distance = frobenius_metric.distance(matrix_a, matrix_b)
    # Update this line:
    assert np.isclose(distance, np.sqrt(7))


@pytest.mark.unit
def test_distance_with_different_shapes(frobenius_metric):
    """Test that distance calculation raises ValueError for matrices with different shapes."""
    matrix_a = np.array([[1.0, 0.0], [0.0, 1.0]])
    matrix_b = np.array([[1.0, 0.0, 2.0], [0.0, 1.0, 3.0]])

    with pytest.raises(ValueError) as excinfo:
        frobenius_metric.distance(matrix_a, matrix_b)

    assert "Matrices must have the same shape" in str(excinfo.value)


@pytest.mark.unit
def test_distance_with_unsupported_type(frobenius_metric):
    """Test that distance calculation raises TypeError for unsupported input types."""
    matrix_a = np.array([[1.0, 0.0], [0.0, 1.0]])
    invalid_input = "not a matrix"

    with pytest.raises(TypeError) as excinfo:
        frobenius_metric.distance(matrix_a, invalid_input)

    assert "Unsupported type for Frobenius metric" in str(excinfo.value)


@pytest.mark.unit
def test_distances_between_collections(frobenius_metric, sample_matrices):
    """Test distances calculation between collections of matrices."""
    matrix_a, matrix_b, matrix_c, _ = sample_matrices

    matrices_x = [matrix_a, matrix_b]
    matrices_y = [matrix_b, matrix_c]

    distances = frobenius_metric.distances(matrices_x, matrices_y)

    # Verify dimensions of result
    assert len(distances) == len(matrices_x)
    assert len(distances[0]) == len(matrices_y)

    # Verify specific distances
    assert np.isclose(distances[0][0], frobenius_metric.distance(matrix_a, matrix_b))
    assert np.isclose(distances[0][1], frobenius_metric.distance(matrix_a, matrix_c))
    assert np.isclose(distances[1][0], frobenius_metric.distance(matrix_b, matrix_b))
    assert np.isclose(distances[1][1], frobenius_metric.distance(matrix_b, matrix_c))


@pytest.mark.unit
def test_distances_invalid_input(frobenius_metric, sample_matrices):
    """Test distances calculation with invalid inputs."""
    matrix_a, _, _, _ = sample_matrices

    with pytest.raises(TypeError) as excinfo:
        frobenius_metric.distances(matrix_a, [matrix_a])

    assert "Both inputs must be collections of matrices" in str(excinfo.value)


@pytest.mark.unit
@pytest.mark.parametrize(
    "matrix_pair",
    [
        (np.array([[1.0, 0.0], [0.0, 1.0]]), np.array([[2.0, 1.0], [1.0, 3.0]])),
        (np.array([[-1.0, 2.0], [3.0, -4.0]]), np.array([[0.0, 0.0], [0.0, 0.0]])),
    ],
)
def test_non_negativity(frobenius_metric, matrix_pair):
    """Test that the Frobenius metric satisfies the non-negativity axiom."""
    x, y = matrix_pair
    assert frobenius_metric.check_non_negativity(x, y) is True


@pytest.mark.unit
def test_identity_of_indiscernibles(frobenius_metric, sample_matrices):
    """Test that the Frobenius metric satisfies the identity of indiscernibles axiom."""
    matrix_a, matrix_b, _, _ = sample_matrices

    # Same matrices should have zero distance
    assert frobenius_metric.check_identity_of_indiscernibles(matrix_a, matrix_a) is True

    # Different matrices should have non-zero distance
    assert frobenius_metric.check_identity_of_indiscernibles(matrix_a, matrix_b) is True


@pytest.mark.unit
def test_symmetry(frobenius_metric, sample_matrices):
    """Test that the Frobenius metric satisfies the symmetry axiom."""
    matrix_a, matrix_b, matrix_c, _ = sample_matrices

    assert frobenius_metric.check_symmetry(matrix_a, matrix_b) is True
    assert frobenius_metric.check_symmetry(matrix_b, matrix_c) is True


@pytest.mark.unit
def test_triangle_inequality(frobenius_metric, sample_matrices):
    """Test that the Frobenius metric satisfies the triangle inequality axiom."""
    matrix_a, matrix_b, matrix_c, _ = sample_matrices

    assert (
        frobenius_metric.check_triangle_inequality(matrix_a, matrix_b, matrix_c) is True
    )


@pytest.mark.unit
def test_serialization(frobenius_metric):
    """Test serialization and deserialization of FrobeniusMetric."""
    # Serialize to JSON
    json_data = frobenius_metric.model_dump_json()

    # Deserialize from JSON
    deserialized = FrobeniusMetric.model_validate_json(json_data)

    # Check that the deserialized object is equivalent
    assert deserialized.type == frobenius_metric.type
    assert deserialized.resource == frobenius_metric.resource


@pytest.mark.unit
def test_distance_with_zero_matrices(frobenius_metric):
    """Test distance calculation with zero matrices."""
    zero_matrix = np.zeros((2, 2))

    # Distance between identical zero matrices should be 0
    assert np.isclose(frobenius_metric.distance(zero_matrix, zero_matrix), 0.0)

    # Distance between zero matrix and non-zero matrix
    non_zero_matrix = np.array([[1.0, 2.0], [3.0, 4.0]])
    expected_distance = np.sqrt(30.0)  # sqrt(1^2 + 2^2 + 3^2 + 4^2)
    assert np.isclose(
        frobenius_metric.distance(zero_matrix, non_zero_matrix), expected_distance
    )
