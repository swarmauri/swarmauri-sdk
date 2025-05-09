import pytest
import logging
from swarmauri_standard.swarmauri_standard.pseudometrics.FunctionDifferencePseudometric import (
    FunctionDifferencePseudometric,
)
from typing import Union, List, Tuple, Callable


@pytest.mark.unit
class TestFunctionDifferencePseudometric(PseudometricBase_tests):
    """Unit test class for FunctionDifferencePseudometric class."""

    @pytest.fixture
    def fixture_function_difference(self):
        """Fixture to provide a FunctionDifferencePseudometric instance."""
        return FunctionDifferencePseudometric()

    @pytest.mark.parametrize(
        "points,num_sample_points,random_seed",
        [(None, 1000, None), ([1.0, 2.0, 3.0], 0, 42)],
    )
    def test_constructor(self, points, num_sample_points, random_seed):
        """Test the initialization of FunctionDifferencePseudometric."""
        fdp = FunctionDifferencePseudometric(
            points=points, num_sample_points=num_sample_points, random_seed=random_seed
        )

        if points is None:
            assert len(fdp.points) == num_sample_points
        else:
            assert fdp.points == points
        assert fdp.num_sample_points == num_sample_points
        assert fdp.random_seed == random_seed

    def test_distance(self, fixture_function_difference):
        """Test the distance method with simple functions."""
        f = lambda x: x
        g = lambda x: -x

        distance = fixture_function_difference.distance(f, g)
        assert distance >= 0.0
        assert distance == pytest.approx(1.0, abs=1e-2)

    def test_distances(self, fixture_function_difference):
        """Test the distances method with multiple functions."""
        f = lambda x: x
        g1 = lambda x: -x
        g2 = lambda x: x + 1

        distances = fixture_function_difference.distances(f, [g1, g2])
        assert isinstance(distances, list)
        assert len(distances) == 2
        assert all(isinstance(d, float) for d in distances)

    def test_check_non_negativity(self, fixture_function_difference):
        """Test the non-negativity property."""
        f = lambda x: x
        g = lambda x: x

        assert fixture_function_difference.check_non_negativity(f, g)
        assert fixture_function_difference.check_non_negativity(f, lambda x: -x)

    def test_check_symmetry(self, fixture_function_difference):
        """Test the symmetry property."""
        f = lambda x: x
        g = lambda x: x + 1
        h = lambda x: x - 1

        assert fixture_function_difference.check_symmetry(f, g)
        assert fixture_function_difference.check_symmetry(g, h)

    def test_check_triangle_inequality(self, fixture_function_difference):
        """Test the triangle inequality property."""
        f = lambda x: x
        g = lambda x: x + 1
        h = lambda x: x + 2

        d_fg = fixture_function_difference.distance(f, g)
        d_gh = fixture_function_difference.distance(g, h)
        d_fh = fixture_function_difference.distance(f, h)

        assert d_fh <= d_fg + d_gh

    def test_check_weak_identity(self, fixture_function_difference):
        """Test the weak identity of indiscernibles property."""
        f = lambda x: x
        g = lambda x: x

        assert fixture_function_difference.check_weak_identity(f, g)
        assert not fixture_function_difference.check_weak_identity(f, lambda x: x + 1)

    def test_serialization(self, fixture_function_difference):
        """Test JSON serialization and validation."""
        model_json = fixture_function_difference.model_dump_json()
        assert model_json == fixture_function_difference.model_validate_json(model_json)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    pytest.main([__file__])
