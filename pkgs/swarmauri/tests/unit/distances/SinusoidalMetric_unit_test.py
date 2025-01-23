import pytest
from swarmauri.distances.concrete.SinusoidalMetric import SinusoidalMetric
from swarmauri.vectors.concrete.Vector import Vector


@pytest.mark.unit
def test_ubc_resource():
    assert SinusoidalMetric().resource == 'Distance'


@pytest.mark.unit
def test_ubc_type():
    assert SinusoidalMetric().type == 'SinusoidalMetric'


@pytest.mark.unit
def test_serialization():
    metric = SinusoidalMetric()
    assert metric.id == SinusoidalMetric.model_validate_json(metric.model_dump_json()).id


@pytest.mark.unit
def test_distance():
    metric = SinusoidalMetric()
    assert metric.distance(Vector(value=[1, 2, 3]), Vector(value=[1, 2, 3])) == 0.0


@pytest.mark.unit
def test_distance_not_equal_vectors():
    metric = SinusoidalMetric()
    distance = metric.distance(Vector(value=[1, 2, 3]), Vector(value=[4, 5, 6]))
    assert distance > 0.0


@pytest.mark.unit
def test_distance_invalid_input():
    metric = SinusoidalMetric()
    with pytest.raises(ValueError):
        metric.distance(Vector(value=[1, 2]), Vector(value=[1, 2, 3]))


@pytest.mark.unit
def test_similarity():
    metric = SinusoidalMetric()
    assert metric.similarity(Vector(value=[1, 2, 3]), Vector(value=[1, 2, 3])) == 1.0


@pytest.mark.unit
def test_similarity_not_equal_vectors():
    metric = SinusoidalMetric()
    similarity = metric.similarity(Vector(value=[1, 2, 3]), Vector(value=[4, 5, 6]))
    assert similarity < 1.0


@pytest.mark.unit
def test_similarity_invalid_input():
    metric = SinusoidalMetric()
    with pytest.raises(ValueError):
        metric.similarity(Vector(value=[1, 2]), Vector(value=[1, 2, 3]))


@pytest.mark.unit
def test_distances():
    metric = SinusoidalMetric()
    a = Vector(value=[1, 2, 3])
    b = [Vector(value=[4, 5, 6]), Vector(value=[7, 8, 9])]
    distances = metric.distances(a, b)
    assert len(distances) == 2
    assert all(d > 0 for d in distances)


@pytest.mark.unit
def test_similarities():
    metric = SinusoidalMetric()
    a = Vector(value=[1, 2, 3])
    b = [Vector(value=[4, 5, 6]), Vector(value=[7, 8, 9])]
    similarities = metric.similarities(a, b)
    assert len(similarities) == 2
    assert all(0 <= s <= 1 for s in similarities)


@pytest.mark.unit
def test_triangle_inequality():
    metric = SinusoidalMetric()
    a = Vector(value=[1, 2, 3])
    b = Vector(value=[2, 3, 4])
    c = Vector(value=[4, 5, 6])
    assert metric.triangle_inequality(a, b, c) is True
