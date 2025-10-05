import pytest

from swarmauri_metric_hamming import HammingMetric


def test_distance_zero_for_identical_sequences():
    metric = HammingMetric()
    assert metric.distance([0, 1, 1, 0], [0, 1, 1, 0]) == 0.0


def test_distance_counts_differences():
    metric = HammingMetric()
    assert metric.distance([1, 0, 1, 0], [0, 1, 1, 0]) == 2.0


def test_normalized_distance():
    metric = HammingMetric()
    assert metric.normalized_distance("abcd", "abcf") == pytest.approx(0.25)


def test_weight_counts_non_zero_symbols():
    metric = HammingMetric()
    assert metric.weight([0, 1, 0, 0, 1, 1, 0]) == 3.0


def test_distances_pairwise_matrix():
    metric = HammingMetric()
    x = [[0, 0, 0], [1, 1, 1]]
    y = [[0, 0, 0], [1, 0, 1]]
    assert metric.distances(x, y) == [[0.0, 2.0], [3.0, 1.0]]


def test_invalid_lengths_raise_value_error():
    metric = HammingMetric()
    with pytest.raises(ValueError):
        metric.distance([0, 1, 0], [0, 1])


@pytest.mark.parametrize("data", [42, "abc", None])
def test_invalid_inputs_raise_type_error(data):
    metric = HammingMetric()
    with pytest.raises(TypeError):
        metric.distance(data, [0, 1, 0])
