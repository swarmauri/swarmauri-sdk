from typing import List, Tuple, Literal, Optional, Union
import logging
import numpy as np
from swarmauri_base.pseudometrics.PseudometricBase import PseudometricBase
from swarmauri_base.ComponentBase import ComponentBase

logger = logging.getLogger(__name__)

@ComponentBase.register_type(PseudometricBase, "ProjectionPseudometricR2")
class ProjectionPseudometricR2(PseudometricBase):
    """
    Implements a pseudometric based on projection in R2 space.
    
    This pseudometric projects points onto a selected coordinate axis (x or y)
    and measures the distance along that axis only, ignoring the other dimension.
    
    This satisfies the pseudometric properties:
    - Non-negativity: d(x,y) ≥ 0
    - Symmetry: d(x,y) = d(y,x)
    - Triangle inequality: d(x,z) ≤ d(x,y) + d(y,z)
    
    But it does not satisfy the identity of indiscernibles (d(x,y)=0 iff x=y),
    making it a pseudometric rather than a metric. Points with the same projected
    coordinate will have zero distance regardless of their other coordinate.
    """
    
    type: Literal["ProjectionPseudometricR2"] = "ProjectionPseudometricR2"
    
    def __init__(self, projection_axis: int = 0, **kwargs):
        """
        Initialize the projection pseudometric.
        
        Args:
            projection_axis: The axis to project onto (0 for x-axis, 1 for y-axis)
            **kwargs: Additional keyword arguments to pass to parent classes
        
        Raises:
            ValueError: If projection_axis is not 0 or 1
        """
        super().__init__(**kwargs)
        
        if projection_axis not in [0, 1]:
            logger.error(f"Invalid projection_axis: {projection_axis}. Must be 0 (x-axis) or 1 (y-axis).")
            raise ValueError(f"projection_axis must be 0 (x-axis) or 1 (y-axis), got {projection_axis}")
        
        self.projection_axis = projection_axis
        logger.debug(f"Initialized {self.__class__.__name__} with projection on {'x' if projection_axis == 0 else 'y'}-axis")
    
    def _validate_point(self, point: Union[List, Tuple, np.ndarray]) -> np.ndarray:
        """
        Validate and convert a point to a numpy array.
        
        Args:
            point: A point in R2 as a list, tuple, or numpy array
            
        Returns:
            The point as a numpy array
            
        Raises:
            ValueError: If the point is not 2-dimensional
        """
        point_array = np.asarray(point)
        if point_array.shape != (2,):
            logger.error(f"Invalid point: {point}. Must be a 2D point.")
            raise ValueError(f"Points must be 2-dimensional, got shape {point_array.shape}")
        return point_array
    
    def distance(self, x: Union[List, Tuple, np.ndarray], y: Union[List, Tuple, np.ndarray]) -> float:
        """
        Calculate the pseudometric distance between two points in R2 using projection.
        
        Args:
            x: First point in R2
            y: Second point in R2
            
        Returns:
            The absolute difference between the projected coordinates
            
        Raises:
            ValueError: If inputs are not 2D points
        """
        # Validate and convert points
        x_array = self._validate_point(x)
        y_array = self._validate_point(y)
        
        # Calculate the distance along the projection axis
        distance = abs(x_array[self.projection_axis] - y_array[self.projection_axis])
        
        # Validate non-negativity (should always be true due to abs function)
        self._validate_non_negativity(distance, x, y)
        
        logger.debug(f"Distance between {x} and {y} along {'x' if self.projection_axis == 0 else 'y'}-axis: {distance}")
        return distance
    
    def batch_distance(self, xs: List[Union[List, Tuple, np.ndarray]], 
                      ys: List[Union[List, Tuple, np.ndarray]]) -> List[float]:
        """
        Calculate distances between corresponding pairs of points from two lists.
        
        Args:
            xs: List of first points in R2
            ys: List of second points in R2
            
        Returns:
            List of distances between corresponding points
            
        Raises:
            ValueError: If input lists have different lengths or points are not 2D
        """
        if len(xs) != len(ys):
            logger.error(f"Input lists have different lengths: {len(xs)} vs {len(ys)}")
            raise ValueError(f"Input lists must have the same length, got {len(xs)} and {len(ys)}")
        
        distances = []
        for i, (x, y) in enumerate(zip(xs, ys)):
            try:
                distances.append(self.distance(x, y))
            except ValueError as e:
                logger.error(f"Error calculating distance for pair at index {i}: {e}")
                raise
        
        return distances
    
    def pairwise_distances(self, points: List[Union[List, Tuple, np.ndarray]]) -> List[List[float]]:
        """
        Calculate all pairwise distances between points in the given list.
        
        Args:
            points: List of points in R2
            
        Returns:
            A square matrix (as list of lists) where element [i][j] 
            contains the distance between points[i] and points[j]
            
        Raises:
            ValueError: If points are not 2D
        """
        n = len(points)
        # Pre-validate all points
        validated_points = [self._validate_point(p) for p in points]
        
        # Initialize the distance matrix
        distance_matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        
        # Calculate distances
        for i in range(n):
            for j in range(i+1, n):  # Only calculate upper triangle (due to symmetry)
                dist = abs(validated_points[i][self.projection_axis] - 
                          validated_points[j][self.projection_axis])
                # Store distance in both positions (symmetry)
                distance_matrix[i][j] = dist
                distance_matrix[j][i] = dist
        
        # Check a sample of triangle inequalities (for debugging/validation)
        if n >= 3:
            # Sample a few triplets to check triangle inequality
            for _ in range(min(5, n)):
                i, j, k = np.random.choice(n, 3, replace=False)
                self._validate_triangle_inequality(
                    distance_matrix[i][k], 
                    distance_matrix[i][j], 
                    distance_matrix[j][k],
                    points[i], points[j], points[k]
                )
        
        logger.debug(f"Calculated pairwise distances for {n} points")
        return distance_matrix
    
    def get_projection_axis_name(self) -> str:
        """
        Get the name of the currently used projection axis.
        
        Returns:
            String indicating which axis is being used ('x' or 'y')
        """
        return 'x' if self.projection_axis == 0 else 'y'
    
    def set_projection_axis(self, axis: int) -> None:
        """
        Change the projection axis.
        
        Args:
            axis: The axis to project onto (0 for x-axis, 1 for y-axis)
            
        Raises:
            ValueError: If axis is not 0 or 1
        """
        if axis not in [0, 1]:
            logger.error(f"Invalid projection_axis: {axis}. Must be 0 (x-axis) or 1 (y-axis).")
            raise ValueError(f"projection_axis must be 0 (x-axis) or 1 (y-axis), got {axis}")
        
        self.projection_axis = axis
        logger.info(f"Changed projection axis to {'x' if axis == 0 else 'y'}-axis")