import pytest
import numpy as np
from approx_query import approx_query

@pytest.mark.unit
def test_approx_query_basic():
    """Test the basic functionality of the approximate query engine."""
    dataset = [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]
    query_point = [2.0, 3.0]
    num_neighbors = 2
    accuracy = 0.1

    result = approx_query(dataset, query_point, num_neighbors, accuracy)

    assert len(result) == num_neighbors
    assert all(isinstance(i, int) for i in result)

@pytest.mark.unit
def test_approx_query_edge_cases():
    """Test edge cases for the approximate query engine."""
    dataset = [[1.0, 2.0]]
    query_point = [1.0, 2.0]
    num_neighbors = 1
    accuracy = 0.1

    result = approx_query(dataset, query_point, num_neighbors, accuracy)

    assert result == [0]  # The only point should be returned

@pytest.mark.unit
@pytest.mark.parametrize("dataset, query_point, expected_indices", [
    ([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]], [2.0, 3.0], [0]),
    ([[1.0, 1.0], [1.0, 2.0], [1.0, 3.0]], [1.0, 1.5], [1, 0]),
])
def test_approx_query_parametrized(dataset, query_point, expected_indices):
    """Test approximate query engine with parametrized inputs."""
    num_neighbors = 2
    accuracy = 0.1

    result = approx_query(dataset, query_point, num_neighbors, accuracy)

    assert all(i in expected_indices for i in result)  # Check if the result is within expected indices

@pytest.mark.unit
def test_approx_query_invalid_data():
    """Test the approximate query engine with invalid input data."""
    dataset = "invalid_data"
    query_point = [2.0, 3.0]
    num_neighbors = 2
    accuracy = 0.1

    with pytest.raises(TypeError):
        approx_query(dataset, query_point, num_neighbors, accuracy)

    dataset = [[1.0, 2.0], [3.0, 4.0]]
    query_point = "invalid_query"
    
    with pytest.raises(TypeError):
        approx_query(dataset, query_point, num_neighbors, accuracy)

@pytest.mark.unit
def test_approx_query_large_dataset():
    """Test the performance of the approximate query engine with a large dataset."""
    dataset = np.random.rand(1000, 2).tolist()  # Large dataset of 1000 points
    query_point = [0.5, 0.5]
    num_neighbors = 5
    accuracy = 0.1

    result = approx_query(dataset, query_point, num_neighbors, accuracy)

    assert len(result) == num_neighbors
    assert all(isinstance(i, int) for i in result)