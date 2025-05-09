import pytest
from swarmauri_standard.swarmauri_standard.seminorms.PointEvaluationSeminorm import (
    PointEvaluationSeminorm,
)
from typing import Union, Sequence, Callable
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix


@pytest.mark.unit
class TestPointEvaluationSeminorm:
    """Unit tests for the PointEvaluationSeminorm class."""

    def test_initialization(self):
        """Test the initialization of PointEvaluationSeminorm with and without point."""
        pes = PointEvaluationSeminorm()
        assert pes.point == 0.0

        custom_point = 5.0
        pes_custom = PointEvaluationSeminorm(point=custom_point)
        assert pes_custom.point == custom_point

    def test_compute_vector(self):
        """Test compute method with vector input."""
        input_vector = [1, 2, 3]
        point = 1
        pes = PointEvaluationSeminorm(point=point)
        result = pes.compute(input_vector)
        assert result == input_vector[point]

    def test_compute_matrix(self):
        """Test compute method with matrix input."""
        input_matrix = IMatrix()  # Assuming IMatrix has some implementation
        pes = PointEvaluationSeminorm()
        with pytest.raises(NotImplementedError):
            pes.compute(input_matrix)

    def test_compute_sequence(self):
        """Test compute method with sequence input."""
        input_seq = (10, 20, 30)
        point = 2
        pes = PointEvaluationSeminorm(point=point)
        result = pes.compute(input_seq)
        assert result == input_seq[point]

    def test_compute_string(self):
        """Test compute method with string input."""
        input_str = "test"
        point = 2
        pes = PointEvaluationSeminorm(point=point)
        result = pes.compute(input_str)
        assert result == input_str[point]

    def test_compute_callable(self):
        """Test compute method with callable input."""

        def func(x):
            return x * 2

        point = 5.0
        pes = PointEvaluationSeminorm(point=point)
        result = pes.compute(func)
        assert result == func(point)

    def test_check_triangle_inequality(self):
        """Test the triangle inequality check."""
        pes = PointEvaluationSeminorm()
        a = [1, 2, 3]
        b = [4, 5, 6]
        assert pes.check_triangle_inequality(a, b) is True

    def test_check_scalar_homogeneity(self):
        """Test the scalar homogeneity check."""
        pes = PointEvaluationSeminorm()
        input = [1, 2, 3]
        scalar = 2.0
        assert pes.check_scalar_homogeneity(input, scalar) is True

    def test_serialization(self):
        """Test the model serialization and deserialization."""
        pes = PointEvaluationSeminorm(point=10.0)
        model_dump = pes.model_dump_json()
        model_load = pes.model_validate_json(model_dump)
        assert pes.id == model_load.id

    def test_error_handling_point_out_of_bounds(self):
        """Test error handling for point out of bounds."""
        pes = PointEvaluationSeminorm(point=5)
        input = [1, 2]
        with pytest.raises(IndexError):
            pes.compute(input)

    def test_error_handling_unsupported_type(self):
        """Test error handling for unsupported input type."""
        pes = PointEvaluationSeminorm()
        input = dict()
        with pytest.raises(ValueError):
            pes.compute(input)
