import pytest
from swarmauri.distances.concrete.MahalanobisDistance import MahalanobisDistance  
from swarmauri.vectors.concrete.Vector import Vector

@pytest.mark.unit
def test_ubc_resource():
	assert MahalanobisDistance().resource == 'Distance'

@pytest.mark.unit
def test_ubc_type():
	assert MahalanobisDistance().type == 'MahalanobisDistance' 

@pytest.mark.unit
def test_serialization():
    distance = MahalanobisDistance() 
    assert distance.id == MahalanobisDistance.model_validate_json(distance.model_dump_json()).id

@pytest.mark.unit
def test_distance(self):
	assert MahalanobisDistance().distance(
	    Vector(value=[1,2]), 
	    Vector(value=[1,2])
	    ) == 0.0

@pytest.mark.unit
def test_distance_not_equal_vectors():
	assert MahalanobisDistance().distance(
	    Vector(value=[1,2]), 
	    Vector(value=[3,4])
	    ) != 0.0

@pytest.mark.unit
def test_distance_invalid_input():
    with pytest.raises(TypeError):
        MahalanobisDistance().distance(
            Vector(value=[1, 2]), 
            "invalid input"
        )

@pytest.mark.unit
def test_similarity(self):
	assert MahalanobisDistance().similarity(
	    Vector(value=[1,2]), 
	    Vector(value=[1,2])
	    ) == 1.0

@pytest.mark.unit
def test_similarity_not_equal_vectors():
	assert MahalanobisDistance().similarity(
	    Vector(value=[1,2]), 
	    Vector(value=[3,4])
	    ) != 1.0

@pytest.mark.unit
def test_similarity_invalid_input():
    with pytest.raises(TypeError):
        MahalanobisDistance().similarity(
            Vector(value=[1, 2]), 
            "invalid input"
        )

@pytest.mark.unit
def test_distances(self):
    distance = MahalanobisDistance()
    vectors = [
        Vector(value=[1, 2]),
        Vector(value=[3, 4]),
        Vector(value=[5, 6])
    ]
    distances = distance.distances(
        Vector(value=[1, 2]), 
        vectors
    )
    assert len(distances) == 3
    assert distances[0] != 0.0
    assert distances[1] != 0.0
    assert distances[2] != 0.0

@pytest.mark.unit
def test_similarities(self):
    distance = MahalanobisDistance()
    vectors = [
        Vector(value=[1, 2]),
        Vector(value=[3, 4]),
        Vector(value=[5, 6])
    ]
    similarities = distance.similarities(
        Vector(value=[1, 2]), 
        vectors
    )
    assert len(similarities) == 3
    assert similarities[0] != 1.0
    assert similarities[1] != 1.0
    assert similarities[2] != 1.0
