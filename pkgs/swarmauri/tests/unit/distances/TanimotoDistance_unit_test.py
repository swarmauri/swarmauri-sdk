import pytest
from swarmauri.distances.concrete.TanimotoDistance import TanimotoDistance
from swarmauri.vectors.concrete.Vector import Vector

@pytest.mark.unit
def test_ubc_resource():
    assert TanimotoDistance().resource == 'Distance'

@pytest.mark.unit
def test_ubc_type():
    assert TanimotoDistance().type == 'TanimotoDistance'

@pytest.mark.unit
def test_serialization():
    distance = TanimotoDistance()
    assert distance.id == TanimotoDistance.model_validate_json(distance.model_dump_json()).id

@pytest.mark.unit
def test_distance():
    assert TanimotoDistance().distance(
        Vector(value=[1, 2, 3]),
        Vector(value=[1, 2, 3])
    ) == 0.0

@pytest.mark.unit
def test_distance_not_equal_vectors():
    assert TanimotoDistance().distance(
        Vector(value=[1, 2, 3]),
        Vector(value=[4, 5, 6])
    ) > 0.0

@pytest.mark.unit
def test_distance_invalid_input():
    with pytest.raises(TypeError):
        TanimotoDistance().distance(
            Vector(value=[1, 2, 3]),
            "invalid input"
        )

@pytest.mark.unit
def test_distance_negative_values():
    with pytest.raises(ValueError):
        TanimotoDistance().distance(
            Vector(value=[-1, 2, 3]),
            Vector(value=[1, 2, 3])
        )

@pytest.mark.unit
def test_similarity():
    assert TanimotoDistance().similarity(
        Vector(value=[1, 2, 3]),
        Vector(value=[1, 2, 3])
    ) == pytest.approx(1.0, rel=1e-5)

@pytest.mark.unit
def test_similarity_not_equal_vectors():
    assert TanimotoDistance().similarity(
        Vector(value=[1, 2, 3]),
        Vector(value=[4, 5, 6])
    ) < 1.0

@pytest.mark.unit
def test_distances():
    distance = TanimotoDistance()
    vectors = [
        Vector(value=[4, 5, 6]),
        Vector(value=[7, 8, 9]),
        Vector(value=[10, 11, 12])
    ]
    distances = distance.distances(
        Vector(value=[1, 2, 3]),
        vectors
    )
    assert len(distances) == 3
    assert distances[0] > 0.0
    assert distances[1] > 0.0
    assert distances[2] > 0.0

@pytest.mark.unit
def test_similarities():
    distance = TanimotoDistance()
    vectors = [
        Vector(value=[4, 5, 6]),
        Vector(value=[7, 8, 9]),
        Vector(value=[10, 11, 12])
    ]
    similarities = distance.similarities(
        Vector(value=[1, 2, 3]),
        vectors
    )
    assert len(similarities) == 3
    assert similarities[0] < 1.0
    assert similarities[1] < 1.0
    assert similarities[2] < 1.0
