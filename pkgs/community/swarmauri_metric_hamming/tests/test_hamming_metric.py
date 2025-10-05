import numpy as np
import pytest

from swarmauri_metric_hamming import HammingMetric


def test_distance_between_binary_vectors():
    metric = HammingMetric()
    assert metric.distance([1, 0, 1, 1], [1, 1, 0, 1]) == pytest.approx(2.0)


def test_distance_with_strings_and_numpy_arrays():
    metric = HammingMetric()
    left = "1011001"
    right = np.array([1, 0, 1, 0, 0, 0, 1])
    assert metric.distance(left, right) == pytest.approx(2.0)


def test_distances_supports_collections():
    metric = HammingMetric()
    left = [[0, 0, 0], [1, 1, 1]]
    right = [[0, 0, 1], [1, 0, 1]]
    distances = metric.distances(left, right)
    assert distances == [[1.0, 2.0], [2.0, 1.0]]


def test_metric_axioms_hold_for_valid_inputs():
    metric = HammingMetric()
    x = [0, 1, 0, 1]
    y = [0, 0, 1, 1]
    z = [1, 0, 1, 0]

    assert metric.check_non_negativity(x, y)
    assert metric.check_symmetry(x, y)
    assert metric.check_triangle_inequality(x, y, z)


def test_distance_requires_equal_length_inputs():
    metric = HammingMetric()
    with pytest.raises(ValueError):
        metric.distance([1, 0, 1], [1, 0])
