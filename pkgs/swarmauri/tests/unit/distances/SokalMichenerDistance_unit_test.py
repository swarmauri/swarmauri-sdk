import pytest
from swarmauri.distances.concrete.SokalMichenerDistance import SokalMichenerDistance
from swarmauri.vectors.concrete.Vector import Vector

@pytest.mark.unit
def test_ubc_resource():
    assert SokalMichenerDistance().resource == 'Distance'

@pytest.mark.unit
def test_ubc_type():
    assert SokalMichenerDistance().type == 'SokalMichenerDistance'

@pytest.mark.unit
def test_serialization():
    distance = SokalMichenerDistance()
    assert distance.id == SokalMichenerDistance.model_validate_json(distance.model_dump_json()).id

@pytest.mark.unit
def test_distance_identical_vectors():
    assert SokalMichenerDistance().distance(
        Vector(value=[1, 0, 1, 0]),
        Vector(value=[1, 0, 1, 0])
    ) == pytest.approx(0.0, rel=1e-5)

@pytest.mark.unit
def test_distance_not_equal_vectors():
    assert SokalMichenerDistance().distance(
        Vector(value=[1, 0, 1, 0]),
        Vector(value=[0, 1, 0, 1])
    ) == pytest.approx(1.0, rel=1e-5)

@pytest.mark.unit
def test_distance_invalid_input():
    with pytest.raises(ValueError):
        SokalMichenerDistance().distance(
            Vector(value=[1, 0, 1]),
            "invalid input"
        )

@pytest.mark.unit
def test_distance_non_binary_vectors():
    with pytest.raises(ValueError):
        SokalMichenerDistance().distance(
            Vector(value=[1, 2, 3]),
            Vector(value=[1, 0, 1])
        )

@pytest.mark.unit
def test_similarity_identical_vectors():
    assert SokalMichenerDistance().similarity(
        Vector(value=[1, 0, 1, 0]),
        Vector(value=[1, 0, 1, 0])
    ) == pytest.approx(1.0, rel=1e-5)

@pytest.mark.unit
def test_similarity_not_equal_vectors():
    assert SokalMichenerDistance().similarity(
        Vector(value=[1, 0, 1, 0]),
        Vector(value=[0, 1, 0, 1])
    ) == pytest.approx(0.0, rel=1e-5)

@pytest.mark.unit
def test_distances():
    distance = SokalMichenerDistance()
    vectors = [
        Vector(value=[1, 0, 1, 0]),
        Vector(value=[0, 1, 0, 1]),
        Vector(value=[1, 1, 1, 1])
    ]
    distances = distance.distances(
        Vector(value=[1, 0, 1, 0]),
        vectors
    )
    assert len(distances) == 3
    assert distances[0] == pytest.approx(0.0, rel=1e-5)
    assert distances[1] == pytest.approx(1.0, rel=1e-5)
    assert distances[2] > 0.0

@pytest.mark.unit
def test_similarities():
    distance = SokalMichenerDistance()
    vectors = [
        Vector(value=[1, 0, 1, 0]),
        Vector(value=[0, 1, 0, 1]),
        Vector(value=[1, 1, 1, 1])
    ]
    similarities = distance.similarities(
        Vector(value=[1, 0, 1, 0]),
        vectors
    )
    assert len(similarities) == 3
    assert similarities[0] == pytest.approx(1.0, rel=1e-5)
    assert similarities[1] == pytest.approx(0.0, rel=1e-5)
    assert similarities[2] < 1.0
