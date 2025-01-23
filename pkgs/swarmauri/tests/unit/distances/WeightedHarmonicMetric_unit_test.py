import pytest
from swarmauri.distances.concrete.WeightedHarmonicMetric import WeightedHarmonicMetric
from swarmauri.vectors.concrete.Vector import Vector
import numpy as np


@pytest.mark.unit
def test_ubc_resource():
    assert WeightedHarmonicMetric().resource == 'Distance'


@pytest.mark.unit
def test_ubc_type():
    assert WeightedHarmonicMetric().type == 'WeightedHarmonicMetric'


@pytest.mark.unit
def test_serialization():
    metric = WeightedHarmonicMetric()
    assert metric.id == WeightedHarmonicMetric.model_validate_json(metric.model_dump_json()).id


@pytest.mark.unit
def test_distance_same_vector():
    metric = WeightedHarmonicMetric()
    a = Vector(value=[1, 2, 3])
    weights = [1, 1, 1]
    assert metric.distance(a, a, weights) == 3.0


@pytest.mark.unit
def test_distance_different_vectors():
    metric = WeightedHarmonicMetric()
    a = Vector(value=[1, 2, 3])
    b = Vector(value=[4, 5, 6])
    weights = [1, 1, 1]
    assert metric.distance(a, b, weights) < 3.0


@pytest.mark.unit
def test_distance_invalid_input():
    metric = WeightedHarmonicMetric()
    a = Vector(value=[1, 2])
    b = Vector(value=[1, 2, 3])
    weights = [1, 1, 1]
    with pytest.raises(ValueError):
        metric.distance(a, b, weights)


@pytest.mark.unit
def test_similarity():
    metric = WeightedHarmonicMetric()
    a = Vector(value=[1, 2, 3])
    b = Vector(value=[1, 2, 3])
    weights = [1, 1, 1]
    assert metric.similarity(a, b, weights) == 1.0


@pytest.mark.unit
def test_similarity_different_vectors():
    metric = WeightedHarmonicMetric()
    a = Vector(value=[1, 2, 3])
    b = Vector(value=[4, 5, 6])
    weights = [1, 1, 1]
    similarity = metric.similarity(a, b, weights)
    assert 0 <= similarity < 1.0


@pytest.mark.unit
def test_similarity_invalid_input():
    metric = WeightedHarmonicMetric()
    a = Vector(value=[1, 2])
    b = Vector(value=[1, 2, 3])
    weights = [1, 1, 1]
    with pytest.raises(ValueError):
        metric.similarity(a, b, weights)


@pytest.mark.unit
def test_similarities():
    metric = WeightedHarmonicMetric()
    a = Vector(value=[1, 2, 3])
    b = [Vector(value=[4, 5, 6]), Vector(value=[7, 8, 9])]
    weights = [1, 1, 1]
    
    similarities = metric.similarities(a, b, weights)
    assert len(similarities) == 2
    assert all(0 <= s <= 1 for s in similarities)


@pytest.mark.unit
def test_distances():
    metric = WeightedHarmonicMetric()
    a = Vector(value=[1, 2, 3])
    b = [Vector(value=[4, 5, 6]), Vector(value=[7, 8, 9])]
    weights = [1, 1, 1]
    
    distances = metric.distances(a, b, weights)
    assert len(distances) == 2
    assert all(d > 0 for d in distances)


@pytest.mark.unit
def test_triangle_inequality():
    metric = WeightedHarmonicMetric()
    a = Vector(value=[1, 2, 3])
    b = Vector(value=[2, 3, 4])
    c = Vector(value=[3, 4, 5])
    weights = [1, 1, 1]
    assert metric.triangle_inequality(a, b, c, weights) is True


@pytest.mark.unit
def test_expected_distance():
    metric = WeightedHarmonicMetric()
    a = Vector(value=[1, 2, 3])
    b = Vector(value=[1, 3, 5])
    weights = [1, 1, 1]
    
    # Compute the expected distance manually
    total_difference = np.abs(np.array(a.value) - np.array(b.value))
    expected_distance = np.sum(1 / (1 + total_difference * np.array(weights)))
    
    # Compute using the metric class
    calculated_distance = metric.distance(a, b, weights)
    assert pytest.approx(calculated_distance, 0.001) == expected_distance


@pytest.mark.unit
def test_expected_similarity():
    metric = WeightedHarmonicMetric()
    a = Vector(value=[1, 2, 3])
    b = Vector(value=[1, 3, 5])
    weights = [1, 1, 1]
    
    # Compute the similarity
    total_difference = np.abs(np.array(a.value) - np.array(b.value))
    expected_distance = np.sum(1 / (1 + total_difference * np.array(weights)))
    expected_similarity = 1 / (1 + expected_distance)
    
    # Compute using the metric class
    calculated_similarity = metric.similarity(a, b, weights)
    assert pytest.approx(calculated_similarity, 0.001) == expected_similarity
