import pytest
import logging
from swarmauri_standard.norms.L1ManhattanNorm import L1ManhattanNorm

@pytest.mark.unit
class TestL1ManhattanNorm:
    """Unit tests for the L1ManhattanNorm class."""
    
    @pytest.mark.unit
    def test_type(self):
        """Test that the type attribute is correctly set."""
        assert L1ManhattanNorm.type == "L1ManhattanNorm"
        
    @pytest.mark.unit
    @pytest.parametrize("vector,expected_norm", [
        ([1, 2, 3], 6.0),
        ((-1, 2.5, 3.0), 6.5),
        ("123", 6.0),  # Treats string as an iterable of characters
        ([], 0.0),  # Empty vector
        ([-1.0, -2.0, -3.0], 6.0)  # All negative values
    ])
    def test_compute_valid_inputs(self, vector, expected_norm):
        """Test compute method with valid input vectors."""
        norm = L1ManhattanNorm()
        result = norm.compute(vector)
        assert result == expected_norm
        
    @pytest.mark.unit
    def test_compute_invalid_input(self):
        """Test compute method with invalid input types."""
        norm = L1ManhattanNorm()
        with pytest.raises(TypeError):
            norm.compute({"invalid": "input"})  # Non-iterable input
    
    @pytest.mark.unit
    def test_logging_debug_message(self, caplog):
        """Test that debug messages are logged during computation."""
        caplog.set_level(logging.DEBUG)
        norm = L1ManhattanNorm()
        norm.compute([1, 2, 3])
        assert "Computing L1 Manhattan norm" in caplog.text
        assert "L1 norm computed as 6.0" in caplog.text
        
    @pytest.mark.unit
    def test_logging_error_message(self, caplog):
        """Test that error messages are logged for invalid inputs."""
        caplog.set_level(logging.ERROR)
        norm = L1ManhattanNorm()
        with pytest.raises(TypeError):
            norm.compute({"invalid": "input"})
        assert "Failed to compute L1 norm" in caplog.text