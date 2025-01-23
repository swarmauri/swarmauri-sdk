import pytest
from swarmauri.distances.concrete.GeneralizedCosineMetric import GeneralizedCosineMetric
from swarmauri.vectors.concrete.Vector import Vector
import numpy as np


@pytest.mark.unit
def test_ubc_resource():
    assert GeneralizedCosineMetric().resource == 'Distance'


@pytest.mark.unit
def test_ubc_type():
    assert GeneralizedCosineMetric().type == 'GeneralizedCosineMetric'


@pytest.mark.unit
def test_serialization():
    metric = GeneralizedCosineMetric()
    assert metric.id == GeneralizedCosineMetric.model_validate_json(metric.model_dump_json()).id


@pytest.mark.unit
def test_distance():
    metric = GeneralizedCosineMetric()
    assert metric.distance(Vector(value=[1, 2, 3]), Vector(value=[1, 2, 3])) == 0.0


@pytest.mark.unit
def test_distance_not_equal_vectors():
    metric = GeneralizedCosineMetric()
    distance = metric.distance(Vector(value=[1, 2, 3]), Vector(value=[4, 5, 6]))
    assert distance > 0.0


@pytest.mark.unit
def test_distance_invalid_input():
    metric = GeneralizedCosineMetric()
    with pytest.raises(ValueError):
        metric.distance(Vector(value=[1, 2]), Vector(value=[1, 2, 3]))


@pytest.mark.unit
def test_similarity():
    metric = GeneralizedCosineMetric()
    assert metric.similarity(Vector(value=[1, 2, 3]), Vector(value=[1, 2, 3])) == 1.0


@pytest.mark.unit
def test_similarity_not_equal_vectors():
    metric = GeneralizedCosineMetric()
    similarity = metric.similarity(Vector(value=[1, 2, 3]), Vector(value=[4, 5, 6]))
    assert similarity < 1.0


@pytest.mark.unit
def test_similarity_invalid_input():
    metric = GeneralizedCosineMetric()
    with pytest.raises(ValueError):
        metric.similarity(Vector(value=[1, 2]), Vector(value=[1, 2, 3]))


@pytest.mark.unit
def test_similarities():
    metric = GeneralizedCosineMetric()
    a = Vector(value=[1, 2, 3])
    b = [Vector(value=[4, 5, 6]), Vector(value=[7, 8, 9])]
    
    similarities = metric.similarities(a, b)
    assert len(similarities) == 2
    assert all(0 <= s <= 1 for s in similarities)


@pytest.mark.unit
def test_triangle_inequality():
    metric = GeneralizedCosineMetric()
    a = Vector(value=[1, 2, 3])
    b = Vector(value=[4, 5, 6])
    c = Vector(value=[7, 8, 9])
    
    # Check the triangle inequality
    assert metric.triangle_inequality(a, b, c) is True


@pytest.mark.unit
def test_distances():
    metric = GeneralizedCosineMetric()
    a = Vector(value=[1, 2, 3])
    b = [Vector(value=[4, 5, 6]), Vector(value=[7, 8, 9])]
    
    distances = metric.distances(a, b)
    assert len(distances) == 2
    assert all(d > 0 for d in distances)


@pytest.mark.unit
def test_expected_distance():
    metric = GeneralizedCosineMetric()
    a = Vector(value=[1, 2, 3])
    b = Vector(value=[1, 3, 5])
    
    # Compute the expected distance manually
    total_difference = sum([abs(x - y) for x, y in zip(a.value, b.value)])
    expected_distance = 1 - np.cos(total_difference)
    
    # Compute using the metric class
    calculated_distance = metric.distance(a, b)
    assert pytest.approx(calculated_distance, 0.001) == expected_distance


@pytest.mark.unit
def test_expected_similarity():
    metric = GeneralizedCosineMetric()
    a = Vector(value=[1, 2, 3])
    b = Vector(value=[1, 3, 5])
    
    # Compute the similarity
    total_difference = sum([abs(x - y) for x, y in zip(a.value, b.value)])
    expected_distance = 1 - np.cos(total_difference)
    expected_similarity = 1 / (1 + expected_distance)
    
    # Compute using the metric class
    calculated_similarity = metric.similarity(a, b)
    assert pytest.approx(calculated_similarity, 0.001) == expected_similarity
