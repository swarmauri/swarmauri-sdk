import logging
import random
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Sequence,
    TypeVar,
    Union,
)


import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.pseudometrics.PseudometricBase import PseudometricBase

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar("T", bound=Union[int, float, complex])


@ComponentBase.register_type(PseudometricBase, "FunctionDifferencePseudometric")
class FunctionDifferencePseudometric(PseudometricBase):
    """
    Measures the distance between two functions based on their output differences.

    This pseudometric calculates the distance between functions by evaluating them
    at specific points and measuring the differences in their outputs. Functions are
    considered close if they produce similar outputs at the evaluation points, even
    if they differ elsewhere.

    Attributes
    ----------
    type : Literal["FunctionDifferencePseudometric"]
        The type identifier for this pseudometric.
    evaluation_points : Optional[List[Any]]
        The specific points at which to evaluate the functions.
    num_samples : int
        Number of points to sample if using random sampling.
    sampling_strategy : str
        Strategy for sampling points ('fixed', 'random', 'grid').
    domain_bounds : Optional[Dict[str, Tuple[float, float]]]
        Bounds for the domain when using random or grid sampling.
    norm_type : str
        The type of norm to use for calculating differences ('l1', 'l2', 'max').
    """

    type: Literal["FunctionDifferencePseudometric"] = "FunctionDifferencePseudometric"

    def __init__(
        self,
        evaluation_points: Optional[List[Any]] = None,
        num_samples: int = 10,
        sampling_strategy: str = "fixed",
        domain_bounds: Optional[Dict[str, tuple]] = None,
        norm_type: str = "l2",
    ):
        """
        Initialize the FunctionDifferencePseudometric.

        Parameters
        ----------
        evaluation_points : Optional[List[Any]], optional
            The specific points at which to evaluate the functions. Required if
            sampling_strategy is 'fixed'.
        num_samples : int, optional
            Number of points to sample if using random sampling, by default 10.
        sampling_strategy : str, optional
            Strategy for sampling points ('fixed', 'random', 'grid'), by default "fixed".
        domain_bounds : Optional[Dict[str, tuple]], optional
            Bounds for the domain when using random or grid sampling, by default None.
            Example: {'x': (-1, 1), 'y': (0, 2)} for a 2D domain.
        norm_type : str, optional
            The type of norm to use for calculating differences ('l1', 'l2', 'max'),
            by default "l2".

        Raises
        ------
        ValueError
            If evaluation_points is None and sampling_strategy is 'fixed',
            or if domain_bounds is None and sampling_strategy is 'random' or 'grid'.
        """
        super().__init__()

        # Validate inputs
        if sampling_strategy == "fixed" and evaluation_points is None:
            raise ValueError(
                "evaluation_points must be provided when sampling_strategy is 'fixed'"
            )

        if sampling_strategy in ["random", "grid"] and domain_bounds is None:
            raise ValueError(
                "domain_bounds must be provided when sampling_strategy is 'random' or 'grid'"
            )

        if norm_type not in ["l1", "l2", "max"]:
            raise ValueError("norm_type must be one of 'l1', 'l2', or 'max'")

        self.evaluation_points = evaluation_points
        self.num_samples = num_samples
        self.sampling_strategy = sampling_strategy
        self.domain_bounds = domain_bounds
        self.norm_type = norm_type

        # Generate sample points if not fixed
        self._sample_points = None
        if sampling_strategy != "fixed":
            self._generate_sample_points()

        logger.debug(
            f"Initialized FunctionDifferencePseudometric with strategy={sampling_strategy}, "
            f"num_samples={num_samples}, norm_type={norm_type}"
        )

    def _generate_sample_points(self) -> None:
        """
        Generate sample points based on the specified strategy.

        This method creates sample points based on the sampling strategy:
        - 'random': Randomly samples points within the domain bounds
        - 'grid': Creates a grid of points within the domain bounds

        The generated points are stored in self._sample_points.

        Raises
        ------
        ValueError
            If the sampling strategy is not supported.
        """
        if self.sampling_strategy == "random":
            self._generate_random_points()
        elif self.sampling_strategy == "grid":
            self._generate_grid_points()
        else:
            raise ValueError(f"Unsupported sampling strategy: {self.sampling_strategy}")

        logger.debug(
            f"Generated {len(self._sample_points)} sample points using {self.sampling_strategy} strategy"
        )

    def _generate_random_points(self) -> None:
        """
        Generate random sample points within the domain bounds.

        The generated points are stored in self._sample_points.
        """
        # Extract dimensions and bounds
        dimensions = list(self.domain_bounds.keys())
        bounds = [self.domain_bounds[dim] for dim in dimensions]

        # Generate random points
        self._sample_points = []
        for _ in range(self.num_samples):
            if len(dimensions) == 1:
                # 1D case - return scalar
                lower, upper = bounds[0]
                point = random.uniform(lower, upper)
                self._sample_points.append(point)
            else:
                # Multi-dimensional case - return dict
                point = {
                    dim: random.uniform(lower, upper)
                    for dim, (lower, upper) in zip(dimensions, bounds)
                }
                self._sample_points.append(point)

    def _generate_grid_points(self) -> None:
        """
        Generate a grid of sample points within the domain bounds.

        The generated points are stored in self._sample_points.
        """
        # Extract dimensions and bounds
        dimensions = list(self.domain_bounds.keys())
        bounds = [self.domain_bounds[dim] for dim in dimensions]

        # Calculate points per dimension
        # For n dimensions, we want approximately num_samples total points
        # So we need approximately num_samples^(1/n) points per dimension
        points_per_dim = max(2, int(self.num_samples ** (1 / len(dimensions))))

        # Generate grid points for each dimension
        grid_points = []
        for lower, upper in bounds:
            if points_per_dim > 1:
                step = (upper - lower) / (points_per_dim - 1)
                dim_points = [lower + i * step for i in range(points_per_dim)]
            else:
                dim_points = [(lower + upper) / 2]  # Just the midpoint
            grid_points.append(dim_points)

        # Generate all combinations
        self._sample_points = []

        if len(dimensions) == 1:
            # 1D case - return scalars
            self._sample_points = grid_points[0]
        else:
            # Multi-dimensional case - return dicts
            # Use numpy's meshgrid to generate all combinations
            mesh = np.meshgrid(*grid_points, indexing="ij")
            grid_shape = mesh[0].shape

            for idx in np.ndindex(grid_shape):
                point = {dim: mesh[i][idx] for i, dim in enumerate(dimensions)}
                self._sample_points.append(point)

            # If we have too many points, randomly sample down to num_samples
            if len(self._sample_points) > self.num_samples:
                self._sample_points = random.sample(
                    self._sample_points, self.num_samples
                )

    def _get_evaluation_points(self) -> List[Any]:
        """
        Get the points at which to evaluate the functions.

        Returns
        -------
        List[Any]
            The points to use for function evaluation.
        """
        if self.sampling_strategy == "fixed":
            return self.evaluation_points
        else:
            if self._sample_points is None:
                self._generate_sample_points()
            return self._sample_points

    def _evaluate_function(self, func: Callable, points: List[Any]) -> List[float]:
        """
        Evaluate a function at the given points.

        Parameters
        ----------
        func : Callable
            The function to evaluate.
        points : List[Any]
            The points at which to evaluate the function.

        Returns
        -------
        List[float]
            The function values at the given points.

        Raises
        ------
        ValueError
            If the function cannot be evaluated at a point.
        """
        results = []

        for point in points:
            try:
                value = func(point)
                # Ensure the result is a float
                if isinstance(value, (int, float)):
                    results.append(float(value))
                else:
                    # If the result is not a scalar, try to get its magnitude
                    if hasattr(value, "norm"):
                        results.append(float(value.norm()))
                    elif hasattr(value, "__abs__"):
                        results.append(float(abs(value)))
                    else:
                        raise ValueError(
                            f"Function output {value} cannot be converted to a float"
                        )
            except Exception as e:
                logger.error(f"Error evaluating function at point {point}: {e}")
                raise ValueError(
                    f"Failed to evaluate function at point {point}: {e}"
                ) from e

        return results

    def _calculate_difference(
        self, values1: List[float], values2: List[float]
    ) -> float:
        """
        Calculate the difference between two sets of function values.

        Parameters
        ----------
        values1 : List[float]
            The values of the first function at the evaluation points.
        values2 : List[float]
            The values of the second function at the evaluation points.

        Returns
        -------
        float
            The difference between the function values, based on the selected norm.

        Raises
        ------
        ValueError
            If the lists have different lengths.
        """
        if len(values1) != len(values2):
            raise ValueError("Function value lists must have the same length")

        # Calculate differences
        differences = [abs(v1 - v2) for v1, v2 in zip(values1, values2)]

        # Apply the selected norm
        if self.norm_type == "l1":
            # L1 norm (sum of absolute differences)
            return sum(differences)
        elif self.norm_type == "l2":
            # L2 norm (Euclidean distance)
            return np.sqrt(sum(d**2 for d in differences))
        elif self.norm_type == "max":
            # Maximum norm (maximum absolute difference)
            return max(differences) if differences else 0.0
        else:
            # This should never happen due to validation in __init__
            raise ValueError(f"Unsupported norm type: {self.norm_type}")

    def distance(self, x: Callable, y: Callable) -> float:
        """
        Calculate the pseudometric distance between two functions.

        Parameters
        ----------
        x : Callable
            The first function
        y : Callable
            The second function

        Returns
        -------
        float
            The distance between the functions based on their output differences

        Raises
        ------
        TypeError
            If inputs are not callable
        ValueError
            If functions cannot be evaluated at the sample points
        """
        # Validate inputs
        if not callable(x) or not callable(y):
            logger.error("Both inputs must be callable functions")
            raise TypeError("Both inputs must be callable functions")

        try:
            # Get evaluation points
            points = self._get_evaluation_points()

            # Evaluate functions at the points
            values_x = self._evaluate_function(x, points)
            values_y = self._evaluate_function(y, points)

            # Calculate difference
            diff = self._calculate_difference(values_x, values_y)

            logger.debug(f"Function difference distance: {diff}")
            return diff

        except Exception as e:
            logger.error(f"Error calculating function difference: {e}")
            raise

    def distances(
        self, xs: Sequence[Callable], ys: Sequence[Callable]
    ) -> List[List[float]]:
        """
        Calculate the pairwise distances between two collections of functions.

        Parameters
        ----------
        xs : Sequence[Callable]
            The first collection of functions
        ys : Sequence[Callable]
            The second collection of functions

        Returns
        -------
        List[List[float]]
            A matrix of distances where distances[i][j] is the distance between xs[i] and ys[j]

        Raises
        ------
        TypeError
            If any input is not callable
        ValueError
            If functions cannot be evaluated at the sample points
        """
        # Validate inputs
        if not all(callable(f) for f in xs) or not all(callable(f) for f in ys):
            logger.error("All inputs must be callable functions")
            raise TypeError("All inputs must be callable functions")

        try:
            # Get evaluation points
            points = self._get_evaluation_points()

            # Pre-compute function values to avoid redundant evaluations
            values_xs = [self._evaluate_function(f, points) for f in xs]
            values_ys = [self._evaluate_function(f, points) for f in ys]

            # Calculate all pairwise distances
            result = []
            for values_x in values_xs:
                row = []
                for values_y in values_ys:
                    diff = self._calculate_difference(values_x, values_y)
                    row.append(diff)
                result.append(row)

            return result

        except Exception as e:
            logger.error(f"Error calculating pairwise function differences: {e}")
            raise

    def check_non_negativity(self, x: Callable, y: Callable) -> bool:
        """
        Check if the distance function satisfies the non-negativity property.

        For a pseudometric, d(x,y) ≥ 0 must always hold.

        Parameters
        ----------
        x : Callable
            The first function
        y : Callable
            The second function

        Returns
        -------
        bool
            True if d(x,y) ≥ 0, False otherwise
        """
        try:
            dist = self.distance(x, y)
            result = dist >= 0

            if not result:
                logger.warning(f"Non-negativity check failed: distance = {dist}")

            return result

        except Exception as e:
            logger.error(f"Error checking non-negativity: {e}")
            raise

    def check_symmetry(
        self, x: Callable, y: Callable, tolerance: float = 1e-10
    ) -> bool:
        """
        Check if the distance function satisfies the symmetry property.

        For a pseudometric, d(x,y) = d(y,x) must hold.

        Parameters
        ----------
        x : Callable
            The first function
        y : Callable
            The second function
        tolerance : float, optional
            The tolerance for floating-point comparisons, by default 1e-10

        Returns
        -------
        bool
            True if d(x,y) = d(y,x) within tolerance, False otherwise
        """
        try:
            dist_xy = self.distance(x, y)
            dist_yx = self.distance(y, x)

            result = abs(dist_xy - dist_yx) <= tolerance

            if not result:
                logger.warning(
                    f"Symmetry check failed: d(x,y) = {dist_xy}, d(y,x) = {dist_yx}"
                )

            return result

        except Exception as e:
            logger.error(f"Error checking symmetry: {e}")
            raise

    def check_triangle_inequality(
        self, x: Callable, y: Callable, z: Callable, tolerance: float = 1e-10
    ) -> bool:
        """
        Check if the distance function satisfies the triangle inequality.

        For a pseudometric, d(x,z) ≤ d(x,y) + d(y,z) must hold.

        Parameters
        ----------
        x : Callable
            The first function
        y : Callable
            The second function
        z : Callable
            The third function
        tolerance : float, optional
            The tolerance for floating-point comparisons, by default 1e-10

        Returns
        -------
        bool
            True if d(x,z) ≤ d(x,y) + d(y,z) within tolerance, False otherwise
        """
        try:
            dist_xy = self.distance(x, y)
            dist_yz = self.distance(y, z)
            dist_xz = self.distance(x, z)

            result = dist_xz <= dist_xy + dist_yz + tolerance

            if not result:
                logger.warning(
                    f"Triangle inequality check failed: "
                    f"d(x,z) = {dist_xz}, d(x,y) + d(y,z) = {dist_xy + dist_yz}"
                )

            return result

        except Exception as e:
            logger.error(f"Error checking triangle inequality: {e}")
            raise

    def check_weak_identity(self, x: Callable, y: Callable) -> bool:
        """
        Check if the distance function satisfies the weak identity property.

        For a pseudometric, d(x,y) = 0 is allowed even when x ≠ y, which happens
        when the functions produce identical outputs at all evaluation points.

        Parameters
        ----------
        x : Callable
            The first function
        y : Callable
            The second function

        Returns
        -------
        bool
            True if the pseudometric properly handles the weak identity property
        """
        try:
            # Create a function that's equal to x at all evaluation points but different elsewhere
            points = self._get_evaluation_points()

            # Evaluate x at all points to create a lookup table
            x_values = {}
            for point in points:
                x_values[str(point)] = x(point)

            # Create a function that matches x at evaluation points but differs elsewhere
            def modified_x(p):
                # If p is in our evaluation points, return the same value as x
                p_str = str(p)
                if p_str in x_values:
                    return x_values[p_str]
                # Otherwise, return a different value
                return x(p) + 1.0 if callable(x) else 1.0

            # The distance between x and modified_x should be 0
            # (they're equal at all evaluation points)
            dist = self.distance(x, modified_x)

            result = abs(dist) <= 1e-10

            if not result:
                logger.warning(f"Weak identity check failed: distance = {dist}")

            return result

        except Exception as e:
            logger.error(f"Error checking weak identity: {e}")
            raise

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the pseudometric to a dictionary representation.

        Returns
        -------
        Dict[str, Any]
            Dictionary representation of the pseudometric
        """
        return {
            "type": self.type,
            "evaluation_points": self.evaluation_points,
            "num_samples": self.num_samples,
            "sampling_strategy": self.sampling_strategy,
            "domain_bounds": self.domain_bounds,
            "norm_type": self.norm_type,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FunctionDifferencePseudometric":
        """
        Create a FunctionDifferencePseudometric from a dictionary representation.

        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary representation of the pseudometric

        Returns
        -------
        FunctionDifferencePseudometric
            The reconstructed pseudometric
        """
        return cls(
            evaluation_points=data.get("evaluation_points"),
            num_samples=data.get("num_samples", 10),
            sampling_strategy=data.get("sampling_strategy", "fixed"),
            domain_bounds=data.get("domain_bounds"),
            norm_type=data.get("norm_type", "l2"),
        )
