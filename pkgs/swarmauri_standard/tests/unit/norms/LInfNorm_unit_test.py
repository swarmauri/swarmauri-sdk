import pytest
from typing import Union, Sequence
import numpy as np
import logging

from swarmauri_standard.swarmauri_standard.norms.LInfNorm import LInfNorm

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestLInfNorm:
    """Unit tests for the LInfNorm class implementation."""

    @pytest.fixture
    def norm_instance(self):
        """Fixture providing an instance of LInfNorm."""
        return LInfNorm()

    @pytest.mark.parametrize(
        "x,expected_norm",
        [
            ([1, 2, 3], 3),
            ([-1, -2, -3], 3),
            ([0, 0, 0], 0),
            (lambda x: x**2, 1),
            (lambda x: -x, 1),
        ],
    )
    def test_compute(self, norm_instance, x, expected_norm):
        """Test the compute method with various inputs."""
        logger.info(f"Testing compute method with input type {type(x).__name__}")
        assert norm_instance.compute(x) == expected_norm

    def test_compute_invalid_input(self, norm_instance):
        """Test compute method with invalid input types."""
        logger.info("Testing compute method with invalid input types")
        with pytest.raises(ValueError):
            norm_instance.compute("invalid_type")

    def test_check_non_negativity(self, norm_instance):
        """Test the non-negativity property of the norm."""
        logger.info("Testing non-negativity property")
        test_cases = [[1, 2, 3], [-1, -2, -3], [0, 0, 0], lambda x: x**2, lambda x: -x]

        for x in test_cases:
            norm = norm_instance.compute(x)
            assert norm >= 0, f"Non-negativity failed for input {x}"

    def test_check_triangle_inequality(self, norm_instance):
        """Test the triangle inequality property."""
        logger.info("Testing triangle inequality property")
        x = [1, 2, 3]
        y = [4, 5, 6]

        norm_x = norm_instance.compute(x)
        norm_y = norm_instance.compute(y)
        norm_xy = norm_instance.compute([x[i] + y[i] for i in range(len(x))])

        assert norm_xy <= norm_x + norm_y, "Triangle inequality failed"

    def test_check_absolute_homogeneity(self, norm_instance):
        """Test the absolute homogeneity property."""
        logger.info("Testing absolute homogeneity property")
        x = [1, 2, 3]
        alpha = 2.5

        norm_x = norm_instance.compute(x)
        scaled_x = [alpha * val for val in x]
        norm_scaled = norm_instance.compute(scaled_x)

        assert np.isclose(norm_scaled, abs(alpha) * norm_x), (
            "Absolute homogeneity failed"
        )

    def test_check_definiteness(self, norm_instance):
        """Test the definiteness property."""
        logger.info("Testing definiteness property")
        zero_sequence = [0, 0, 0]
        non_zero_sequence = [1, 2, 3]

        norm_zero = norm_instance.compute(zero_sequence)
        norm_non_zero = norm_instance.compute(non_zero_sequence)

        assert norm_zero == 0, "Definiteness failed for zero input"
        assert norm_non_zero != 0, "Definiteness failed for non-zero input"

    def test_serialization(self, norm_instance):
        """Test JSON serialization and deserialization."""
        logger.info("Testing JSON serialization")
        dumped_json = norm_instance.model_dump_json()
        loaded_json = LInfNorm.model_validate_json(dumped_json)
        assert norm_instance.id == loaded_json.id, (
            "Serialization/Deserialization failed"
        )
