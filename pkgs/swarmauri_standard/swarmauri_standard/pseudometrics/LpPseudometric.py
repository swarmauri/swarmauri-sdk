import logging
import math
from typing import Callable, List, Literal, Optional, Sequence, Tuple, TypeVar, Union


try:
    import numpy as np  # type: ignore

    _NP_AVAILABLE = True
except Exception:  # pragma: no cover - numpy may not be installed
    _NP_AVAILABLE = False
    np = None  # type: ignore
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.pseudometrics.PseudometricBase import PseudometricBase
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.vectors.IVector import IVector

# Configure logging
logger = logging.getLogger(__name__)

# Type variables
T = TypeVar("T")

# Type aliases
if _NP_AVAILABLE:
    VectorType = Union[IVector, List[float], Tuple[float, ...], np.ndarray]
    MatrixType = Union[IMatrix, List[List[float]], np.ndarray]
else:  # pragma: no cover - numpy fallback
    VectorType = Union[IVector, List[float], Tuple[float, ...]]
    MatrixType = Union[IMatrix, List[List[float]]]

InputType = Union[VectorType, MatrixType, Sequence[T], str, Callable]


@ComponentBase.register_type(PseudometricBase, "LpPseudometric")
class LpPseudometric(PseudometricBase):
    """
    Lp-style pseudometric without point separation.

    This class defines a pseudometric over function space using Lp integration,
    possibly on a subset of coordinates or domain. It allows for calculating
    distances between functions or vectors based on the Lp norm of their differences,
    but may not distinguish between all distinct inputs.

    Attributes
    ----------
    type : Literal["LpPseudometric"]
        Type identifier for this component
    p : float
        The parameter p for the Lp pseudometric (must be in [1, ∞])
    domain : Optional[Tuple[float, float]]
        The domain interval [a, b] to integrate over
    coordinates : Optional[List[int]]
        Specific coordinates to include in the distance calculation
    epsilon : float
        Small value used for numerical stability
    """

    type: Literal["LpPseudometric"] = "LpPseudometric"

    def __init__(
        self,
        p: float = 2.0,
        domain: Optional[Tuple[float, float]] = None,
        coordinates: Optional[List[int]] = None,
        epsilon: float = 1e-10,
    ):
        """
        Initialize an Lp pseudometric.

        Parameters
        ----------
        p : float, optional
            The parameter p for the Lp pseudometric, by default 2.0
        domain : Optional[Tuple[float, float]], optional
            The domain interval [a, b] to integrate over, by default None
        coordinates : Optional[List[int]], optional
            Specific coordinates to include in the distance calculation, by default None
        epsilon : float, optional
            Small value used for numerical stability, by default 1e-10

        Raises
        ------
        ValueError
            If p is not in the range [1, ∞]
        ValueError
            If domain is specified but not a valid interval
        ValueError
            If coordinates contains negative indices
        """
        super().__init__()

        # Validate p parameter
        if p < 1:
            raise ValueError(f"Parameter p must be at least 1, got {p}")

        # Validate domain if provided
        if domain is not None:
            if len(domain) != 2 or domain[0] >= domain[1]:
                raise ValueError(
                    f"Domain must be a valid interval [a, b] where a < b, got {domain}"
                )

        # Validate coordinates if provided
        if coordinates is not None:
            if any(c < 0 for c in coordinates):
                raise ValueError("Coordinates must contain non-negative indices")

        self.p = p
        self.domain = domain
        self.coordinates = coordinates
        self.epsilon = epsilon

        logger.info(
            f"Initialized LpPseudometric with p={p}, domain={domain}, coordinates={coordinates}"
        )

    def _convert_to_array(self, x: InputType):
        """
        Convert input to a numpy array for computation.

        Parameters
        ----------
        x : InputType
            The input to convert

        Returns
        -------
        np.ndarray
            The converted input as a numpy array

        Raises
        ------
        TypeError
            If the input type is not supported
        """
        # Check for IVector and IMatrix first, using isinstance or hasattr
        if hasattr(x, "to_array") and callable(x.to_array):
            arr = x.to_array()
        elif _NP_AVAILABLE and isinstance(x, np.ndarray):
            arr = x
        elif isinstance(x, (list, tuple)):
            arr = list(x)
        elif isinstance(x, str):
            # Convert string to array of character codes
            arr = [ord(c) for c in x]
        elif callable(x):
            if self.domain is None:
                raise ValueError("Domain must be specified when using callable inputs")

            # Sample the function over the domain
            a, b = self.domain
            # Use 100 sample points by default
            if _NP_AVAILABLE:
                sample_points = np.linspace(a, b, 100)
            else:  # pragma: no cover - numpy fallback
                step = (b - a) / 99
                sample_points = [a + step * i for i in range(100)]
            arr = [x(t) for t in sample_points]
        else:
            try:
                # Try to convert to array as a last resort
                arr = list(x)
            except Exception:
                raise TypeError(f"Unsupported input type for LpPseudometric: {type(x)}")
        if _NP_AVAILABLE:
            return np.array(arr, dtype=float)
        return arr

    def _filter_coordinates(self, arr):
        """
        Filter array to include only specified coordinates.

        Parameters
        ----------
        arr : np.ndarray
            Input array

        Returns
        -------
        np.ndarray
            Filtered array containing only the specified coordinates
        """
        if self.coordinates is None:
            return arr

        coord_max = max(self.coordinates)

        if _NP_AVAILABLE and hasattr(arr, "shape"):
            if len(arr.shape) == 1:
                if coord_max >= arr.shape[0]:
                    raise ValueError(
                        f"Coordinate index out of bounds: max index {coord_max}, array shape {arr.shape}"
                    )
                return arr[self.coordinates]
            elif len(arr.shape) == 2:
                if coord_max >= arr.shape[0]:
                    raise ValueError(
                        f"Coordinate index out of bounds: max index {coord_max}, array shape {arr.shape}"
                    )
                return arr[self.coordinates, :]
            else:
                raise ValueError(
                    f"Cannot filter coordinates for array with shape {arr.shape}"
                )
        else:  # pragma: no cover - numpy fallback
            if isinstance(arr[0], (list, tuple)):
                if coord_max >= len(arr):
                    raise ValueError(
                        f"Coordinate index out of bounds: max index {coord_max}, array length {len(arr)}"
                    )
                return [arr[i] for i in self.coordinates]
            else:
                if coord_max >= len(arr):
                    raise ValueError(
                        f"Coordinate index out of bounds: max index {coord_max}, array length {len(arr)}"
                    )
                return [arr[i] for i in self.coordinates]

    def distance(self, x: InputType, y: InputType) -> float:
        """
        Calculate the Lp pseudometric distance between two objects.

        Parameters
        ----------
        x : InputType
            The first object
        y : InputType
            The second object

        Returns
        -------
        float
            The Lp pseudometric distance between x and y

        Raises
        ------
        TypeError
            If inputs are of incompatible types
        ValueError
            If inputs have incompatible dimensions
        """
        logger.debug(
            f"Calculating Lp pseudometric distance with p={self.p} between inputs of types {type(x)} and {type(y)}"
        )

        try:
            x_arr = self._convert_to_array(x)
            y_arr = self._convert_to_array(y)

            # Check if dimensions are compatible
            if _NP_AVAILABLE and hasattr(x_arr, "shape") and hasattr(y_arr, "shape"):
                if x_arr.shape != y_arr.shape:
                    raise ValueError(
                        f"Inputs must have the same shape: {x_arr.shape} vs {y_arr.shape}"
                    )
            else:  # pragma: no cover - numpy fallback
                if isinstance(x_arr[0], (list, tuple)) != isinstance(
                    y_arr[0], (list, tuple)
                ):
                    raise ValueError("Inputs must have the same shape")
                if isinstance(x_arr[0], (list, tuple)):
                    if len(x_arr) != len(y_arr) or any(
                        len(a) != len(b) for a, b in zip(x_arr, y_arr)
                    ):
                        raise ValueError("Inputs must have the same shape")
                else:
                    if len(x_arr) != len(y_arr):
                        raise ValueError("Inputs must have the same shape")

            # Filter coordinates if specified
            if self.coordinates is not None:
                x_arr = self._filter_coordinates(x_arr)
                y_arr = self._filter_coordinates(y_arr)

            # Calculate the difference
            if _NP_AVAILABLE and hasattr(x_arr, "__sub__"):
                diff = np.abs(x_arr - y_arr)
            else:  # pragma: no cover - numpy fallback
                diff = [abs(a - b) for a, b in zip(x_arr, y_arr)]

            # Apply normalization factor for callable inputs (domain integration)
            scaling_factor = 1.0
            if callable(x) and callable(y) and self.domain is not None:
                # For continuous functions, we need to scale by domain width
                domain_width = self.domain[1] - self.domain[0]
                # The scaling depends on number of sample points (default is 100)
                scaling_factor = domain_width / len(diff)

            # Handle special cases for common p values with scaling
            if math.isclose(self.p, 1.0):
                total = (
                    np.sum(diff * scaling_factor)
                    if _NP_AVAILABLE
                    else sum(d * scaling_factor for d in diff)
                )
                return float(total)
            elif math.isclose(self.p, 2.0):
                total = (
                    np.sum((diff**2) * scaling_factor)
                    if _NP_AVAILABLE
                    else sum((d**2) * scaling_factor for d in diff)
                )
                return float(np.sqrt(total) if _NP_AVAILABLE else math.sqrt(total))
            elif (_NP_AVAILABLE and np.isinf(self.p)) or (
                not _NP_AVAILABLE and math.isinf(self.p)
            ):
                return float(np.max(diff) if _NP_AVAILABLE else max(diff))
            else:
                total = (
                    np.sum((diff**self.p) * scaling_factor)
                    if _NP_AVAILABLE
                    else sum((d**self.p) * scaling_factor for d in diff)
                )
                return float((total) ** (1.0 / self.p))

        except Exception as e:
            logger.error(f"Error calculating Lp pseudometric distance: {str(e)}")
            raise

    def distances(
        self, xs: Sequence[InputType], ys: Sequence[InputType]
    ) -> List[List[float]]:
        """
        Calculate the pairwise distances between two collections of objects.

        Parameters
        ----------
        xs : Sequence[InputType]
            The first collection of objects
        ys : Sequence[InputType]
            The second collection of objects

        Returns
        -------
        List[List[float]]
            A matrix of distances where distances[i][j] is the distance between xs[i] and ys[j]

        Raises
        ------
        TypeError
            If inputs contain incompatible types
        ValueError
            If inputs have incompatible dimensions
        """
        logger.debug(
            f"Calculating pairwise Lp pseudometric distances between {len(xs)} and {len(ys)} objects"
        )

        result = []
        for i, x in enumerate(xs):
            row = []
            for j, y in enumerate(ys):
                try:
                    row.append(self.distance(x, y))
                except Exception as e:
                    logger.error(
                        f"Error calculating distance between xs[{i}] and ys[{j}]: {str(e)}"
                    )
                    raise
            result.append(row)

        return result

    def check_non_negativity(self, x: InputType, y: InputType) -> bool:
        """
        Check if the distance function satisfies the non-negativity property.

        Parameters
        ----------
        x : InputType
            The first object
        y : InputType
            The second object

        Returns
        -------
        bool
            True if d(x,y) ≥ 0, False otherwise
        """
        try:
            dist = self.distance(x, y)
            return dist >= 0
        except Exception as e:
            logger.error(f"Error checking non-negativity: {str(e)}")
            return False

    def check_symmetry(
        self, x: InputType, y: InputType, tolerance: float = 1e-10
    ) -> bool:
        """
        Check if the distance function satisfies the symmetry property.

        Parameters
        ----------
        x : InputType
            The first object
        y : InputType
            The second object
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
            return abs(dist_xy - dist_yx) <= tolerance
        except Exception as e:
            logger.error(f"Error checking symmetry: {str(e)}")
            return False

    def check_triangle_inequality(
        self, x: InputType, y: InputType, z: InputType, tolerance: float = 1e-10
    ) -> bool:
        """
        Check if the distance function satisfies the triangle inequality.

        Parameters
        ----------
        x : InputType
            The first object
        y : InputType
            The second object
        z : InputType
            The third object
        tolerance : float, optional
            The tolerance for floating-point comparisons, by default 1e-10

        Returns
        -------
        bool
            True if d(x,z) ≤ d(x,y) + d(y,z) within tolerance, False otherwise
        """
        try:
            dist_xz = self.distance(x, z)
            dist_xy = self.distance(x, y)
            dist_yz = self.distance(y, z)

            # Account for floating-point errors with tolerance
            return dist_xz <= dist_xy + dist_yz + tolerance
        except Exception as e:
            logger.error(f"Error checking triangle inequality: {str(e)}")
            return False

    def check_weak_identity(self, x: InputType, y: InputType) -> bool:
        """
        Check if the distance function satisfies the weak identity property.

        In a pseudometric, d(x,y) = 0 is allowed even when x ≠ y.
        This method verifies that this property is properly handled.

        Parameters
        ----------
        x : InputType
            The first object
        y : InputType
            The second object

        Returns
        -------
        bool
            True if the pseudometric properly handles the weak identity property
        """
        # For Lp pseudometric, weak identity is satisfied when:
        # 1. d(x,x) = 0 for any x
        # 2. If objects differ only outside the measured domain/coordinates, d(x,y) = 0

        try:
            # Check if d(x,x) = 0
            if not math.isclose(self.distance(x, x), 0, abs_tol=self.epsilon):
                return False

            # Check if d(y,y) = 0
            if not math.isclose(self.distance(y, y), 0, abs_tol=self.epsilon):
                return False

            # If d(x,y) = 0, then the weak identity property is satisfied
            # for these particular x and y
            if math.isclose(self.distance(x, y), 0, abs_tol=self.epsilon):
                return True

            # If we're only measuring certain coordinates and the objects are
            # identical in those coordinates but different elsewhere, d(x,y) should be 0
            x_arr = self._convert_to_array(x)
            y_arr = self._convert_to_array(y)

            if self.coordinates is not None:
                x_filtered = self._filter_coordinates(x_arr)
                y_filtered = self._filter_coordinates(y_arr)

                # If the filtered arrays are equal but the original arrays are not,
                # then we have a case of weak identity
                return np.array_equal(x_filtered, y_filtered) and not np.array_equal(
                    x_arr, y_arr
                )

            # If we have a domain restriction for callable functions,
            # we can't easily check this property in the general case

            return False
        except Exception as e:
            logger.error(f"Error checking weak identity: {str(e)}")
            return False

    def __str__(self) -> str:
        """
        Return a string representation of the LpPseudometric.

        Returns
        -------
        str
            String representation
        """
        domain_str = f", domain={self.domain}" if self.domain else ""
        coords_str = f", coordinates={self.coordinates}" if self.coordinates else ""
        return f"LpPseudometric(p={self.p}{domain_str}{coords_str})"

    def __repr__(self) -> str:
        """
        Return a detailed string representation of the LpPseudometric.

        Returns
        -------
        str
            Detailed string representation
        """
        return f"LpPseudometric(p={self.p}, domain={self.domain}, coordinates={self.coordinates}, epsilon={self.epsilon})"
