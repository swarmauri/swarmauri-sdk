import logging
from typing import Dict, Literal

import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.seminorms.SeminormBase import SeminormBase
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.seminorms.ISeminorm import InputType, T
from swarmauri_core.vectors.IVector import IVector

# Configure logging
logger = logging.getLogger(__name__)


@ComponentBase.register_type(SeminormBase, "PointEvaluationSeminorm")
class PointEvaluationSeminorm(SeminormBase):
    """
    Seminorm that evaluates a function at a single point.

    This seminorm assigns a value by evaluating a function at a fixed coordinate or input.
    It's useful for measuring the behavior of functions at specific points of interest.

    Attributes
    ----------
    type : Literal["PointEvaluationSeminorm"]
        The type identifier for this seminorm.
    point : T
        The point at which to evaluate the function.
    absolute : bool
        Whether to take the absolute value of the function evaluation.
    """

    type: Literal["PointEvaluationSeminorm"] = "PointEvaluationSeminorm"
    point: T = None
    absolute: bool = True

    def __init__(self, point: T, absolute: bool = True, **kwargs):
        """
        Initialize the PointEvaluationSeminorm.

        Parameters
        ----------
        point : T
            The point at which to evaluate the function.
        absolute : bool, optional
            Whether to take the absolute value of the function evaluation, by default True.
            Must be True for a valid seminorm (to ensure non-negativity).
        """
        super().__init__(**kwargs)
        self.point = point
        self.absolute = absolute
        logger.debug(
            f"Initialized PointEvaluationSeminorm with point={point}, absolute={absolute}"
        )

    def compute(self, x: InputType) -> float:
        """
        Compute the seminorm by evaluating the input at the specified point.

        Parameters
        ----------
        x : InputType
            The input to evaluate. Must be callable or support item access.

        Returns
        -------
        float
            The (absolute) value of the function at the specified point.

        Raises
        ------
        TypeError
            If the input type is not supported.
        ValueError
            If the point is not in the domain of the function.
        """
        logger.debug(f"Computing point evaluation seminorm for input of type {type(x)}")

        try:
            # Handle different input types
            if callable(x):
                # If x is a function
                result = x(self.point)
            elif isinstance(x, (IVector, IMatrix, list, tuple, np.ndarray)):
                # If x is a vector-like object that supports indexing
                result = x[self.point]
            elif isinstance(x, dict):
                # If x is a dictionary
                result = x[self.point]
            else:
                raise TypeError(
                    f"Unsupported input type: {type(x)}. Must be callable or support item access."
                )

            # Convert result to float if possible
            try:
                result_float = float(result)
            except (TypeError, ValueError):
                # If result cannot be converted to float, use its magnitude/norm if available
                if hasattr(result, "norm"):
                    result_float = result.norm()
                elif hasattr(result, "__abs__"):
                    result_float = abs(result)
                else:
                    raise TypeError(
                        f"Cannot convert result {result} to a non-negative real number"
                    )

            # Apply absolute value if required
            if self.absolute:
                return abs(result_float)
            return result_float

        except (KeyError, IndexError) as e:
            logger.error(
                f"Point {self.point} is not in the domain of the function: {e}"
            )
            raise ValueError(
                f"Point {self.point} is not in the domain of the function"
            ) from e
        except Exception as e:
            logger.error(f"Error computing point evaluation seminorm: {e}")
            raise

    def check_triangle_inequality(self, x: InputType, y: InputType) -> bool:
        """
        Check if the triangle inequality property holds for the given inputs.

        The triangle inequality states that:
        ||x + y|| ≤ ||x|| + ||y||

        Parameters
        ----------
        x : InputType
            First input to check
        y : InputType
            Second input to check

        Returns
        -------
        bool
            True if the triangle inequality holds, False otherwise

        Raises
        ------
        TypeError
            If the input types are not supported or compatible
        ValueError
            If the check cannot be performed on the given inputs
        """
        logger.debug(
            f"Checking triangle inequality for inputs of types {type(x)} and {type(y)}"
        )

        try:
            # Compute the seminorms
            norm_x = self.compute(x)
            norm_y = self.compute(y)

            # For the sum, we need to handle different input types
            if callable(x) and callable(y):
                # For functions, create a new function that is their sum
                def sum_func(p):
                    return x(p) + y(p)

                norm_sum = self.compute(sum_func)
            elif isinstance(x, (list, tuple)) and isinstance(y, (list, tuple)):
                # For sequences, check if we can add them element-wise
                if len(x) != len(y):
                    raise ValueError(
                        "Sequences must have the same length for triangle inequality check"
                    )
                sum_seq = [x_i + y_i for x_i, y_i in zip(x, y)]
                norm_sum = self.compute(sum_seq)
            elif isinstance(x, dict) and isinstance(y, dict):
                # For dictionaries, merge them with addition for common keys
                sum_dict = dict(x)
                for key, value in y.items():
                    if key in sum_dict:
                        sum_dict[key] += value
                    else:
                        sum_dict[key] = value
                norm_sum = self.compute(sum_dict)
            elif hasattr(x, "__add__") and x.__add__(y) is not NotImplemented:
                # For objects that support addition
                norm_sum = self.compute(x + y)
            else:
                raise TypeError(f"Cannot add inputs of types {type(x)} and {type(y)}")

            # Check the triangle inequality
            return norm_sum <= norm_x + norm_y

        except Exception as e:
            logger.error(f"Error checking triangle inequality: {e}")
            raise

    def check_scalar_homogeneity(self, x: InputType, alpha: T) -> bool:
        """
        Check if the scalar homogeneity property holds for the given input and scalar.

        The scalar homogeneity states that:
        ||αx|| = |α|·||x||

        Parameters
        ----------
        x : InputType
            The input to check
        alpha : T
            The scalar to multiply by

        Returns
        -------
        bool
            True if scalar homogeneity holds, False otherwise

        Raises
        ------
        TypeError
            If the input type is not supported
        ValueError
            If the check cannot be performed on the given input
        """
        logger.debug(
            f"Checking scalar homogeneity for input of type {type(x)} with scalar {alpha}"
        )

        try:
            # Compute the seminorm of x
            norm_x = self.compute(x)

            # Create scaled version of x based on input type
            if callable(x):
                # For functions, create a new function that is scaled
                def scaled_func(p):
                    return alpha * x(p)

                scaled_x = scaled_func
            elif isinstance(x, (list, tuple)):
                # For sequences, scale each element
                scaled_x = [alpha * item for item in x]
            elif isinstance(x, dict):
                # For dictionaries, scale each value
                scaled_x = {key: alpha * value for key, value in x.items()}
            elif hasattr(x, "__mul__") and x.__mul__(alpha) is not NotImplemented:
                # For objects that support multiplication
                scaled_x = x * alpha
            else:
                raise TypeError(
                    f"Cannot scale input of type {type(x)} with scalar {alpha}"
                )

            # Compute the seminorm of the scaled input
            norm_scaled_x = self.compute(scaled_x)

            # Check scalar homogeneity (with a small tolerance for floating-point errors)
            return abs(norm_scaled_x - abs(alpha) * norm_x) < 1e-10

        except Exception as e:
            logger.error(f"Error checking scalar homogeneity: {e}")
            raise

    def to_dict(self) -> Dict[str, T]:
        """
        Convert the seminorm to a dictionary representation.

        Returns
        -------
        Dict[str, T]
            Dictionary representation of the seminorm
        """
        return {"type": self.type, "point": self.point, "absolute": self.absolute}

    @classmethod
    def from_dict(cls, data: Dict[str, T]) -> "PointEvaluationSeminorm":
        """
        Create a PointEvaluationSeminorm from a dictionary representation.

        Parameters
        ----------
        data : Dict[str, T]
            Dictionary representation of the seminorm

        Returns
        -------
        PointEvaluationSeminorm
            The reconstructed seminorm
        """
        return cls(point=data["point"], absolute=data.get("absolute", True))
