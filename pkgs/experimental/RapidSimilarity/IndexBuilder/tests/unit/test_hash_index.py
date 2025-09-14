import pytest
import numpy as np
from IndexBuilder.hash_index import LSHIndex


@pytest.mark.unit
def test_lsh_index_insert_and_query():
    """Test the insert and query functionality of the LSHIndex class."""
    num_hashes = 5
    bucket_size = 10
    lsh_index = LSHIndex(num_hashes, bucket_size)

    # Create a sample data point
    data_point = np.array([0.5, 0.7], dtype=np.float32)
    lsh_index.insert(data_point)

    # Query the same data point
    results = lsh_index.query(data_point)

    assert len(results) > 0, "Query should return results after insertion."
    assert all(np.array_equal(result, data_point) for result in results), (
        "Returned results should match the inserted data point."
    )


@pytest.mark.unit
@pytest.mark.parametrize(
    "data_points",
    [
        (np.array([[0.0, 0.0], [1.0, 1.0]], dtype=np.float32)),
        (np.array([[0.5, 0.5], [0.6, 0.6]], dtype=np.float32)),
    ],
)
def test_lsh_index_bulk_insert_and_query(data_points):
    """Test bulk insert and query functionality of LSHIndex."""
    num_hashes = 5
    bucket_size = 10
    lsh_index = LSHIndex(num_hashes, bucket_size)

    for point in data_points:
        lsh_index.insert(point)

    # Query one of the inserted points
    results = lsh_index.query(data_points[0])

    assert len(results) > 0, "Query should return results after bulk insertion."
    assert any(np.array_equal(result, data_points[0]) for result in results), (
        "Returned results should contain the queried data point."
    )


@pytest.mark.unit
def test_invalid_insert():
    """Test that invalid data points raise errors during insertion."""
    num_hashes = 5
    bucket_size = 10
    lsh_index = LSHIndex(num_hashes, bucket_size)

    with pytest.raises(TypeError):
        lsh_index.insert("invalid_data")  # Should raise TypeError

    with pytest.raises(ValueError):
        lsh_index.insert(
            np.array([], dtype=np.float32)
        )  # Should raise ValueError for empty input


@pytest.mark.unit
def test_query_empty_index():
    """Test querying an empty LSHIndex returns no results."""
    num_hashes = 5
    bucket_size = 10
    lsh_index = LSHIndex(num_hashes, bucket_size)

    data_point = np.array([0.5, 0.7], dtype=np.float32)
    results = lsh_index.query(data_point)

    assert len(results) == 0, "Querying an empty index should return no results."
