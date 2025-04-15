import pytest
import numpy as np
from QueryEngine import exact_query

@pytest.mark.unit
def test_exact_nearest_neighbors_single():
    """Test exact nearest neighbors with a single query point."""
    dataset = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float32)
    query = 3.0
    k = 2
    expected_neighbors = [2, 1]  # Indices of 3.0's nearest neighbors
    neighbors = exact_query.exact_nearest_neighbors(dataset, query, k)
    assert list(neighbors) == expected_neighbors

@pytest.mark.unit
def test_exact_nearest_neighbors_multiple():
    """Test exact nearest neighbors with multiple query points."""
    dataset = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float32)
    queries = [(3.0, 2), (5.0, 1), (1.0, 3)]
    expected_results = [
        [2, 1],  # Neighbors for query 3.0
        [4],     # Neighbors for query 5.0
        [0, 1, 2]  # Neighbors for query 1.0
    ]

    for (query, k), expected_neighbors in zip(queries, expected_results):
        neighbors = exact_query.exact_nearest_neighbors(dataset, query, k)
        assert list(neighbors) == expected_neighbors

@pytest.mark.unit
def test_exact_nearest_neighbors_empty_dataset():
    """Test exact nearest neighbors with an empty dataset."""
    dataset = np.array([], dtype=np.float32)
    query = 3.0
    k = 2
    with pytest.raises(IndexError):
        exact_query.exact_nearest_neighbors(dataset, query, k)

@pytest.mark.unit
def test_exact_nearest_neighbors_large_k():
    """Test exact nearest neighbors with k larger than dataset size."""
    dataset = np.array([1.0, 2.0, 3.0], dtype=np.float32)
    query = 2.0
    k = 5  # k is larger than the dataset
    expected_neighbors = [1, 0, 2]  # All indices
    neighbors = exact_query.exact_nearest_neighbors(dataset, query, k)
    assert list(neighbors) == expected_neighbors

@pytest.mark.unit
@pytest.mark.parametrize("dataset,query,k,expected_neighbors", [
    (np.array([1.0, 2.0, 3.0], dtype=np.float32), 1.5, 1, [0]),
    (np.array([5.0, 1.0, 3.0, 4.0, 2.0], dtype=np.float32), 3.5, 2, [2, 3]),
    (np.array([10.0, 20.0, 30.0], dtype=np.float32), 15.0, 2, [1, 0])
])
def test_exact_nearest_neighbors_parametrized(dataset, query, k, expected_neighbors):
    """Test exact nearest neighbors with parameterized datasets."""
    neighbors = exact_query.exact_nearest_neighbors(dataset, query, k)
    assert list(neighbors) == expected_neighbors