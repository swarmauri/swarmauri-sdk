import pytest
import logging
from swarmauri_standard.metrics import EuclideanMetric


@pytest.fixture
def euclidean_metric():
    """Fixture to create a new EuclideanMetric instance for each test."""
    return EuclideanMetric()


@pytest.mark.unit
def test_euclidean_metric_type(euclidean_metric):
    """Test that the type property returns the correct string."""
    assert euclidean_metric.type == "EuclideanMetric"


@pytest.mark.unit
def test_distance_valid_vectors(euclidean_metric):
    """Test distance calculation with valid vectors."""
    x = [1.0, 2.0, 3.0]
    y = [4.0, 5.0, 6.0]
    expected_distance = math.sqrt((3**2) + (3**2) + (3**2))
    assert euclidean_metric.distance(x, y) == expected_distance


@pytest.mark.unit
def test_distance_zero_vectors(euclidean_metric):
    """Test distance calculation with zero vectors."""
    x = [0.0, 0.0, 0.0]
    y = [0.0, 0.0, 0.0]
    assert euclidean_metric.distance(x, y) == 0.0


@pytest.mark.unit
def test_distance_negative_values(euclidean_metric):
    """Test distance calculation with negative values."""
    x = [-1.0, -2.0, -3.0]
    y = [-4.0, -5.0, -6.0]
    expected_distance = math.sqrt((3**2) + (3**2) + (3**2))
    assert euclidean_metric.distance(x, y) == expected_distance


@pytest.mark.unit
def test_distance_different_dimensions(euclidean_metric):
    """Test that distance raises ValueError for vectors of different dimensions."""
    x = [1.0, 2.0]
    y = [3.0, 4.0, 5.0]
    with pytest.raises(ValueError):
        euclidean_metric.distance(x, y)


@pytest.mark.unit
def test_distances_multiple_vectors(euclidean_metric):
    """Test pairwise distance calculation with multiple vectors."""
    xs = [[1.0, 2.0], [3.0, 4.0]]
    ys = [[5.0, 6.0], [7.0, 8.0]]

    expected_distances = [
        [math.sqrt(4**2 + 4**2), math.sqrt(4**2 + 4**2)],
        [math.sqrt(4**2 + 4**2), math.sqrt(4**2 + 4**2)],
    ]

    distances = euclidean_metric.distances(xs, ys)
    assert len(distances) == 2
    assert len(distances[0]) == 2
    assert all(
        abs(d - expected) < 1e-9
        for row in distances
        for d, expected in zip(row, expected_distances)
    )


@pytest.mark.unit
def test_distances_different_dimensions(euclidean_metric):
    """Test that distances raises ValueError for vectors of different dimensions."""
    xs = [[1.0, 2.0]]
    ys = [[3.0, 4.0, 5.0]]
    with pytest.raises(ValueError):
        euclidean_metric.distances(xs, ys)


@pytest.mark.unit
def test_check_non_negativity(euclidean_metric):
    """Test non-negativity axiom check."""
    x = [1.0, 2.0]
    y = [3.0, 4.0]
    euclidean_metric.check_non_negativity(x, y)


@pytest.mark.unit
def test_check_non_negativity_negative_distance(euclidean_metric):
    """Test that check_non_negativity raises ValueError for negative distance."""
    x = [1.0, 2.0]
    y = [3.0, 4.0]

    # Mock a negative distance for testing purposes
    real_distance = euclidean_metric.distance

    def mock_distance(*args, **kwargs):
        return -1.0

    euclidean_metric.distance = mock_distance

    with pytest.raises(ValueError):
        euclidean_metric.check_non_negativity(x, y)

    euclidean_metric.distance = real_distance


@pytest.mark.unit
def test_check_identity(euclidean_metric):
    """Test identity of indiscernibles axiom check."""
    x = [1.0, 2.0]
    y = [1.0, 2.0]
    euclidean_metric.check_identity(x, y)


@pytest.mark.unit
def test_check_identity_different_vectors(euclidean_metric):
    """Test that check_identity raises ValueError for different vectors with zero distance."""
    x = [1.0, 2.0]
    y = [1.0, 2.0]

    # Make x and y different but with same values
    x[0] = 2.0
    y[0] = 1.0

    with pytest.raises(ValueError):
        euclidean_metric.check_identity(x, y)


@pytest.mark.unit
def test_check_symmetry(euclidean_metric):
    """Test symmetry axiom check."""
    x = [1.0, 2.0]
    y = [3.0, 4.0]
    euclidean_metric.check_symmetry(x, y)


@pytest.mark.unit
def test_check_symmetry_asymmetric_distance(euclidean_metric):
    """Test that check_symmetry raises ValueError for asymmetric distances."""
    x = [1.0, 2.0]
    y = [3.0, 4.0]

    # Mock asymmetric distances
    real_distance = euclidean_metric.distance

    def mock_distance(*args, **kwargs):
        if args[0] == x:
            return 1.0
        else:
            return 2.0

    euclidean_metric.distance = mock_distance

    with pytest.raises(ValueError):
        euclidean_metric.check_symmetry(x, y)

    euclidean_metric.distance = real_distance


@pytest.mark.unit
def test_check_triangle_inequality(euclidean_metric):
    """Test triangle inequality axiom check."""
    x = [1.0, 2.0]
    y = [3.0, 4.0]
    z = [5.0, 6.0]
    euclidean_metric.check_triangle_inequality(x, y, z)


@pytest.mark.unit
def test_check_triangle_inequality_violation(euclidean_metric):
    """Test that check_triangle_inequality raises ValueError for invalid triangle."""
    x = [1.0, 2.0]
    y = [3.0, 4.0]
    z = [5.0, 6.0]

    # Mock distances to violate triangle inequality
    real_distance = euclidean_metric.distance

    def mock_distance(x, y):
        if x == x and y == z:
            return 20.0
        else:
            return 1.0

    euclidean_metric.distance = mock_distance

    with pytest.raises(ValueError):
        euclidean_metric.check_triangle_inequality(x, y, z)

    euclidean_metric.distance = real_distance


@pytest.mark.unit
def test_euclidean_metric_registration_type():
    """Test the registration type of EuclideanMetric."""
    assert EuclideanMetric.type == "EuclideanMetric"


@pytest.mark.unit
def test_euclidean_metric_serialization(euclidean_metric):
    """Test the serialization and deserialization of EuclideanMetric."""
    model_json = euclidean_metric.model_dump_json()
    assert euclidean_metric.model_validate_json(model_json) == euclidean_metric.id
