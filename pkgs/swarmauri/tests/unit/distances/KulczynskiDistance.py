import numpy as np
from typing import List, Literal
from swarmauri.vectors.concrete.Vector import Vector
from swarmauri.distances.concrete.KulczynskiDistance import KulczynskiDistance
from swarmauri.vectors.concrete.Vector import Vector


@pytest.mark.unit
def test_ubc_resource():
    assert KulczynskiDistance().resource == 'Distance'

@pytest.mark.unit
def test_ubc_type():
    assert KulczynskiDistance().type == 'KulczynskiDistance' 

@pytest.mark.unit
def test_serialization():
    distance = KulczynskiDistance() 
    assert distance.id == KulczynskiDistance.model_validate_json(distance.model_dump_json()).id

@pytest.mark.unit
def test_distance():
    vector_a = Vector(value=[1,2,3])
    vector_b = Vector(value=[1,2,3])
    assert KulczynskiDistance().distance(vector_a, vector_b) == 0.0

@pytest.mark.unit
def test_distance_not_equal_vectors():
    vector_a = Vector(value=[1,2,3])
    vector_b = Vector(value=[4,5,6])
    assert KulczynskiDistance().distance(vector_a, vector_b) != 0.0

@pytest.mark.unit
def test_distance_invalid_input():
    vector_a = Vector(value=[1, 2, 3])
    with pytest.raises(TypeError):
        KulczynskiDistance().distance(vector_a, "invalid input")

@pytest.mark.unit
def test_similarity():
    vector_a = Vector(value=[1,2,3])
    vector_b = Vector(value=[1,2,3])
    assert KulczynskiDistance().similarity(vector_a, vector_b) == 1.0

@pytest.mark.unit
def test_similarity_not_equal_vectors():
    vector_a = Vector(value=[1,2,3])
    vector_b = Vector(value=[4,5,6])
    assert KulczynskiDistance().similarity(vector_a, vector_b) != 1.0

@pytest.mark.unit
def test_similarity_invalid_input():
    vector_a = Vector(value=[1, 2, 3])
    with pytest.raises(TypeError):
        KulczynskiDistance().similarity(vector_a, "invalid input")

@pytest.mark.unit
def test_distances():
    distance = KulczynskiDistance()
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
    distance = KulczynskiDistance()
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
