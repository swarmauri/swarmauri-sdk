import pytest
import numpy as np
from swarmauri_standard.similarities.BhattacharyyaCoefficientSimilarity import BhattacharyyaCoefficientSimilarity

@pytest.mark.unit
def test_resource():
    """Test that the resource type is correctly set."""
    assert BhattacharyyaCoefficientSimilarity.resource == "Similarity"

@pytest.mark.unit
def test_type():
    """Test that the type is correctly set."""
    assert BhattacharyyaCoefficientSimilarity.type == "BhattacharyyaCoefficientSimilarity"

@pytest.mark.unit
def test_similarity():
    """Test the similarity calculation with various inputs."""
    bhattacharyya = BhattacharyyaCoefficientSimilarity()
    
    # Test identical distributions
    x = [1, 2, 3]
    y = [1, 2, 3]
    assert bhattacharyya.similarity(x, y) == 1.0
    
    # Test different distributions
    x = [1, 0]
    y = [0, 1]
    assert bhattacharyya.similarity(x, y) == 0.0

@pytest.mark.unit
def test_dissimilarity():
    """Test the dissimilarity calculation."""
    bhattacharyya = BhattacharyyaCoefficientSimilarity()
    
    # Test identical distributions
    x = [1, 2, 3]
    y = [1, 2, 3]
    assert bhattacharyya.dissimilarity(x, y) == 0.0
    
    # Test different distributions
    x = [1, 0]
    y = [0, 1]
    assert bhattacharyya.dissimilarity(x, y) == 1.0

@pytest.mark.unit
def test_check_boundedness():
    """Test that the measure is bounded."""
    bhattacharyya = BhattacharyyaCoefficientSimilarity()
    assert bhattacharyya.check_boundedness() is True

@pytest.mark.unit
def test_check_reflexivity():
    """Test that the measure is reflexive."""
    bhattacharyya = BhattacharyyaCoefficientSimilarity()
    assert bhattacharyya.check_reflexivity() is True

@pytest.mark.unit
def test_check_symmetry():
    """Test that the measure is symmetric."""
    bhattacharyya = BhattacharyyaCoefficientSimilarity()
    assert bhattacharyya.check_symmetry() is True

@pytest.mark.unit
def test_check_identity():
    """Test that the measure satisfies identity of discernibles."""
    bhattacharyya = BhattacharyyaCoefficientSimilarity()
    assert bhattacharyya.check_identity() is True

@pytest.mark.unit
def test_similarity_different_lengths():
    """Test that similarity raises ValueError for different length inputs."""
    bhattacharyya = BhattacharyyaCoefficientSimilarity()
    x = [1, 2]
    y = [3]
    with pytest.raises(ValueError):
        bhattacharyya.similarity(x, y)

@pytest.mark.unit
def test_similarity_empty_arrays():
    """Test that similarity handles empty arrays appropriately."""
    bhattacharyya = BhattacharyyaCoefficientSimilarity()
    x = []
    y = []
    with pytest.raises(ValueError):
        bhattacharyya.similarity(x, y)

@pytest.mark.unit
def test_similarity_normalization():
    """Test that inputs are properly normalized."""
    bhattacharyya = BhattacharyyaCoefficientSimilarity()
    x = [2, 2]
    y = [1, 1]
    assert bhattacharyya.similarity(x, y) == 1.0