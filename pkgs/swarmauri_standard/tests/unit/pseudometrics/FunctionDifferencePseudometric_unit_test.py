import pytest
from swarmauri_standard.pseudometrics.FunctionDifferencePseudometric import FunctionDifferencePseudometric
import logging

@pytest.mark.unit
class TestFunctionDifferencePseudometric:
    """Unit tests for FunctionDifferencePseudometric class."""

    def test_resource_type(self):
        """Test the resource type of FunctionDifferencePseudometric."""
        assert FunctionDifferencePseudometric.resource == "Pseudometric"

    def test_type(self):
        """Test the type of FunctionDifferencePseudometric."""
        assert FunctionDifferencePseudometric.type == "FunctionDifferencePseudometric"

    def test_simple_distance(self):
        """Test simple distance calculation between two functions."""
        # Define simple functions
        def f(x: float) -> float:
            return x

        def g(x: float) -> float:
            return x

        # Initialize pseudometric
        pseudometric = FunctionDifferencePseudometric(f, g, evaluation_points=[0, 1, 2])
        
        # Compute distance
        distance = pseudometric.distance(f, g)
        
        # Assert distance is zero since functions are identical
        assert distance == 0.0

    def test_non_zero_distance(self):
        """Test distance calculation between two different functions."""
        # Define simple functions
        def f(x: float) -> float:
            return x

        def g(x: float) -> float:
            return x + 1

        # Initialize pseudometric
        pseudometric = FunctionDifferencePseudometric(f, g, evaluation_points=[0, 1, 2])
        
        # Compute distance
        distance = pseudometric.distance(f, g)
        
        # Assert distance is non-zero
        assert distance > 0.0

    def test_symmetry(self):
        """Test symmetry property of the pseudometric."""
        # Define simple functions
        def f(x: float) -> float:
            return x

        def g(x: float) -> float:
            return x + 1

        # Initialize pseudometric
        pseudometric = FunctionDifferencePseudometric(f, g, evaluation_points=[0, 1, 2])
        
        # Compute distance both ways
        distance_fg = pseudometric.distance(f, g)
        distance_gf = pseudometric.distance(g, f)
        
        # Assert symmetry
        assert distance_fg == distance_gf

    def test_non_negativity(self):
        """Test non-negativity property of the pseudometric."""
        # Define simple functions
        def f(x: float) -> float:
            return x

        def g(x: float) -> float:
            return x + 1

        # Initialize pseudometric
        pseudometric = FunctionDifferencePseudometric(f, g, evaluation_points=[0, 1, 2])
        
        # Compute distance
        distance = pseudometric.distance(f, g)
        
        # Assert non-negativity
        assert distance >= 0.0

    def test_weak_identity(self):
        """Test weak identity property of the pseudometric."""
        # Define functions that are different but have same evaluation points
        def f(x: float) -> float:
            return x

        def g(x: float) -> float:
            return x

        def h(x: float) -> float:
            return x if x < 0 else x + 1

        # Initialize pseudometric
        pseudometric = FunctionDifferencePseudometric(f, g, evaluation_points=[-1, 0, 1])
        
        # Compute distances
        distance_fg = pseudometric.distance(f, g)
        distance_fh = pseudometric.distance(f, h)
        
        # Assert that different functions can have zero distance
        assert distance_fg == 0.0
        assert distance_fh == 0.0

    def test_triangle_inequality(self):
        """Test triangle inequality property of the pseudometric."""
        # Define three different functions
        def f(x: float) -> float:
            return x

        def g(x: float) -> float:
            return x + 1

        def h(x: float) -> float:
            return x + 2

        # Initialize pseudometric
        pseudometric = FunctionDifferencePseudometric(f, g, evaluation_points=[0, 1, 2])
        
        # Compute distances
        distance_fg = pseudometric.distance(f, g)
        distance_gh = pseudometric.distance(g, h)
        distance_fh = pseudometric.distance(f, h)
        
        # Check if triangle inequality holds
        # Note: FunctionDifferencePseudometric does not satisfy triangle inequality
        assert not (distance_fh <= distance_fg + distance_gh)

    def test_serialization(self):
        """Test serialization and deserialization of the pseudometric."""
        # Initialize pseudometric
        pseudometric = FunctionDifferencePseudometric()
        
        # Get class identifier
        class_id = pseudometric.model_dump_json()
        
        # Validate class identifier
        assert class_id == FunctionDifferencePseudometric.type

    def test_logging(self, caplog):
        """Test logging functionality in the pseudometric."""
        # Define simple functions
        def f(x: float) -> float:
            return x

        def g(x: float) -> float:
            return x

        # Initialize pseudometric
        pseudometric = FunctionDifferencePseudometric(f, g, evaluation_points=[0, 1, 2])
        
        # Compute distance
        with caplog.at_level(logging.DEBUG):
            pseudometric.distance(f, g)
            
        # Assert logging occurred
        assert "Computing function difference pseudometric" in caplog.text

    @pytest.fixture
    def simple_functions(self):
        """Fixture providing simple test functions."""
        def f(x: float) -> float:
            return x
        
        def g(x: float) -> float:
            return x + 1
        
        return f, g

    def test_distance_with_fixtures(self, simple_functions):
        """Test distance calculation using fixture-provided functions."""
        f, g = simple_functions
        pseudometric = FunctionDifferencePseudometric(f, g, evaluation_points=[0, 1, 2])
        distance = pseudometric.distance(f, g)
        assert distance > 0.0

    def test_invalid_input(self):
        """Test handling of invalid input types."""
        pseudometric = FunctionDifferencePseudometric()
        
        # Test non-callable input
        with pytest.raises(ValueError):
            pseudometric.distance("not_callable", "also_not_callable")

    def test_empty_evaluation_points(self):
        """Test handling of empty evaluation points."""
        pseudometric = FunctionDifferencePseudometric()
        
        # Test with empty evaluation points
        with pytest.raises(ValueError):
            pseudometric.distance(lambda x: x, lambda x: x + 1)