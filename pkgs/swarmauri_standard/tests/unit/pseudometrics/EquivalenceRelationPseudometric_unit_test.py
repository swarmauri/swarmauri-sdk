import pytest
from swarmauri_standard.swarmauri_standard.pseudometrics.EquivalenceRelationPseudometric import EquivalenceRelationPseudometric
import logging

logger = logging.getLogger(__name__)

@pytest.mark.unit
class TestEquivalenceRelationPseudometric:
    """Unit test class for EquivalenceRelationPseudometric class."""
    
    def test_resource(self):
        """Test the resource property."""
        assert EquivalenceRelationPseudometric.resource == "Pseudometric"
        
    def test_type(self):
        """Test the type property."""
        assert EquivalenceRelationPseudometric.type == "EquivalenceRelationPseudometric"
        
    def test_serialization(self):
        """Test serialization and deserialization."""
        er_pseudo = EquivalenceRelationPseudometric()
        assert er_pseudo.model_dump_json() is not None
        assert EquivalenceRelationPseudometric.model_validate_json(er_pseudo.model_dump_json()) == er_pseudo.id
        
    def test_distance(self):
        """Test the distance method with various inputs."""
        er_pseudo = EquivalenceRelationPseudometric()
        
        # Test with equivalent elements
        assert er_pseudo.distance("test", "test") == 0.0
        assert er_pseudo.distance(1, 1) == 0.0
        assert er_pseudo.distance([1, 2], [1, 2]) == 0.0
        
        # Test with non-equivalent elements
        assert er_pseudo.distance("test", "different") == 1.0
        assert er_pseudo.distance(1, 2) == 1.0
        assert er_pseudo.distance([1, 2], [2, 3]) == 1.0
        
    def test_distances(self):
        """Test the distances method with sequences."""
        er_pseudo = EquivalenceRelationPseudometric()
        
        xs = ["a", "b", 1, [1, 2]]
        ys = ["a", "b", 2, [1, 3]]
        
        distances = er_pseudo.distances(xs, ys)
        assert len(distances) == 4
        assert distances == [0.0, 0.0, 1.0, 1.0]
        
    def test_equivalence_function(self):
        """Test the equivalence function behavior."""
        er_pseudo = EquivalenceRelationPseudometric()
        
        # Test default equivalence function
        assert er_pseudo.equivalence_function("a", "a")
        assert not er_pseudo.equivalence_function("a", "b")
        
        # Test custom equivalence function
        def custom_eq(x, y):
            return x == y.upper()
            
        er_custom = EquivalenceRelationPseudometric(equivalence_function=custom_eq)
        assert er_custom.equivalence_function("a", "A")
        assert not er_custom.equivalence_function("a", "B")
        
    def test_default_equivalence(self):
        """Test the default equivalence function."""
        er_pseudo = EquivalenceRelationPseudometric()
        assert er_pseudo._default_equivalence("test", "test")
        assert not er_pseudo._default_equivalence("test", "different")
        assert er_pseudo._default_equivalence(1, 1)
        assert not er_pseudo._default_equivalence(1, 2)
        assert er_pseudo._default_equivalence([1, 2], [1, 2])
        assert not er_pseudo._default_equivalence([1, 2], [2, 3])
        
    def test_logging(self):
        """Test logging functionality."""
        er_pseudo = EquivalenceRelationPseudometric()
        assert er_pseudo.logger is not None
        er_pseudo.logger.debug("Test debug message")
        er_pseudo.logger.info("Test info message")
        er_pseudo.logger.warning("Test warning message")
        er_pseudo.logger.error("Test error message")
        er_pseudo.logger.critical("Test critical message")