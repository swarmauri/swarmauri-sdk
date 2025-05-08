import logging
import numpy as np
from typing import List, Set, Union, Literal, TypeVar, Optional
from swarmauri_core.seminorms.ISeminorm import ISeminorm
from swarmauri_base.seminorms.SeminormBase import SeminormBase
from swarmauri_core.ComponentBase import ComponentBase

# Set up logging
logger = logging.getLogger(__name__)

# Type variable for generic typing
T = TypeVar('T')

@ComponentBase.register_type(SeminormBase, "CoordinateProjectionSeminorm")
class CoordinateProjectionSeminorm(SeminormBase):
    """
    Seminorm via projection onto a subset of coordinates.
    
    This class implements a seminorm that ignores certain components of the vector,
    resulting in possible degeneracy. It projects the input vector onto a subspace
    defined by the specified coordinate indices before evaluating the seminorm.
    
    Attributes
    ----------
    type : Literal["CoordinateProjectionSeminorm"]
        The type identifier for this component.
    projection_indices : Set[int]
        The set of indices to project onto. Only these components will be considered
        when evaluating the seminorm.
    """
    
    type: Literal["CoordinateProjectionSeminorm"] = "CoordinateProjectionSeminorm"
    projection_indices: Set[int]
    
    def __init__(self, projection_indices: Union[List[int], Set[int]]):
        """
        Initialize the CoordinateProjectionSeminorm.
        
        Parameters
        ----------
        projection_indices : Union[List[int], Set[int]]
            The indices of the coordinates to project onto. These are the only
            coordinates that will be considered when evaluating the seminorm.
        """
        super().__init__()
        self.projection_indices = set(projection_indices)
        logger.info(f"Initialized CoordinateProjectionSeminorm with projection indices: {self.projection_indices}")
    
    def _project(self, x: np.ndarray) -> np.ndarray:
        """
        Project the input vector onto the subspace defined by projection_indices.
        
        Parameters
        ----------
        x : np.ndarray
            The input vector to project.
            
        Returns
        -------
        np.ndarray
            The projected vector, with zeros in the positions not in projection_indices.
        """
        # Create a copy to avoid modifying the original
        projected = np.zeros_like(x)
        
        # Only keep the components specified in projection_indices
        for idx in self.projection_indices:
            if idx < len(x):
                projected[idx] = x[idx]
        
        return projected
    
    def evaluate(self, x: np.ndarray) -> float:
        """
        Evaluate the seminorm for a given input by projecting it onto the specified coordinates.
        
        Parameters
        ----------
        x : np.ndarray
            The input vector to evaluate the seminorm on.
            
        Returns
        -------
        float
            The seminorm value, which is the Euclidean norm of the projected vector.
        """
        logger.debug(f"Evaluating CoordinateProjectionSeminorm on vector of shape {x.shape}")
        
        # Project the vector onto the specified coordinates
        projected = self._project(x)
        
        # Compute the Euclidean norm of the projected vector
        norm_value = np.linalg.norm(projected)
        
        logger.debug(f"CoordinateProjectionSeminorm evaluated to {norm_value}")
        return float(norm_value)
    
    def scale(self, x: np.ndarray, alpha: float) -> float:
        """
        Evaluate the seminorm of a scaled input.
        
        This method satisfies scalar homogeneity: p(αx) = |α|p(x)
        
        Parameters
        ----------
        x : np.ndarray
            The input vector to evaluate the seminorm on.
        alpha : float
            The scaling factor.
            
        Returns
        -------
        float
            The seminorm value of the scaled input.
        """
        logger.debug(f"Scaling vector by {alpha} before evaluating CoordinateProjectionSeminorm")
        
        # Scale the vector
        scaled_x = alpha * x
        
        # Evaluate the seminorm on the scaled vector
        return self.evaluate(scaled_x)
    
    def triangle_inequality(self, x: np.ndarray, y: np.ndarray) -> bool:
        """
        Verify that the triangle inequality holds for the given inputs.
        
        This method checks if p(x + y) <= p(x) + p(y).
        
        Parameters
        ----------
        x : np.ndarray
            First input vector.
        y : np.ndarray
            Second input vector.
            
        Returns
        -------
        bool
            True if the triangle inequality holds, False otherwise.
        """
        logger.debug("Checking triangle inequality for CoordinateProjectionSeminorm")
        
        # Compute p(x + y)
        sum_norm = self.evaluate(x + y)
        
        # Compute p(x) + p(y)
        x_norm = self.evaluate(x)
        y_norm = self.evaluate(y)
        sum_of_norms = x_norm + y_norm
        
        # Check if p(x + y) <= p(x) + p(y)
        result = sum_norm <= sum_of_norms + 1e-10  # Adding small tolerance for numerical stability
        
        logger.debug(f"Triangle inequality check: {sum_norm} <= {sum_of_norms}: {result}")
        return result
    
    def is_zero(self, x: np.ndarray, tolerance: float = 1e-10) -> bool:
        """
        Check if the seminorm evaluates to zero (within a tolerance).
        
        Parameters
        ----------
        x : np.ndarray
            The input vector to check.
        tolerance : float, optional
            The numerical tolerance for considering a value as zero.
            
        Returns
        -------
        bool
            True if the seminorm of x is zero (within tolerance), False otherwise.
        """
        logger.debug(f"Checking if CoordinateProjectionSeminorm is zero with tolerance {tolerance}")
        
        # Compute the seminorm
        norm_value = self.evaluate(x)
        
        # Check if it's close to zero
        result = norm_value < tolerance
        
        logger.debug(f"Is zero check: {norm_value} < {tolerance}: {result}")
        return result
    
    def is_definite(self) -> bool:
        """
        Check if this seminorm is actually a norm (i.e., it has the definiteness property).
        
        A seminorm is definite if p(x) = 0 implies x = 0. For a coordinate projection
        seminorm, this is true if and only if all coordinates are included in the projection.
        
        Returns
        -------
        bool
            True if the seminorm is definite (and thus a norm), False otherwise.
        """
        logger.debug("Checking if CoordinateProjectionSeminorm is definite")
        
        # This seminorm is definite if and only if all coordinates are included
        # Since we don't know the dimension of the space, we can't determine this
        # in the general case. However, if projection_indices is empty, it's definitely
        # not definite.
        
        if not self.projection_indices:
            logger.debug("CoordinateProjectionSeminorm is not definite (empty projection indices)")
            return False
        
        # In practice, this would require knowledge of the space dimension
        # For now, we'll return False unless explicitly instructed otherwise
        logger.debug("CoordinateProjectionSeminorm might be definite depending on the space dimension")
        return False