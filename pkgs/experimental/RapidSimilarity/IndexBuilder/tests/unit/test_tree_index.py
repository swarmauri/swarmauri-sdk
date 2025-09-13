import pytest
from IndexBuilder import tree_index


@pytest.mark.unit
def test_nearest_neighbor():
    """Test the nearest neighbor functionality of the KDTree."""
    points = [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0], [7.0, 8.0]]
    target = [4.0, 5.0]

    nearest = tree_index.nearestNeighbor(points, target)
    expected = [3.0, 4.0]

    assert nearest == expected, f"Expected {expected}, got {nearest}"


@pytest.mark.unit
def test_nearest_neighbor_empty():
    """Test nearest neighbor with an empty point set."""
    points = []
    target = [1.0, 1.0]

    nearest = tree_index.nearestNeighbor(points, target)

    assert nearest == [], "Expected no nearest neighbor for empty points."


@pytest.mark.unit
@pytest.mark.parametrize(
    "points,target,expected",
    [
        ([[1.0, 2.0], [3.0, 4.0]], [2.0, 3.0], [1.0, 2.0]),
        ([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]], [4.1, 4.1], [3.0, 4.0]),
        ([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0], [7.0, 8.0]], [6.5, 7.5], [7.0, 8.0]),
    ],
)
def test_nearest_neighbor_parametrized(points, target, expected):
    """Test nearest neighbor functionality with parameterized inputs."""
    nearest = tree_index.nearestNeighbor(points, target)

    assert nearest == expected, f"Expected {expected}, got {nearest}"
