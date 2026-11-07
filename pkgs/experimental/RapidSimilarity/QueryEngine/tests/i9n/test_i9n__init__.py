import numpy as np
import pytest


@pytest.mark.i9n
def test_import_cpp_extensions() -> None:
    from QueryEngine import approx_query, exact_query

    assert callable(approx_query.approx_query)
    assert callable(exact_query.exact_nearest_neighbors)


@pytest.mark.i9n
def test_query_returns_nearest_index() -> None:
    from QueryEngine.exact_query import exact_nearest_neighbors

    values = np.array([1.0, 4.0, 9.0], dtype=np.float32)
    assert list(exact_nearest_neighbors(values, 4.0, 1)) == [1]
