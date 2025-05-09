import pytest
import logging
from swarmauri_standard.swarmauri_standard.norms.L1ManhattanNorm import L1ManhattanNorm
from swarmauri_base.norms.NormBase import NormBase

@pytest.mark.unit
class TestL1ManhattanNorm:
    """Unit test class for L1ManhattanNorm implementation."""

    @pytest.fixture
    def norm_instance(self):
        """Fixture providing a fresh instance of L1ManhattanNorm for each test."""
        return L1ManhattanNorm()

    def test_resource_property(self, norm_instance):
        """Test the resource property of the L1ManhattanNorm class."""
        assert norm_instance.resource == "Norm"

    def test_type_property(self, norm_instance):
        """Test the type property of the L1ManhattanNorm class."""
        assert norm_instance.type == "L1ManhattanNorm"

    def test_model_serialization(self, norm_instance):
        """Test model serialization and validation methods."""
        model_json = norm_instance.model_dump_json()
        assert norm_instance.model_validate_json(model_json) == model_json

    @pytest.mark.parametrize("vector,expected_norm", [
        ([1, 2, 3], 6),
        ((-1, 2, -3), 6),
        (lambda: [4, 0, -2], 6)
    ])
    def test_compute_method_valid_inputs(self, norm_instance, vector, expected_norm):
        """Test compute method with valid input vectors of different types."""
        assert norm_instance.compute(vector) == expected_norm

    def test_compute_method_invalid_input(self, norm_instance):
        """Test compute method with an invalid input type."""
        with pytest.raises(ValueError):
            norm_instance.compute(object())

    def test_compute_method_logging(self, norm_instance, caplog):
        """Test if compute method logs correctly."""
        caplog.set_level(logging.DEBUG)
        vector = [1, -2, 3]
        norm_instance.compute(vector)
        assert "Starting L1 norm computation" in caplog.text
        assert f"L1 norm computed successfully: {sum(abs(x) for x in vector)}" in caplog.text

    def test_str_method(self, norm_instance):
        """Test string representation of the L1ManhattanNorm instance."""
        assert str(norm_instance) == "L1ManhattanNorm()"

    def test_repr_method(self, norm_instance):
        """Test official string representation of the L1ManhattanNorm instance."""
        assert repr(norm_instance) == "L1ManhattanNorm()"