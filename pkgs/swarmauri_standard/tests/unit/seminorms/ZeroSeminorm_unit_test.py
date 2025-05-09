import pytest
from swarmauri_standard.swarmauri_standard.seminorms import ZeroSeminorm
import logging

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestZeroSeminorm:
    """Unit tests for ZeroSeminorm class."""

    @pytest.fixture
    def zero_seminorm_instance(self):
        """Fixture to provide a ZeroSeminorm instance for testing."""
        return ZeroSeminorm()

    @pytest.mark.unit
    def test_compute_string_input(self, zero_seminorm_instance):
        """Test compute method with string input."""
        result = zero_seminorm_instance.compute("test_string")
        assert result == 0.0

    @pytest.mark.unit
    def test_compute_callable_input(self, zero_seminorm_instance):
        """Test compute method with callable input."""
        result = zero_seminorm_instance.compute(lambda x: x)
        assert result == 0.0

    @pytest.mark.unit
    def test_compute_sequence_input(self, zero_seminorm_instance):
        """Test compute method with sequence input."""
        result = zero_seminorm_instance.compute([1, 2, 3])
        assert result == 0.0

    @pytest.mark.unit
    def test_check_triangle_inequality(self, zero_seminorm_instance):
        """Test triangle inequality method."""
        result = zero_seminorm_instance.check_triangle_inequality("a", "b")
        assert result is True

    @pytest.mark.unit
    def test_check_scalar_homogeneity(self, zero_seminorm_instance):
        """Test scalar homogeneity method."""
        result = zero_seminorm_instance.check_scalar_homogeneity("test", 5.0)
        assert result is True

    @pytest.mark.unit
    def test_serialization(self, zero_seminorm_instance):
        """Test serialization/deserialization of ZeroSeminorm."""
        instance = zero_seminorm_instance
        serialized = instance.model_dump_json()
        deserialized = ZeroSeminorm.model_validate_json(serialized)
        assert instance.id == deserialized.id
