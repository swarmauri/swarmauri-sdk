import pytest
from swarmauri.distances.concrete.BraysCurtisDistance import BrayCurtisDistance
from swarmauri.vectors.concrete.Vector import Vector

@pytest.mark.unit
def test_ubc_resource():
    assert BrayCurtisDistance().resource == 'Distance'

@pytest.mark.unit
def test_ubc_type():
    assert BrayCurtisDistance().type == 'BrayCurtisDistance' 

@pytest.mark.unit
def test_serialization():
    distance = BrayCurtisDistance() 
    assert distance.id == BrayCurtisDistance.model_validate_json(distance.model_dump_json()).id

@pytest.mark.unit
def test_distance():
    vector_a = Vector(value=[1,2,3])
    vector_b = Vector(value=[1,2,3])
    assert BrayCurtisDistance().distance(vector_a, vector_b) == 0.0

@pytest.mark.unit
def test_distance_not_equal_vectors():
    vector_a = Vector(value=[1,2,3])
    vector_b = Vector(value=[4,5,6])
    assert BrayCurtisDistance().distance(vector_a, vector_b) != 0.0

@pytest.mark.unit
def test_distance_invalid_input():
    vector_a = Vector(value=[1, 2, 3])
    with pytest.raises(TypeError):
        BrayCurtisDistance().distance(vector_a, "invalid input")

@pytest.mark.unit
def test_similarity():
    vector_a = Vector(value=[1,2,3])
    vector_b = Vector(value=[1,2,3])
    assert BrayCurtisDistance().similarity(vector_a, vector_b) == 1.0

@pytest.mark.unit
def test_similarity_not_equal_vectors():
    vector_a = Vector(value=[1,2,3])
    vector_b = Vector(value=[4,5,6])
    assert BrayCurtisDistance().similarity(vector_a, vector_b) != 1.0

@pytest.mark.unit
def test_similarity_invalid_input():
    vector_a = Vector(value=[1, 2, 3])
    with pytest.raises(TypeError):
        BrayCurtisDistance().similarity(vector_a, "invalid input")

@pytest.mark.unit
def test_distances():
    distance = BrayCurtisDistance()
    vectors = [
        Vector(value=[1, 2, 3]),
        Vector(value=[4, 5, 6]),
        Vector(value=[7, 8, 9])
    ]
    distances = distance.distances(
        Vector(value=[1, 2, 3]), 
        vectors
    )
    assert len(distances) == 3
    assert distances[0] != 0.0
    assert distances[1] != 0.0
    assert distances[2] != 0.0

@pytest.mark.unit
def test_similarities():
    distance = BrayCurtisDistance()
    vectors = [
        Vector(value=[1, 2, 3]),
        Vector(value=[4, 5, 6]),
        Vector(value=[7, 8, 9])
    ]
    similarities = distance.similarities(
        Vector(value=[1, 2, 3]), 
        vectors
    )
    assert len(similarities) == 3
    assert similarities[0] != 1.0
    assert similarities[1] != 1.0
    assert similarities[2] != 1.0

@pytest.mark.parametrize(
    "vector_a, vector_b, expected_distance",
    [
        (Vector(value=[1, 2, 3]), Vector(value=[1, 2, 3]), 0.0),
        (Vector(value=[1, 2, 3]), Vector(value=[4, 5, 6]), 0.1875),
        (Vector(value=[1, 1, 1]), Vector(value=[0.5, 2, 3]), 0.375),
        (Vector(value=[1, 1, 1]), Vector(value=[0, 0, 0]), 1.0),
    ],
)
@pytest.mark.unit
def test_braycurtis_distance(vector_a, vector_b, expected_distance):
    distance = BrayCurtisDistance()
    assert distance.distance(vector_a, vector_b) == expected_distance

@pytest.mark.parametrize(
    "vector_a, vector_b, expected_similarity",
    [
        (Vector(value=[1, 2, 3]), Vector(value=[1, 2, 3]), 1.0),
        (Vector(value=[1, 2, 3]), Vector(value=[4, 5, 6]), 0.8125),
        (Vector(value=[1, 1, 1]), Vector(value=[0.5, 2, 3]), 0.625),
        (Vector(value=[1, 1, 1]), Vector(value=[0, 0, 0]), 0),
    ],
)
@pytest.mark.unit
def test_braycurtis_similarity(vector_a, vector_b, expected_similarity):
    distance = BrayCurtisDistance()
    assert distance.similarity(vector_a, vector_b) == expected_similarity
