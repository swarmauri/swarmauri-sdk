import numpy as np
import pytest


@pytest.mark.i9n
def test_import_cpp_extensions() -> None:
    from IndexBuilder import hash_index, tree_index

    assert callable(hash_index.LSHIndex)
    assert callable(tree_index.nearestNeighbor)


@pytest.mark.i9n
def test_tree_index_returns_nearest_point() -> None:
    from IndexBuilder.tree_index import nearestNeighbor

    assert nearestNeighbor([[1.0, 2.0], [4.0, 5.0]], [3.9, 5.0]) == [
        4.0,
        5.0,
    ]


@pytest.mark.i9n
def test_hash_index_finds_inserted_point() -> None:
    from IndexBuilder.hash_index import LSHIndex

    index = LSHIndex(2, 2)
    point = np.array([1.0, 2.0], dtype=np.float32)
    index.insert(point)

    assert len(index.query(point)) > 0
