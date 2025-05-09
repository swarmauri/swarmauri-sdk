import pytest
from swarmauri_standard.swarmauri_standard.norms.SupremumComplexNorm import (
    SupremumComplexNorm,
)
import logging


@pytest.mark.unit
class TestSupremumComplexNorm:
    """Unit tests for the SupremumComplexNorm class."""

    @pytest.fixture
    def supremum_complex_norm(self):
        """Fixture to provide a SupremumComplexNorm instance."""
        return SupremumComplexNorm()

    @pytest.mark.unit
    def test_type(self, supremum_complex_norm):
        """Test the type property of the SupremumComplexNorm class."""
        assert supremum_complex_norm.type == "SupremumComplexNorm"

    @pytest.mark.unit
    def test_compute(self, supremum_complex_norm):
        """Test the compute method with a simple function."""
        # Test with a simple function
        test_func = lambda t: 2 + t
        result = supremum_complex_norm.compute(test_func)
        assert result >= 2.0 and result <= 3.0

        # Test with invalid input
        with pytest.raises(ValueError):
            supremum_complex_norm.compute("not_a_callable")

    @pytest.mark.unit
    def test_serialization(self, supremum_complex_norm):
        """Test serialization/deserialization of the object."""
        # Serialize the object
        serialized = supremum_complex_norm.model_dump_json()
        # Deserialize the object
        deserialized = SupremumComplexNorm.model_validate_json(serialized)
        # Assert the type matches
        assert supremum_complex_norm.type == deserialized.type

    @pytest.mark.unit
    def test_component_registration(self):
        """Test if the class is properly registered with ComponentBase."""
        # Get the type from registry
        registered_type = SupremumComplexNorm.get_type()
        assert registered_type == "SupremumComplexNorm"
