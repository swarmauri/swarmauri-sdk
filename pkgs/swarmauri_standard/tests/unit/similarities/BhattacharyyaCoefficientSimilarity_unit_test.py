import pytest
import logging
from swarmauri_standard.swarmauri_standard.similarities.BhattacharyyaCoefficientSimilarity import BhattacharyyaCoefficientSimilarity

@pytest.fixture
def bhattacharyya_coeff():
    """Fixture to provide a BhattacharyyaCoefficientSimilarity instance"""
    return BhattacharyyaCoefficientSimilarity()

@pytest.mark.unit
def test_resource(bhattacharyya_coeff):
    """Test the resource attribute"""
    assert bhattacharyya_coeff.resource == "Similarity"

@pytest.mark.unit
def test_type(bhattacharyya_coeff):
    """Test the type attribute"""
    assert bhattacharyya_coeff.type == "BhattacharyyaCoefficientSimilarity"

@pytest.mark.unit
def test_serialization(bhattacharyya_coeff):
    """Test serialization and deserialization"""
    model = bhattacharyya_coeff.model_dump_json()
    loaded_model = BhattacharyyaCoefficientSimilarity.model_validate_json(model)
    assert bhattacharyya_coeff.id == loaded_model.id

@pytest.mark.unit
@pytest.mark.parametrize("a,b,expected", [
    ([0.5, 0.5], [0.5, 0.5], 1.0),  # Identical distributions
    ([0.0, 1.0], [0.5, 0.5], 0.5),  # Different distributions
])
def test_similarity(a, b, expected, bhattacharyya_coeff):
    """Test the similarity method with valid distributions"""
    result = bhattacharyya_coeff.similarity(a, b)
    assert 0 <= result <= 1
    assert pytest.approx(result) == expected

@pytest.mark.unit
def test_similarity_invalid_distribution(bhattacharyya_coeff):
    """Test similarity with invalid distributions"""
    with pytest.raises(ValueError):
        bhattacharyya_coeff.similarity([1.5, -0.5], [0.5, 0.5])

@pytest.mark.unit
def test_similarity_none_input(bhattacharyya_coeff):
    """Test similarity with None input"""
    result = bhattacharyya_coeff.similarity(None, [0.5, 0.5])
    assert result == 0.0

@pytest.mark.unit
def test_dissimilarity(bhattacharyya_coeff):
    """Test the dissimilarity method"""
    similarity = bhattacharyya_coeff.similarity([0.5, 0.5], [0.5, 0.5])
    dissimilarity = bhattacharyya_coeff.dissimilarity([0.5, 0.5], [0.5, 0.5])
    assert dissimilarity == 1.0 - similarity

@pytest.mark.unit
def test_check_boundedness(bhattacharyya_coeff):
    """Test the boundedness check"""
    result = bhattacharyya_coeff.check_boundedness([0.5, 0.5], [0.5, 0.5])
    assert result is True

@pytest.mark.unit
def test_check_reflexivity(bhattacharyya_coeff):
    """Test the reflexivity check"""
    result = bhattacharyya_coeff.check_reflexivity([0.5, 0.5])
    assert result is True

@pytest.mark.unit
def test_check_symmetry(bhattacharyya_coeff):
    """Test the symmetry check"""
    result = bhattacharyya_coeff.check_symmetry([0.5, 0.5], [0.5, 0.5])
    assert result is True

@pytest.mark.unit
def test_check_identity(bhattacharyya_coeff):
    """Test the identity check"""
    result = bhattacharyya_coeff.check_identity([0.5, 0.5], [0.5, 0.5])
    assert result is True

@pytest.mark.unit
@pytest.mark.parametrize("p,q,expected", [
    ([0.5, 0.5], [0.5, 0.5], 1.0),
    ([1.0, 0.0], [0.0, 1.0], 0.0),
])
def test_bhattacharyya_coefficient(p, q, expected):
    """Test the Bhattacharyya coefficient calculation"""
    result = BhattacharyyaCoefficientSimilarity._bhattacharyya_coefficient(p, q)
    assert 0 <= result <= 1
    assert pytest.approx(result) == expected

@pytest.mark.unit
def test_bhattacharyya_coefficient_invalid_length():
    """Test Bhattacharyya coefficient with different length distributions"""
    with pytest.raises(ValueError):
        BhattacharyyaCoefficientSimilarity._bhattacharyya_coefficient([0.5, 0.5], [0.3])

@pytest.mark.unit
@pytest.mark.parametrize("distribution,expected", [
    ([0.5, 0.5], True),
    ([1.0, 0.0], True),
    ([1.5, -0.5], False),
    ([0.3, 0.3, 0.4], True),
])
def test_is_valid_distribution(distribution, expected):
    """Test distribution validation"""
    result = BhattacharyyaCoefficientSimilarity._is_valid_distribution(distribution)
    assert result == expected