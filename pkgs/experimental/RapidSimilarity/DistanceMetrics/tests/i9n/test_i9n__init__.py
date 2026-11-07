import numpy as np
import pytest


@pytest.mark.i9n
def test_import_cpp_extensions() -> None:
    from DistanceMetrics import cosine, euclidean

    assert callable(cosine.cosine_similarity)
    assert callable(euclidean.euclidean_distance)


@pytest.mark.i9n
def test_cosine_similarity_from_python() -> None:
    from DistanceMetrics.cosine import cosine_similarity

    assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) == pytest.approx(1.0)


@pytest.mark.i9n
def test_euclidean_distance_from_numpy() -> None:
    from DistanceMetrics import euclidean_distance

    first = np.array([0.0, 0.0])
    second = np.array([3.0, 4.0])
    assert euclidean_distance(first, second) == pytest.approx(5.0)
