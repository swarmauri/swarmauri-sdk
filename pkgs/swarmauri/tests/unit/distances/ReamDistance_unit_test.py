import pytest
from swarmauri.distances.concrete.ReamDistance import ReamDistance
from swarmauri.vectors.concrete.Vector import Vector


@pytest.mark.unit
def test_ubc_resource():
    assert ReamDistance().resource == 'Distance'


@pytest.mark.unit
def test_ubc_type():
    assert ReamDistance().type == 'ReamDistance'


@pytest.mark.unit
def test_serialization():
    metric = ReamDistance()
    assert metric.id == ReamDistance.model_validate_json(metric.model_dump_json()).id


@pytest.mark.unit
def test_distance():
    metric = ReamDistance()
    assert metric.distance(Vector(value=[1, 2, 3]), Vector(value=[1, 2, 3])) == 0.0


@pytest.mark.unit
def test_distance_not_equal_vectors():
    metric = ReamDistance()
    distance = metric.distance(Vector(value=[1, 2, 3]), Vector(value=[4, 5, 6]))
    assert distance > 0.0


@pytest.mark.unit
def test_distance_invalid_input():
    metric = ReamDistance()
    with pytest.raises(ValueError):
        metric.distance(Vector(value=[1, 2]), Vector(value=[1, 2, 3]))


@pytest.mark.unit
def test_similarity():
    metric = ReamDistance()
    assert metric.similarity(Vector(value=[1, 2, 3]), Vector(value=[1, 2, 3])) == 1.0


@pytest.mark.unit
def test_similarity_not_equal_vectors():
    metric = ReamDistance()
    similarity = metric.similarity(Vector(value=[1, 2, 3]), Vector(value=[4, 5, 6]))
    assert similarity < 1.0


@pytest.mark.unit
def test_similarity_invalid_input():
    metric = ReamDistance()
    with pytest.raises(ValueError):
        metric.similarity(Vector(value=[1, 2]), Vector(value=[1, 2, 3]))


@pytest.mark.unit
def test_distances():
    metric = ReamDistance()
    a = Vector(value=[1, 2, 3])
    b = [Vector(value=[4, 5, 6]), Vector(value=[7, 8, 9])]
    distances = metric.distances(a, b)
    assert len(distances) == 2
    assert all(d > 0 for d in distances)


@pytest.mark.unit
def test_similarities():
    metric = ReamDistance()
    a = Vector(value=[1, 2, 3])
    b = [Vector(value=[4, 5, 6]), Vector(value=[7, 8, 9])]
    similarities = metric.similarities(a, b)
    assert len(similarities) == 2
    assert all(0 <= s <= 1 for s in similarities)


@pytest.mark.unit
def test_expected_distance():
    metric = ReamDistance()
    distance = metric.distance(Vector(value=[1, 1, 1]), Vector(value=[2, 2, 2]))
    expected_distance = np.sqrt(3 * (np.exp(1) - 1) ** 2)
    assert pytest.approx(distance, 0.001) == expected_distance


@pytest.mark.unit
def test_expected_similarity():
    metric = ReamDistance()
    distance = metric.distance(Vector(value=[1, 1, 1]), Vector(value=[2, 2, 2]))
    similarity = metric.similarity(Vector(value=[1, 1, 1]), Vector(value=[2, 2, 2]))
    expected_similarity = np.exp(-distance)
    assert pytest.approx(similarity, 0.001) == expected_similarity


@pytest.mark.unit
def test_inequality():
    metric = ReamDistance()
    a = Vector(value=[1, 2, 3])
    b = Vector(value=[2, 3, 4])
    c = Vector(value=[4, 5, 6])
    assert metric.triangle_inequality(a, b, c) is True
