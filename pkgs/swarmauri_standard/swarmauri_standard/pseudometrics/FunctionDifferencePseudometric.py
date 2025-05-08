from typing import Callable, List, Optional, Sequence, Tuple, Literal, Union, Any
import logging
import numpy as np
from functools import lru_cache
import random
from swarmauri_base.pseudometrics.PseudometricBase import PseudometricBase
from swarmauri_base.ComponentBase import ComponentBase

logger = logging.getLogger(__name__)

Function = Callable[[Any], Any]


@ComponentBase.register_type(PseudometricBase, "FunctionDifferencePseudometric")
class FunctionDifferencePseudometric(PseudometricBase):
    """
    Measures the distance between two functions based on their output differences
    at specific evaluation points.
    
    This pseudometric computes the distance between functions by evaluating them
    at a set of sample points and measuring the differences in their outputs.
    The functions must be defined on the same domain.
    
    Attributes:
        type: The type identifier for this pseudometric
        evaluation_points: Fixed points at which to evaluate the functions
        sampling_strategy: Strategy for generating evaluation points if not provided
        norm_type: Type of norm to use for computing differences (1, 2, or 'inf')
        sample_size: Number of points to sample when using a sampling strategy
        domain_bounds: Bounds of the domain for sampling (min, max)
        seed: Random seed for reproducible sampling
    """
    
    type: Literal["FunctionDifferencePseudometric"] = "FunctionDifferencePseudometric"
    
    def __init__(
        self,
        evaluation_points: Optional[Sequence[Any]] = None,
        sampling_strategy: Literal["random", "uniform", "custom"] = "uniform",
        norm_type: Union[int, Literal["inf"]] = 2,
        sample_size: int = 100,
        domain_bounds: Optional[Tuple[float, float]] = None,
        custom_sampler: Optional[Callable[[], Sequence[Any]]] = None,
        seed: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize the function difference pseudometric.
        
        Args:
            evaluation_points: Specific points at which to evaluate the functions.
                If None, points will be generated according to sampling_strategy.
            sampling_strategy: Method to generate evaluation points if none provided:
                - "random": Random sampling from domain
                - "uniform": Uniformly spaced points across domain
                - "custom": Use custom_sampler function
            norm_type: Type of norm to use for computing differences:
                - 1: L1 norm (sum of absolute differences)
                - 2: L2 norm (Euclidean distance)
                - "inf": Maximum absolute difference
            sample_size: Number of points to sample when using a sampling strategy
            domain_bounds: Tuple of (min, max) defining the domain bounds for sampling
            custom_sampler: Function that returns sequence of evaluation points
            seed: Random seed for reproducible sampling
            **kwargs: Additional keyword arguments to pass to parent classes
        
        Raises:
            ValueError: If invalid parameters are provided
        """
        super().__init__(**kwargs)
        
        # Set random seed if provided
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        self.norm_type = norm_type
        self.sample_size = sample_size
        self.sampling_strategy = sampling_strategy
        self.domain_bounds = domain_bounds or (0, 1)
        self.custom_sampler = custom_sampler
        
        # If evaluation points are provided, use them directly
        if evaluation_points is not None:
            self.evaluation_points = tuple(evaluation_points)
            logger.info(f"Using {len(self.evaluation_points)} provided evaluation points")
        else:
            # Generate evaluation points based on sampling strategy
            self.evaluation_points = self._generate_evaluation_points()
            logger.info(f"Generated {len(self.evaluation_points)} evaluation points using {sampling_strategy} strategy")
    
    def _generate_evaluation_points(self) -> Tuple[Any, ...]:
        """
        Generate evaluation points based on the specified sampling strategy.
        
        Returns:
            A tuple of evaluation points
            
        Raises:
            ValueError: If the sampling strategy is invalid or required parameters are missing
        """
        if self.sampling_strategy == "random":
            if self.domain_bounds is None:
                raise ValueError("Domain bounds must be specified for random sampling")
            min_val, max_val = self.domain_bounds
            points = np.random.uniform(min_val, max_val, self.sample_size)
            return tuple(points)
            
        elif self.sampling_strategy == "uniform":
            if self.domain_bounds is None:
                raise ValueError("Domain bounds must be specified for uniform sampling")
            min_val, max_val = self.domain_bounds
            points = np.linspace(min_val, max_val, self.sample_size)
            return tuple(points)
            
        elif self.sampling_strategy == "custom":
            if self.custom_sampler is None:
                raise ValueError("Custom sampler function must be provided for custom sampling strategy")
            return tuple(self.custom_sampler())
            
        else:
            raise ValueError(f"Unknown sampling strategy: {self.sampling_strategy}")
    
    @lru_cache(maxsize=128)
    def _evaluate_function(self, func: Function) -> np.ndarray:
        """
        Evaluate a function at all evaluation points and cache the result.
        
        Args:
            func: The function to evaluate
            
        Returns:
            Array of function values at evaluation points
            
        Raises:
            ValueError: If the function cannot be evaluated at the points
        """
        try:
            results = np.array([func(point) for point in self.evaluation_points])
            return results
        except Exception as e:
            logger.error(f"Error evaluating function: {e}")
            raise ValueError(f"Failed to evaluate function at evaluation points: {e}")
    
    def _compute_norm(self, differences: np.ndarray) -> float:
        """
        Compute the norm of the differences array based on the specified norm type.
        
        Args:
            differences: Array of differences between function outputs
            
        Returns:
            The computed norm value
            
        Raises:
            ValueError: If the norm type is invalid
        """
        if self.norm_type == 1:
            return float(np.sum(np.abs(differences)))
        elif self.norm_type == 2:
            return float(np.sqrt(np.sum(np.square(differences))))
        elif self.norm_type == "inf":
            return float(np.max(np.abs(differences)))
        else:
            raise ValueError(f"Unsupported norm type: {self.norm_type}")
    
    def distance(self, x: Function, y: Function) -> float:
        """
        Calculate the pseudometric distance between two functions.
        
        The distance is computed as the norm of the differences between
        function outputs at the evaluation points.
        
        Args:
            x: First function
            y: Second function
            
        Returns:
            The non-negative distance value between the functions
            
        Raises:
            ValueError: If the functions cannot be evaluated properly
        """
        # Evaluate both functions at all evaluation points
        try:
            x_values = self._evaluate_function(x)
            y_values = self._evaluate_function(y)
        except ValueError as e:
            logger.error(f"Error evaluating functions: {e}")
            raise
        
        # Compute differences and apply norm
        differences = x_values - y_values
        distance_value = self._compute_norm(differences)
        
        # Validate non-negativity (should always be satisfied by norm)
        self._validate_non_negativity(distance_value, x, y)
        
        return distance_value
    
    def batch_distance(self, xs: List[Function], ys: List[Function]) -> List[float]:
        """
        Calculate distances between corresponding pairs of functions from two lists.
        
        Args:
            xs: List of first functions
            ys: List of second functions
            
        Returns:
            List of distances between corresponding functions
            
        Raises:
            ValueError: If input lists have different lengths
        """
        if len(xs) != len(ys):
            err_msg = f"Input lists must have equal length, got {len(xs)} and {len(ys)}"
            logger.error(err_msg)
            raise ValueError(err_msg)
        
        distances = []
        for i in range(len(xs)):
            try:
                distances.append(self.distance(xs[i], ys[i]))
            except ValueError as e:
                logger.warning(f"Error computing distance for pair {i}: {e}")
                # Re-raise with more context
                raise ValueError(f"Error computing distance for function pair {i}: {e}")
                
        return distances
    
    def pairwise_distances(self, points: List[Function]) -> List[List[float]]:
        """
        Calculate all pairwise distances between functions in the given list.
        
        Args:
            points: List of functions
            
        Returns:
            A square matrix (as list of lists) where element [i][j] 
            contains the distance between points[i] and points[j]
        """
        n = len(points)
        distance_matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        
        # Pre-compute all function evaluations to avoid redundant calculations
        evaluations = []
        for func in points:
            try:
                evaluations.append(self._evaluate_function(func))
            except ValueError as e:
                logger.error(f"Error evaluating function: {e}")
                raise ValueError(f"Failed to compute pairwise distances: {e}")
        
        # Compute upper triangular part of the distance matrix
        for i in range(n):
            for j in range(i+1, n):
                differences = evaluations[i] - evaluations[j]
                distance_value = self._compute_norm(differences)
                
                # Validate the distance is non-negative
                self._validate_non_negativity(distance_value, points[i], points[j])
                
                # Fill both entries (symmetry)
                distance_matrix[i][j] = distance_value
                distance_matrix[j][i] = distance_value
        
        return distance_matrix
    
    def add_evaluation_points(self, new_points: Sequence[Any]) -> None:
        """
        Add new evaluation points to the existing set.
        
        Args:
            new_points: New points to add to the evaluation set
            
        Note:
            This invalidates the function evaluation cache
        """
        # Convert to list, add new points, and convert back to tuple
        points_list = list(self.evaluation_points)
        points_list.extend(new_points)
        self.evaluation_points = tuple(points_list)
        
        # Clear the evaluation cache since we've changed the evaluation points
        self._evaluate_function.cache_clear()
        logger.info(f"Added {len(new_points)} new evaluation points, now using {len(self.evaluation_points)} points")
    
    def set_evaluation_points(self, points: Sequence[Any]) -> None:
        """
        Replace the current evaluation points with a new set.
        
        Args:
            points: New evaluation points to use
            
        Note:
            This invalidates the function evaluation cache
        """
        self.evaluation_points = tuple(points)
        # Clear the evaluation cache
        self._evaluate_function.cache_clear()
        logger.info(f"Set {len(self.evaluation_points)} new evaluation points")
    
    def get_evaluation_points(self) -> Tuple[Any, ...]:
        """
        Get the current evaluation points.
        
        Returns:
            Tuple of current evaluation points
        """
        return self.evaluation_points