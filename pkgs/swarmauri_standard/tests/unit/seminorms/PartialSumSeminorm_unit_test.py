import pytest
from swarmauri_standard.swarmauri_standard.seminorms.PartialSumSeminorm import PartialSumSeminorm
import logging

logger = logging.getLogger(__name__)

@pytest.fixture
def partialsumseminorm():
    return PartialSumSeminorm(start=0, end=2, indices=[0, 2])

@pytest.mark.unit
def test_type():
    """Test that the type attribute is correctly set."""
    assert PartialSumSeminorm.type == "PartialSumSeminorm"

@pytest.mark.unit
def test_resource():
    """Test that the resource attribute is correctly set."""
    assert PartialSumSeminorm.resource == "Seminorm"

@pytest.mark.unit
def test_compute_vector(partialsumseminorm):
    """Test computation with a vector input."""
    vector = [1, 2, 3, 4]
    result = partialsumseminorm.compute(vector)
    assert result == 3  # Sum of [1, 2]

@pytest.mark.unit
def test_compute_sequence():
    """Test computation with a sequence input."""
    sequence = (1, 2, 3, 4)
    partialsumseminorm = PartialSumSeminorm(start=0, end=2)
    result = partialsumseminorm.compute(sequence)
    assert result == 3  # Sum of [1, 2]

@pytest.mark.unit
def test_compute_indices():
    """Test computation with specified indices."""
    vector = [1, 2, 3, 4]
    partialsumseminorm = PartialSumSeminorm(indices=[0, 2])
    result = partialsumseminorm.compute(vector)
    assert result == 4  # Sum of [1, 3]

@pytest.mark.unit
def test_compute_empty_vector():
    """Test computation with an empty vector."""
    vector = []
    partialsumseminorm = PartialSumSeminorm(start=0, end=0)
    result = partialsumseminorm.compute(vector)
    assert result == 0

@pytest.mark.unit
def test_compute_out_of_bounds():
    """Test computation with start index beyond vector length."""
    vector = [1, 2, 3]
    partialsumseminorm = PartialSumSeminorm(start=4, end=5)
    with pytest.raises(ValueError):
        partialsumseminorm.compute(vector)

@pytest.mark.unit
def test_compute_invalid_input():
    """Test computation with an invalid input type."""
    invalid_input = {"a": 1, "b": 2}
    partialsumseminorm = PartialSumSeminorm()
    with pytest.raises(ValueError):
        partialsumseminorm.compute(invalid_input)

@pytest.mark.unit
def test_serialization():
    """Test the serialization and validation of the model."""
    partialsumseminorm = PartialSumSeminorm()
    model_json = partialsumseminorm.model_dump_json()
    assert partialsumseminorm.model_validate_json(model_json) == model_json

@pytest.mark.unit
def test_init_validation():
    """Test that __init__ validates input parameters correctly."""
    with pytest.raises(ValueError):
        PartialSumSeminorm(start=0, end=2, indices=[0, 2])
    
    with pytest.raises(ValueError):
        PartialSumSeminorm()