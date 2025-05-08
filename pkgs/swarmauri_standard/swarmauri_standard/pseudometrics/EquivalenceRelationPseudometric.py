from typing import Any, List, Callable, TypeVar, Generic, Literal, Optional
import logging
from swarmauri_base.pseudometrics.PseudometricBase import PseudometricBase
from swarmauri_base.ComponentBase import ComponentBase

T = TypeVar('T')
logger = logging.getLogger(__name__)

@ComponentBase.register_type(PseudometricBase, "EquivalenceRelationPseudometric")
class EquivalenceRelationPseudometric(PseudometricBase, Generic[T]):
    """
    Pseudometric based on equivalence relations.
    
    This pseudometric defines distance via equivalence classes. Points in the same
    equivalence class have zero distance, while points in different classes have
    distance 1. This effectively creates a quotient space.
    
    The equivalence relation must satisfy:
    - Reflexivity: x ~ x for all x
    - Symmetry: if x ~ y then y ~ x
    - Transitivity: if x ~ y and y ~ z then x ~ z
    """
    
    type: Literal["EquivalenceRelationPseudometric"] = "EquivalenceRelationPseudometric"
    
    def __init__(self, equivalence_function: Callable[[T, T], bool], **kwargs):
        """
        Initialize the equivalence relation pseudometric.
        
        Args:
            equivalence_function: A function that takes two elements and returns True
                                 if they are equivalent, False otherwise. Must satisfy
                                 reflexivity, symmetry, and transitivity.
            **kwargs: Additional keyword arguments to pass to parent classes
        """
        super().__init__(**kwargs)
        self.equivalence_function = equivalence_function
        logger.debug(f"Initialized {self.__class__.__name__} with custom equivalence function")
    
    def distance(self, x: T, y: T) -> float:
        """
        Calculate the pseudometric distance between two points.
        
        Returns 0 if the points are equivalent under the defined equivalence relation,
        and 1 otherwise.
        
        Args:
            x: First point
            y: Second point
            
        Returns:
            0.0 if the points are equivalent, 1.0 otherwise
        """
        # Check if points are equivalent
        if self.equivalence_function(x, y):
            return 0.0
        else:
            return 1.0
    
    def batch_distance(self, xs: List[T], ys: List[T]) -> List[float]:
        """
        Calculate distances between corresponding pairs of points from two lists.
        
        Args:
            xs: List of first points
            ys: List of second points
            
        Returns:
            List of distances between corresponding points
            
        Raises:
            ValueError: If input lists have different lengths
        """
        if len(xs) != len(ys):
            error_msg = f"Input lists must have the same length, got {len(xs)} and {len(ys)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Calculate distances for each pair
        distances = []
        for i in range(len(xs)):
            distances.append(self.distance(xs[i], ys[i]))
        
        return distances
    
    def pairwise_distances(self, points: List[T]) -> List[List[float]]:
        """
        Calculate all pairwise distances between points in the given list.
        
        Args:
            points: List of points
            
        Returns:
            A square matrix (as list of lists) where element [i][j] 
            contains the distance between points[i] and points[j]
        """
        n = len(points)
        
        # Initialize distance matrix with zeros
        distance_matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        
        # Fill the distance matrix
        for i in range(n):
            for j in range(i+1, n):  # Only compute upper triangle
                dist = self.distance(points[i], points[j])
                # Store distance symmetrically
                distance_matrix[i][j] = dist
                distance_matrix[j][i] = dist  # Ensure symmetry
        
        return distance_matrix
    
    def validate_equivalence_properties(self, sample_points: List[T]) -> bool:
        """
        Validate that the equivalence function satisfies the required properties.
        
        Tests reflexivity, symmetry, and transitivity on the provided sample points.
        
        Args:
            sample_points: A list of points to test the properties on
            
        Returns:
            True if all properties are satisfied, False otherwise
            
        Note:
            This validation is not exhaustive and depends on the sample points provided.
        """
        n = len(sample_points)
        
        # Check reflexivity: x ~ x for all x
        for x in sample_points:
            if not self.equivalence_function(x, x):
                logger.error(f"Reflexivity violation: {x} is not equivalent to itself")
                return False
        
        # Check symmetry: if x ~ y then y ~ x
        for i in range(n):
            for j in range(n):
                x, y = sample_points[i], sample_points[j]
                if self.equivalence_function(x, y) != self.equivalence_function(y, x):
                    logger.error(f"Symmetry violation: {x} ~ {y} but not {y} ~ {x}")
                    return False
        
        # Check transitivity: if x ~ y and y ~ z then x ~ z
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    x, y, z = sample_points[i], sample_points[j], sample_points[k]
                    if (self.equivalence_function(x, y) and 
                        self.equivalence_function(y, z) and 
                        not self.equivalence_function(x, z)):
                        logger.error(f"Transitivity violation: {x} ~ {y} and {y} ~ {z} but not {x} ~ {z}")
                        return False
        
        logger.info("Equivalence relation properties validated successfully")
        return True