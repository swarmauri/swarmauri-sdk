import pytest
from swarmauri.metrics.concrete.CanberraMetric import CanberraMetric
from swarmauri_core.vectors.concrete.Vector import Vector
import numpy as np


@pytest.mark.unit
def test_metric_resource():
    """
    Tests that the metric has the correct resource.
    """
    metric = CanberraMetric()
    assert metric.resource == "Metric"


@pytest.mark.unit
def test_metric_type():
    """
    Tests that the metric has the correct type.
    """
    metric = CanberraMetric()
    assert metric.type == "CanberraMetric"


@pytest.mark.unit
def test_serialization():
    """
    Tests that the metric can be serialized and deserialized correctly.
    """
    metric = CanberraMetric()
    assert metric.id == CanberraMetric.model_validate_json(metric.model_dump_json()).id


@pytest.mark.unit
def test_distance_same_vectors():
    """
    Tests that the distance between identical vectors is zero.
    """
    metric = CanberraMetric()
    vector_a = Vector(value=[1, 2, 3])
    assert metric.distance(vector_a, vector_a) == 0.0


@pytest.mark.unit
def test_distance_different_vectors():
    """
    Tests that the distance between two distinct vectors is greater than zero.
    """
    metric = CanberraMetric()
    vector_a = Vector(value=[1, 2, 3])
    vector_b = Vector(value=[4, 5, 6])
    assert metric.distance(vector_a, vector_b) > 0.0


@pytest.mark.unit
def test_distance_handles_zero_elements():
    """
    Tests that the distance calculation handles zero elements gracefully.
    """
    metric = CanberraMetric()
    vector_a = Vector(value=[0, 2, 3])
    vector_b = Vector(value=[0, 5, 6])
    assert metric.distance(vector_a, vector_b) > 0.0


@pytest.mark.unit
def test_distances():
    """
    Tests the distances between a vector and multiple other vectors.
    """
    metric = CanberraMetric()
    vector_a = Vector(value=[1, 2, 3])
    vectors_b = [Vector(value=[4, 5, 6]), Vector(value=[7, 8, 9])]
    distances = metric.distances(vector_a, vectors_b)
    assert len(distances) == 2
    assert all(d > 0 for d in distances)


@pytest.mark.unit
def test_similarity_identical_vectors():
    """
    Tests that similarity is 1 for identical vectors.
    """
    metric = CanberraMetric()
    vector_a = Vector(value=[1, 2, 3])
    assert metric.similarity(vector_a, vector_a) == 1.0


@pytest.mark.unit
def test_similarity_different_vectors():
    """
    Tests that similarity is less than 1 for distinct vectors.
    """
    metric = CanberraMetric()
    vector_a = Vector(value=[1, 2, 3])
    vector_b = Vector(value=[4, 5, 6])
    similarity = metric.similarity(vector_a, vector_b)
    assert 0 < similarity < 1.0


@pytest.mark.unit
def test_similarities():
    """
    Tests the similarities between a vector and multiple other vectors.
    """
    metric = CanberraMetric()
    vector_a = Vector(value=[1, 2, 3])
    vectors_b = [Vector(value=[4, 5, 6]), Vector(value=[7, 8, 9])]
    similarities = metric.similarities(vector_a, vectors_b)
    assert len(similarities) == 2
    assert all(0 <= s <= 1 for s in similarities)


@pytest.mark.unit
def test_triangle_inequality():
    """
    Tests that the metric satisfies the triangle inequality.
    """
    metric = CanberraMetric()
    vector_a = Vector(value=[1, 2, 3])
    vector_b = Vector(value=[4, 5, 6])
    vector_c = Vector(value=[7, 8, 9])
    assert metric.check_triangle_inequality(vector_a, vector_b, vector_c) is True


@pytest.mark.unit
def test_non_negativity():
    """
    Tests that the metric satisfies the non-negativity property.
    """
    metric = CanberraMetric()
    vector_a = Vector(value=[1, 2, 3])
    vector_b = Vector(value=[4, 5, 6])
    assert metric.check_non_negativity(vector_a, vector_b) is True


@pytest.mark.unit
def test_identity_of_indiscernibles():
    """
    Tests that the metric satisfies the identity of indiscernibles property.
    """
    metric = CanberraMetric()
    vector_a = Vector(value=[1, 2, 3])
    vector_b = Vector(value=[1, 2, 3])
    vector_c = Vector(value=[4, 5, 6])
    assert metric.check_identity_of_indiscernibles(vector_a, vector_b) is True
    assert metric.check_identity_of_indiscernibles(vector_a, vector_c) is True


@pytest.mark.unit
def test_symmetry():
    """
    Tests that the metric satisfies the symmetry property.
    """
    metric = CanberraMetric()
    vector_a = Vector(value=[1, 2, 3])
    vector_b = Vector(value=[4, 5, 6])
    assert metric.check_symmetry(vector_a, vector_b) is True


@pytest.mark.unit
def test_positivity():
    """
    Tests that the metric satisfies the positivity property.
    """
    metric = CanberraMetric()
    vector_a = Vector(value=[1, 2, 3])
    vector_b = Vector(value=[4, 5, 6])
    assert metric.check_positivity(vector_a, vector_b) is True


@pytest.mark.unit
def test_expected_distance():
    """
    Tests the distance calculation against a known expected value.
    """
    metric = CanberraMetric()
    vector_a = Vector(value=[1, 2, 3])
    vector_b = Vector(value=[4, 5, 6])
    expected_distance = (3 / 5) + (3 / 7) + (3 / 9)
    assert pytest.approx(metric.distance(vector_a, vector_b), 0.001) == expected_distance


@pytest.mark.unit
def test_expected_similarity():
    """
    Tests the similarity calculation against a known expected value.
    """
    metric = CanberraMetric()
    vector_a = Vector(value=[1, 2, 3])
    vector_b = Vector(value=[4, 5, 6])
    distance = metric.distance(vector_a, vector_b)
    expected_similarity = np.exp(-distance)
    assert pytest.approx(metric.similarity(vector_a, vector_b), 0.001) == expected_similarity
