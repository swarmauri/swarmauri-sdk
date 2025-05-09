import logging

import pytest

from swarmauri_standard.similarities.BrayCurtisSimilarity import BrayCurtisSimilarity


@pytest.mark.unit
def test_braycurtis_similarity_type():
    """Test that BrayCurtisSimilarity type is correctly set."""
    assert BrayCurtisSimilarity.type == "BrayCurtisSimilarity"


@pytest.mark.unit
def test_braycurtis_similarity_resource():
    """Test that BrayCurtisSimilarity resource is correctly set."""
    assert BrayCurtisSimilarity.resource == "SIMILARITY"


@pytest.mark.unit
def test_braycurtis_similarity_init(mocker):
    """Test that BrayCurtisSimilarity initializes correctly."""
    mock_logger = mocker.patch.object(logging.getLogger(__name__), "debug")
    BrayCurtisSimilarity()
    mock_logger.assert_called_once_with("BrayCurtisSimilarity instance initialized")


@pytest.mark.unit
def test_braycurtis_similarity_valid_vectors():
    """Test BrayCurtisSimilarity with valid input vectors."""
    braycurtis = BrayCurtisSimilarity()

    # Test with identical vectors
    x = [1, 2, 3]
    y = [1, 2, 3]
    similarity = braycurtis.similarity(x, y)
    assert similarity == 1.0

    # Test with different vectors
    x = [1, 0]
    y = [0, 1]
    similarity = braycurtis.similarity(x, y)
    assert 0 <= similarity <= 1


@pytest.mark.unit
def test_braycurtis_similarity_zero_vectors():
    """Test BrayCurtisSimilarity with zero vectors."""
    braycurtis = BrayCurtisSimilarity()
    x = [0, 0]
    y = [0, 0]
    similarity = braycurtis.similarity(x, y)
    assert similarity == 1.0


@pytest.mark.unit
def test_braycurtis_similarity_error_handling():
    """Test that invalid input raises ValueError."""
    braycurtis = BrayCurtisSimilarity()

    # Test vectors of different lengths
    x = [1, 2]
    y = [1]
    with pytest.raises(ValueError):
        braycurtis.similarity(x, y)

    # Test negative values
    x = [1, -2]
    y = [1, 2]
    with pytest.raises(ValueError):
        braycurtis.similarity(x, y)


@pytest.mark.unit
def test_braycurtis_dissimilarity():
    """Test BrayCurtis dissimilarity calculation."""
    braycurtis = BrayCurtisSimilarity()
    x = [1, 0]
    y = [0, 1]
    similarity = braycurtis.similarity(x, y)
    dissimilarity = braycurtis.dissimilarity(x, y)
    assert dissimilarity == 1.0 - similarity


@pytest.mark.unit
def test_braycurtis_similarity_properties():
    """Test BrayCurtis similarity properties."""
    braycurtis = BrayCurtisSimilarity()

    # Test boundedness
    assert braycurtis.check_boundedness() is True

    # Test reflexivity
    assert braycurtis.check_reflexivity() is True

    # Test symmetry
    assert braycurtis.check_symmetry() is True

    # Test identity of discernibles
    assert braycurtis.check_identity() is True
