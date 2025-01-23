import pytest
from swarmauri.distances.concrete.AdaptiveWeightedMetric import AdaptiveWeightedMetric
from swarmauri.vectors.concrete.Vector import Vector
import numpy as np


@pytest.mark.unit
def test_ubc_resource():
    assert AdaptiveWeightedMetric().resource == 'Distance'


@pytest.mark.unit
def test_ubc_type():
    assert AdaptiveWeightedMetric().type == 'AdaptiveWeightedMetric'


@pytest.mark.unit
def test_distance_same_vector():
    metric = AdaptiveWeightedMetric()
    a = Vector(value=[1, 2, 3])
    alphas = [0.5, 0.5, 0.5]
    assert metric.distance(a, a, alphas) == 0.0


@pytest.mark.unit
def test_distance_different_vectors():
    metric = AdaptiveWeightedMetric()
    a = Vector(value=[1, 2, 3])
    b = Vector(value=[4, 5, 6])
    alphas = [0.5, 0.5, 0.5]
    assert metric.distance(a, b, alphas) > 0.0


@pytest.mark.unit
def test_similarity_same_vector():
    metric = AdaptiveWeightedMetric()
    a = Vector(value=[1, 2, 3])
    alphas = [0.5, 0.5, 0.5]
    assert metric.similarity(a, a, alphas) == 1.0


@pytest.mark.unit
def test_similarity_different_vectors():
    metric = AdaptiveWeightedMetric()
    a = Vector(value=[1, 2, 3])
    b = Vector(value=[4, 5, 6])
    alphas = [0.5, 0.5, 0.5]
    assert 0 < metric.similarity(a, b, alphas) < 1.0


@pytest.mark.unit
def test_distances():
    metric = AdaptiveWeightedMetric()
    a = Vector(value=[1, 2, 3])
    b = [Vector(value=[4, 5, 6]), Vector(value=[7, 8, 9])]
    alphas = [0.5, 0.5, 0.5]
    
    distances = metric.distances(a, b, alphas)
    assert len(distances) == 2
    assert all(d > 0 for d in distances)


@pytest.mark.unit
def test_similarities():
    metric = AdaptiveWeightedMetric()
    a = Vector(value=[1, 2, 3])
    b = [Vector(value=[4, 5, 6]), Vector(value=[7, 8, 9])]
    alphas = [0.5, 0.5, 0.5]
    
    similarities = metric.similarities(a, b, alphas)
    assert len(similarities) == 2
    assert all(0 <= s <= 1 for s in similarities)


@pytest.mark.unit
def test_triangle_inequality():
    metric = AdaptiveWeightedMetric()
    a = Vector(value=[1, 2, 3])
    b = Vector(value=[4, 5, 6])
    c = Vector(value=[7, 8, 9])
    alphas = [0.5, 0.5, 0.5]
    assert metric.triangle_inequality(a, b, c, alphas) is True


@pytest.mark.unit
def test_non_negativity():
    metric = AdaptiveWeightedMetric()
    a = Vector(value=[1, 2, 3])
    b = Vector(value=[4, 5, 6])
    alphas = [0.5, 0.5, 0.5]
    assert metric.check_non_negativity(a, b, alphas) is True


@pytest.mark.unit
def test_identity_of_indiscernibles():
    metric = AdaptiveWeightedMetric()
    a = Vector(value=[1, 2, 3])
    b = Vector(value=[1, 2, 3])
    c = Vector(value=[4, 5, 6])
    alphas = [0.5, 0.5, 0.5]
    assert metric.check_identity_of_indiscernibles(a, b, alphas) is True
    assert metric.check_identity_of_indiscernibles(a, c, alphas) is True


@pytest.mark.unit
def test_symmetry():
    metric = AdaptiveWeightedMetric()
    a = Vector(value=[1, 2, 3])
    b = Vector(value=[4, 5, 6])
    alphas = [0.5, 0.5, 0.5]
    assert metric.check_symmetry(a, b, alphas) is True


@pytest.mark.unit
def test_positivity():
    metric = AdaptiveWeightedMetric()
    a = Vector(value=[1, 2, 3])
    b = Vector(value=[4, 5, 6])
    alphas = [0.5, 0.5, 0.5]
    assert metric.check_positivity(a, b, alphas) is True
    assert metric.check_positivity(a, a, alphas) is True


@pytest.mark.unit
def test_expected_distance():
    metric = AdaptiveWeightedMetric()
    a = Vector(value=[1, 2, 3])
    b = Vector(value=[4, 5, 6])
    alphas = [0.5, 0.5, 0.5]
    
    # Manually compute the expected distance
    differences = np.abs(np.array(a.value) - np.array(b.value))
    expected_distance = np.sum(differences / (1 + alphas * np.abs(np.array(a.value))))
    
    # Use the class method
    calculated_distance = metric.distance(a, b, alphas)
    assert pytest.approx(calculated_distance, 0.001) == expected_distance


@pytest.mark.unit
def test_expected_similarity():
    metric = AdaptiveWeightedMetric()
    a = Vector(value=[1, 2, 3])
    b = Vector(value=[4, 5, 6])
    alphas = [0.5, 0.5, 0.5]
    
    # Compute the similarity manually
    differences = np.abs(np.array(a.value) - np.array(b.value))
    expected_distance = np.sum(differences / (1 + alphas * np.abs(np.array(a.value))))
    expected_similarity = 1 / (1 + expected_distance)
    
    # Use the class method
    calculated_similarity = metric.similarity(a, b, alphas)
    assert pytest.approx(calculated_similarity, 0.001) == expected_similarity
