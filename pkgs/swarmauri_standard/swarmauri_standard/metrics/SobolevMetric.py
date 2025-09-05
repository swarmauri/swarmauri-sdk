import logging
from typing import Dict, List, Literal, Sequence, Union

import numpy as np
from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.metrics.IMetric import MetricInput, MetricInputCollection
from swarmauri_core.vectors.IVector import IVector

from swarmauri_standard.norms.SobolevNorm import SobolevNorm

# Configure logging
logger = logging.getLogger(__name__)


@ComponentBase.register_type(MetricBase, "SobolevMetric")
class SobolevMetric(MetricBase):
    """
    A metric derived from the Sobolev norm.

    This metric accounts for both the differences in function values and their
    derivatives, making it suitable for measuring distance between functions
    where smoothness is important.

    Attributes
    ----------
    type : Literal["SobolevMetric"]
        The type identifier for this metric.
    order : int
        The highest derivative order to consider in the metric computation.
    weights : Dict[int, float]
        Weights for each derivative order in the metric computation.
    """

    type: Literal["SobolevMetric"] = "SobolevMetric"
    order: int = Field(default=1, description="Highest derivative order to consider")
    weights: Dict[int, float] = Field(
        default_factory=lambda: {0: 1.0, 1: 1.0},
        description="Weights for each derivative order",
    )

    def __init__(self, **kwargs):
        """
        Initialize the Sobolev metric with specified parameters.

        Parameters
        ----------
        **kwargs
            Keyword arguments to pass to the parent class constructor.
            May include 'order' and 'weights' to customize the metric.
        """
        super().__init__(**kwargs)
        # Create a SobolevNorm instance to handle the norm calculations
        self.norm = SobolevNorm(order=self.order, weights=self.weights)
        logger.debug(
            f"Initialized SobolevMetric with order {self.order} and weights {self.weights}"
        )

    def distance(self, x: MetricInput, y: MetricInput) -> float:
        """
        Calculate the Sobolev distance between two functions or vectors.

        The Sobolev distance is defined as the Sobolev norm of the difference
        between the two inputs, taking into account both values and derivatives.

        Parameters
        ----------
        x : MetricInput
            First input (function or vector)
        y : MetricInput
            Second input (function or vector)

        Returns
        -------
        float
            The Sobolev distance between x and y

        Raises
        ------
        ValueError
            If inputs are incompatible or the distance cannot be computed
        TypeError
            If input types are not supported
        """
        logger.debug(
            f"Calculating Sobolev distance between {type(x).__name__} and {type(y).__name__}"
        )

        try:
            # Ensure x and y are of the same type
            if not isinstance(y, type(x)) and not (callable(x) and callable(y)):
                raise TypeError(
                    f"Inputs must be of the same type, got {type(x).__name__} and {type(y).__name__}"
                )

            # For callable functions
            if callable(x) and callable(y):
                # Create a new function representing x - y
                def diff_func(t):
                    return x(t) - y(t)

                # For functions with derivatives
                if hasattr(x, "derivative") and hasattr(y, "derivative"):
                    # Add derivative method to diff_func
                    def create_derivative(func_x, func_y):
                        def derivative_func(t):
                            return func_x.derivative()(t) - func_y.derivative()(t)

                        return derivative_func

                    diff_func.derivative = lambda: create_derivative(x, y)

                return self.norm.compute(diff_func)

            # For vector-like objects
            elif isinstance(x, IVector) and isinstance(y, IVector):
                from swarmauri_standard.vectors.Vector import Vector

                x_array = x.to_numpy()
                y_array = y.to_numpy()
                diff_values = [x_array[i] - y_array[i] for i in range(len(x_array))]
                diff_vector = Vector(value=diff_values)
                return self.norm.compute(diff_vector)

            # For sequences
            elif isinstance(x, Sequence) and isinstance(y, Sequence):
                if len(x) != len(y):
                    raise ValueError(
                        "Sequences must have the same length for distance calculation"
                    )
                diff_xy = [x[i] - y[i] for i in range(len(x))]
                return self.norm.compute(diff_xy)

            else:
                raise TypeError(
                    f"Cannot compute difference for type {type(x).__name__}"
                )
        except TypeError as e:
            # Re-raise TypeError directly
            logger.error(f"Error calculating Sobolev distance: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error calculating Sobolev distance: {str(e)}")
            raise ValueError(f"Failed to calculate Sobolev distance: {str(e)}")

    def distances(
        self,
        x: Union[MetricInput, MetricInputCollection],
        y: Union[MetricInput, MetricInputCollection],
    ) -> Union[List[float], IVector, IMatrix]:
        """
        Calculate Sobolev distances between collections of functions or vectors.

        Parameters
        ----------
        x : Union[MetricInput, MetricInputCollection]
            First collection of inputs
        y : Union[MetricInput, MetricInputCollection]
            Second collection of inputs

        Returns
        -------
        Union[List[float], IVector, IMatrix]
            Matrix or vector of Sobolev distances between inputs in x and y

        Raises
        ------
        ValueError
            If inputs are incompatible or distances cannot be computed
        TypeError
            If input types are not supported
        """
        logger.debug("Calculating Sobolev distances between collections")

        try:
            # Handle different collection types
            if isinstance(x, IMatrix) and isinstance(y, IMatrix):
                # Return distance matrix between rows of x and y
                result = x.zeros((x.shape[0], y.shape[0]))
                for i in range(x.shape[0]):
                    for j in range(y.shape[0]):
                        result[i, j] = self.distance(x[i], y[j])
                return result

            elif isinstance(x, IVector) and isinstance(y, IVector):
                # Return vector of distances between corresponding elements
                if x.shape[0] != y.shape[0]:
                    raise ValueError(
                        "Vectors must have the same length for element-wise distances"
                    )
                result = x.zeros(x.shape[0])
                for i in range(x.shape[0]):
                    result[i] = self.distance(x[i], y[i])
                return result

            elif isinstance(x, list) and isinstance(y, list):
                # Return a distance matrix even for same-length lists if they contain Vector objects
                if len(x) > 0 and isinstance(x[0], IVector):
                    result = [[0.0 for _ in range(len(y))] for _ in range(len(x))]
                    for i in range(len(x)):
                        for j in range(len(y)):
                            result[i][j] = self.distance(x[i], y[j])
                    return result
                elif len(x) != len(y):
                    # Return distance matrix for different length lists
                    result = [[0.0 for _ in range(len(y))] for _ in range(len(x))]
                    for i in range(len(x)):
                        for j in range(len(y)):
                            result[i][j] = self.distance(x[i], y[j])
                    return result
                else:
                    # Return list of distances for same-length lists of non-Vector objects
                    return [self.distance(x[i], y[i]) for i in range(len(x))]

            elif hasattr(x, "shape") and hasattr(y, "shape") and hasattr(x, "zeros"):
                # Handle matrix-like objects, including mocks
                result = x.zeros((x.shape[0], y.shape[0]))
                for i in range(x.shape[0]):
                    for j in range(y.shape[0]):
                        result[i, j] = self.distance(x[i], y[j])
                return result

            else:
                raise TypeError(
                    f"Unsupported collection types: {type(x).__name__} and {type(y).__name__}"
                )

        except Exception as e:
            logger.error(f"Error calculating Sobolev distances: {str(e)}")
            raise ValueError(f"Failed to calculate Sobolev distances: {str(e)}")

    def check_non_negativity(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the Sobolev metric satisfies the non-negativity axiom: d(x,y) ≥ 0.

        Parameters
        ----------
        x : MetricInput
            First input
        y : MetricInput
            Second input

        Returns
        -------
        bool
            True if the axiom is satisfied, False otherwise
        """
        logger.debug("Checking non-negativity axiom for Sobolev metric")
        try:
            dist = self.distance(x, y)
            return dist >= 0
        except Exception as e:
            logger.error(f"Error checking non-negativity: {str(e)}")
            return False

    def check_identity_of_indiscernibles(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the Sobolev metric satisfies the identity of indiscernibles axiom:
        d(x,y) = 0 if and only if x = y.

        Parameters
        ----------
        x : MetricInput
            First input
        y : MetricInput
            Second input

        Returns
        -------
        bool
            True if the axiom is satisfied, False otherwise
        """
        logger.debug("Checking identity of indiscernibles axiom for Sobolev metric")
        try:
            dist = self.distance(x, y)

            # Check if distance is 0
            if abs(dist) < 1e-10:
                # If distance is 0, check if x and y are effectively equal
                return self._are_effectively_equal(x, y)
            else:
                # If distance is not 0, x and y should be different
                return not self._are_effectively_equal(x, y)
        except Exception as e:
            logger.error(f"Error checking identity of indiscernibles: {str(e)}")
            return False

    def check_symmetry(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the Sobolev metric satisfies the symmetry axiom: d(x,y) = d(y,x).

        Parameters
        ----------
        x : MetricInput
            First input
        y : MetricInput
            Second input

        Returns
        -------
        bool
            True if the axiom is satisfied, False otherwise
        """
        logger.debug("Checking symmetry axiom for Sobolev metric")
        try:
            dist_xy = self.distance(x, y)
            dist_yx = self.distance(y, x)
            # Allow for small numerical differences
            return abs(dist_xy - dist_yx) < 1e-3 * (1 + abs(dist_xy))
        except Exception as e:
            logger.error(f"Error checking symmetry: {str(e)}")
            return False

    def check_triangle_inequality(
        self, x: MetricInput, y: MetricInput, z: MetricInput
    ) -> bool:
        """
        Check if the Sobolev metric satisfies the triangle inequality axiom:
        d(x,z) ≤ d(x,y) + d(y,z).

        Parameters
        ----------
        x : MetricInput
            First input
        y : MetricInput
            Second input
        z : MetricInput
            Third input

        Returns
        -------
        bool
            True if the axiom is satisfied, False otherwise
        """
        logger.debug("Checking triangle inequality axiom for Sobolev metric")
        try:
            dist_xy = self.distance(x, y)
            dist_yz = self.distance(y, z)
            dist_xz = self.distance(x, z)

            # Check the triangle inequality with a small tolerance for numerical issues
            return dist_xz <= dist_xy + dist_yz + 1e-10 * (1 + dist_xy + dist_yz)
        except Exception as e:
            logger.error(f"Error checking triangle inequality: {str(e)}")
            return False

    def _are_effectively_equal(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if two inputs are effectively equal for the purposes of the metric.

        Parameters
        ----------
        x : MetricInput
            First input
        y : MetricInput
            Second input

        Returns
        -------
        bool
            True if the inputs are effectively equal, False otherwise
        """
        try:
            if callable(x) and callable(y):
                # Sample the functions at several points to check if they're equal
                test_points = np.linspace(0, 1, 20)

                # Check function values
                for t in test_points:
                    if abs(x(t) - y(t)) > 1e-10:
                        return False

                # Check derivatives if available
                if hasattr(x, "derivative") and hasattr(y, "derivative"):
                    x_deriv = x.derivative()
                    y_deriv = y.derivative()

                    for t in test_points:
                        if abs(x_deriv(t) - y_deriv(t)) > 1e-10:
                            return False

                return True

            elif hasattr(x, "__eq__"):
                return x == y

            elif isinstance(x, Sequence) and isinstance(y, Sequence):
                if len(x) != len(y):
                    return False
                return all(
                    abs(float(x[i]) - float(y[i])) < 1e-10 for i in range(len(x))
                )

            else:
                # Default case
                return x == y

        except Exception as e:
            logger.error(f"Error checking if inputs are equal: {str(e)}")
            return False
