import pytest
from swarmauri.distances.concrete.WassersteinDistance import WassersteinDistance
from swarmauri.vectors.concrete.Vector import Vector

@pytest.mark.unit
def test_ubc_resource():
    assert WassersteinDistance().resource == 'Distance'

@pytest.mark.unit
def test_ubc_type():
    assert WassersteinDistance().type == 'WassersteinDistance'

@pytest.mark.unit
def test_serialization():
    distance = WassersteinDistance()
    assert distance.id == WassersteinDistance.model_validate_json(distance.model_dump_json()).id

@pytest.mark.unit
def test_distance():
    assert WassersteinDistance().distance(
        Vector(value=[1, 2, 3]),
        Vector(value=[1, 2, 3])
    ) == 0.0

@pytest.mark.unit
def test_distance_not_equal_vectors():
    assert WassersteinDistance().distance(
        Vector(value=[1, 2, 3]),
        Vector(value=[4, 5, 6])
    ) > 0.0

@pytest.mark.unit
def test_distance_invalid_input():
    with pytest.raises(TypeError):
        WassersteinDistance().distance(
            Vector(value=[1, 2, 3]),
            "invalid input"
        )

@pytest.mark.unit
def test_distance_different_lengths():
    with pytest.raises(ValueError):
        WassersteinDistance().distance(
            Vector(value=[1, 2]),
            Vector(value=[1, 2, 3])
        )

@pytest.mark.unit
def test_similarity():
    assert WassersteinDistance().similarity(
        Vector(value=[1, 2, 3]),
        Vector(value=[1, 2, 3])
    ) == pytest.approx(1.0, rel=1e-5)

@pytest.mark.unit
def test_similarity_not_equal_vectors():
    assert WassersteinDistance().similarity(
        Vector(value=[1, 2, 3]),
        Vector(value=[4, 5, 6])
    ) < 1.0

@pytest.mark.unit
def test_similarity_invalid_input():
    with pytest.raises(TypeError):
        WassersteinDistance().similarity(
            Vector(value=[1, 2, 3]),
            "invalid input"
        )

@pytest.mark.unit
def test_distances():
    distance = WassersteinDistance()
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
    distance = WassersteinDistance()
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
