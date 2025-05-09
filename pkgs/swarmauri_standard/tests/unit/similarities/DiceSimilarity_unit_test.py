import pytest
from swarmauri_standard.swarmauri_standard.similarities.DiceSimilarity import DiceSimilarity
import logging

@pytest.fixture
def logging_fixture():
    """Fixture to handle logging setup and teardown"""
    # Set up logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    # Clear any existing handlers
    logger.handlers.clear()
    # Add a handler for testing
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    yield logger
    # Teardown - remove the handler
    logger.removeHandler(handler)

@pytest.mark.unit
def test_dice_similarity_init():
    """Test initialization of DiceSimilarity class"""
    # Arrange and Act
    similarity = DiceSimilarity()
    
    # Assert
    assert similarity.type == "DiceSimilarity"

@pytest.mark.unit
def test_dice_similarity_empty_sets(logging_fixture):
    """Test Dice similarity calculation with empty sets"""
    # Arrange
    similarity = DiceSimilarity()
    
    # Act
    result = similarity.similarity("", "")
    
    # Assert
    assert result == 1.0

@pytest.mark.unit
def test_dice_similarity_no_overlap():
    """Test Dice similarity calculation with no overlapping elements"""
    # Arrange
    similarity = DiceSimilarity()
    
    # Act
    result = similarity.similarity("abc", "def")
    
    # Assert
    assert result == 0.0

@pytest.mark.unit
def test_dice_similarity_partial_overlap():
    """Test Dice similarity calculation with partial overlapping elements"""
    # Arrange
    similarity = DiceSimilarity()
    
    # Act
    result = similarity.similarity("ab", "ab")
    
    # Assert
    assert result == 1.0

@pytest.mark.unit
def test_dice_similarity_multiset():
    """Test Dice similarity calculation with multiset input"""
    # Arrange
    similarity = DiceSimilarity()
    
    # Act
    result = similarity.similarity("aab", "aab")
    
    # Assert
    assert result == 1.0

@pytest.mark.unit
def test_dice_similarity_single_element():
    """Test Dice similarity calculation with single element"""
    # Arrange
    similarity = DiceSimilarity()
    
    # Act
    result = similarity.similarity("a", "a")
    
    # Assert
    assert result == 1.0

@pytest.mark.unit
def test_dice_similarity_logging(logging_fixture):
    """Test if logging works correctly for similarity calculation"""
    # Arrange
    similarity = DiceSimilarity()
    
    # Act
    result = similarity.similarity("a", "a")
    
    # Assert
    assert logging.getLogger(__name__).handlers
    assert any("Calculating Dice similarity between two elements" in record.msg 
               for record in logging_fixture.handlers[0].records)

@pytest.mark.unit
def test_dice_similarity_invalid_input():
    """Test Dice similarity with invalid input types"""
    # Arrange
    similarity = DiceSimilarity()
    
    # Act and Assert
    with pytest.raises(ValueError):
        similarity.similarity(123, "abc")