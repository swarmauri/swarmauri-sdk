import pytest
from swarmauri.distances.concrete.JensenShannonDistance import JensenShannonDistance
from swarmauri.vectors.concrete.Vector import Vector

@pytest.mark.unit
def test_ubc_resource():
    assert JensenShannonDistance().resource == 'Distance'

@pytest.mark.unit
def test_ubc_type():
    assert JensenShannonDistance().type == 'JensenShannonDistance'

@pytest.mark.unit
def test_serialization():
    distance = JensenShannonDistance()
    assert distance.id == JensenShannonDistance.model_validate_json(distance.model_dump_json()).id

@pytest.mark.unit
def test_distance():
    assert JensenShannonDistance().distance(
        Vector(value=[0.5, 0.5]),
        Vector(value=[0.5, 0.5])
    ) == pytest.approx(0.0, rel=1e-5)

@pytest.mark.unit
def test_distance_not_equal_vectors():
    assert JensenShannonDistance().distance(
        Vector(value=[0.5, 0.5]),
        Vector(value=[0.9, 0.1])
    ) > 0.0

@pytest.mark.unit
def test_distance_invalid_input():
    with pytest.raises(ValueError):
        JensenShannonDistance().distance(
            Vector(value=[0.5, 0.5]),
            "invalid input"
        )

@pytest.mark.unit
def test_distance_negative_values():
    with pytest.raises(ValueError):
        JensenShannonDistance().distance(
            Vector(value=[-0.1, 0.9]),
            Vector(value=[0.5, 0.5])
        )

@pytest.mark.unit
def test_similarity():
    assert JensenShannonDistance().similarity(
        Vector(value=[0.5, 0.5]),
        Vector(value=[0.5, 0.5])
    ) == pytest.approx(1.0, rel=1e-5)

@pytest.mark.unit
def test_similarity_not_equal_vectors():
    assert JensenShannonDistance().similarity(
        Vector(value=[0.5, 0.5]),
        Vector(value=[0.9, 0.1])
    ) < 1.0

@pytest.mark.unit
def test_distances():
    distance = JensenShannonDistance()
    vectors = [
        Vector(value=[0.9, 0.1]),
        Vector(value=[0.3, 0.7]),
        Vector(value=[0.5, 0.5])
    ]
    distances = distance.distances(
        Vector(value=[0.5, 0.5]),
        vectors
    )
    assert len(distances) == 3
    assert distances[0] > 0.0
    assert distances[1] > 0.0
    assert distances[2] == pytest.approx(0.0, rel=1e-5)

@pytest.mark.unit
def test_similarities():
    distance = JensenShannonDistance()
    vectors = [
        Vector(value=[0.9, 0.1]),
        Vector(value=[0.3, 0.7]),
        Vector(value=[0.5, 0.5])
    ]
    similarities = distance.similarities(
        Vector(value=[0.5, 0.5]),
        vectors
    )
    assert len(similarities) == 3
    assert similarities[0] < 1.0
    assert similarities[1] < 1.0
