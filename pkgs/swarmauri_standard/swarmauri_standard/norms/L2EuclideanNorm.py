import logging
import math
from typing import Callable, Literal, Sequence, TypeVar, Union

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.norms.NormBase import NormBase
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.vectors.IVector import IVector

# Configure logging
logger = logging.getLogger(__name__)

# Define type variables for supported input types
VectorType = TypeVar("VectorType", bound=IVector)
MatrixType = TypeVar("MatrixType", bound=IMatrix)
SequenceType = TypeVar("SequenceType", bound=Sequence)
StringType = TypeVar("StringType", bound=str)
CallableType = TypeVar("CallableType", bound=Callable)


@ComponentBase.register_type(NormBase, "L2EuclideanNorm")
class L2EuclideanNorm(NormBase):
    """
    Implementation of the Euclidean (L2) norm.

    The Euclidean norm computes the square root of the sum of squares
    of vector components. It is the most commonly used vector norm and
    represents the standard notion of distance in Euclidean space.

    Attributes
    ----------
    type : Literal["L2EuclideanNorm"]
        The specific type of norm.
    resource : str, optional
        The resource type, defaults to NORM.
    """

    type: Literal["L2EuclideanNorm"] = "L2EuclideanNorm"

    def compute(
        self, x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
    ) -> float:
        """
        Compute the Euclidean (L2) norm of the input.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
            The input for which to compute the norm.

        Returns
        -------
        float
            The computed Euclidean norm value.

        Raises
        ------
        TypeError
            If the input type is not supported.
        ValueError
            If the norm cannot be computed for the given input.
        """
        logger.debug(f"Computing L2 Euclidean norm for input of type {type(x)}")

        # Handle different input types
        if isinstance(x, IVector):
            # Use to_numpy() to get numeric values instead of iterating directly
            vector_data = x.to_numpy()
            return math.sqrt(sum(x_i**2 for x_i in vector_data))
        elif isinstance(x, IMatrix):
            # For matrix objects - treat as flattened vector
            return math.sqrt(sum(x_ij**2 for row in x for x_ij in row))
        elif isinstance(x, Sequence) and not isinstance(x, str):
            # For general sequences (lists, tuples, etc.)
            try:
                return math.sqrt(sum(x_i**2 for x_i in x))
            except (TypeError, ValueError) as e:
                logger.error(f"Failed to compute L2 norm for sequence: {e}")
                raise ValueError(
                    f"Cannot compute L2 norm for sequence with non-numeric elements: {e}"
                )
        elif isinstance(x, str):
            # For strings - use ASCII/Unicode values
            return math.sqrt(sum(ord(char) ** 2 for char in x))
        elif callable(x):
            # For functions - not a standard operation, but could implement a custom behavior
            raise TypeError("L2 norm computation for callable objects is not supported")
        else:
            logger.error(f"Unsupported input type for L2 norm: {type(x)}")
            raise TypeError(f"L2 norm computation not supported for type {type(x)}")

    def check_non_negativity(
        self, x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
    ) -> bool:
        """
        Check if the Euclidean norm satisfies the non-negativity property.

        The Euclidean norm is always non-negative by definition.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
            The input to check.

        Returns
        -------
        bool
            True if the norm is non-negative, which is always the case for Euclidean norm.
        """
        try:
            norm_value = self.compute(x)
            logger.debug(f"Checking non-negativity: norm value = {norm_value}")
            return norm_value >= 0
        except (TypeError, ValueError) as e:
            logger.error(f"Error checking non-negativity: {e}")
            return False

    def check_definiteness(
        self, x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
    ) -> bool:
        """
        Check if the Euclidean norm satisfies the definiteness property.

        The definiteness property states that the norm of x is 0 if and only if x is 0.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
            The input to check.

        Returns
        -------
        bool
            True if the norm satisfies the definiteness property.
        """
        try:
            # Compute the norm
            norm_value = self.compute(x)

            # Check if the norm is zero
            if (
                abs(norm_value) < 1e-10
            ):  # Using a small epsilon for floating-point comparison
                # Check if all elements are zero
                if isinstance(x, IVector) or (
                    isinstance(x, Sequence) and not isinstance(x, str)
                ):
                    is_zero = all(abs(element) < 1e-10 for element in x)
                elif isinstance(x, IMatrix):
                    is_zero = all(abs(element) < 1e-10 for row in x for element in row)
                elif isinstance(x, str):
                    is_zero = len(x) == 0
                else:
                    logger.warning(
                        f"Definiteness check not fully implemented for type {type(x)}"
                    )
                    return False

                logger.debug(
                    f"Checking definiteness: norm = {norm_value}, all elements zero: {is_zero}"
                )
                return is_zero
            else:
                # If norm is not zero, then the vector is not zero
                return True
        except (TypeError, ValueError) as e:
            logger.error(f"Error checking definiteness: {e}")
            return False

    def check_triangle_inequality(
        self,
        x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType],
        y: Union[VectorType, MatrixType, SequenceType, StringType, CallableType],
    ) -> bool:
        """
        Check if the Euclidean norm satisfies the triangle inequality.

        The triangle inequality states that norm(x + y) <= norm(x) + norm(y).

        Parameters
        ----------
        x : Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
            The first input.
        y : Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
            The second input.

        Returns
        -------
        bool
            True if the norm satisfies the triangle inequality.

        Raises
        ------
        TypeError
            If the inputs are not of the same type or cannot be added.
        """
        try:
            # Check if inputs are of the same type
            if type(x) is not type(y):
                raise TypeError(
                    f"Inputs must be of the same type, got {type(x)} and {type(y)}"
                )

            # Compute norms
            norm_x = self.compute(x)
            norm_y = self.compute(y)

            # Handle different input types for addition
            if isinstance(x, IVector):
                # Vector addition
                if len(x) != len(y):
                    raise ValueError("Vectors must have the same dimension")
                z = [x[i] + y[i] for i in range(len(x))]
            elif isinstance(x, IMatrix):
                # Matrix addition
                if x.shape != y.shape:
                    raise ValueError("Matrices must have the same shape")
                z = [
                    [x[i][j] + y[i][j] for j in range(len(x[0]))] for i in range(len(x))
                ]
            elif isinstance(x, Sequence) and not isinstance(x, str):
                # Sequence addition
                if len(x) != len(y):
                    raise ValueError("Sequences must have the same length")
                z = [x[i] + y[i] for i in range(len(x))]
            elif isinstance(x, str):
                # String concatenation (not a standard vector operation)
                z = x + y
            else:
                raise TypeError(
                    f"Triangle inequality check not supported for type {type(x)}"
                )

            # Compute norm of the sum
            norm_z = self.compute(z)

            # Check triangle inequality
            result = (
                norm_z <= norm_x + norm_y + 1e-10
            )  # Adding small epsilon for floating-point comparison
            logger.debug(
                f"Triangle inequality check: norm(x+y)={norm_z}, norm(x)+norm(y)={norm_x + norm_y}, result={result}"
            )
            return result

        except (TypeError, ValueError) as e:
            logger.error(f"Error checking triangle inequality: {e}")
            raise

    def check_absolute_homogeneity(
        self,
        x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType],
        scalar: float,
    ) -> bool:
        """
        Check if the Euclidean norm satisfies the absolute homogeneity property.

        The absolute homogeneity property states that norm(a*x) = |a|*norm(x) for scalar a.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
            The input.
        scalar : float
            The scalar value.

        Returns
        -------
        bool
            True if the norm satisfies the absolute homogeneity property.

        Raises
        ------
        TypeError
            If the input cannot be scaled by the scalar.
        """
        try:
            # Compute the norm of x
            norm_x = self.compute(x)

            # Scale the input by the scalar
            if isinstance(x, IVector):
                scaled_x = [scalar * x_i for x_i in x]
            elif isinstance(x, IMatrix):
                scaled_x = [
                    [scalar * x[i][j] for j in range(len(x[0]))] for i in range(len(x))
                ]
            elif isinstance(x, Sequence) and not isinstance(x, str):
                scaled_x = [scalar * x_i for x_i in x]
            elif isinstance(x, str):
                if not isinstance(scalar, int) or scalar < 0:
                    raise TypeError(
                        "String can only be multiplied by non-negative integers"
                    )
                scaled_x = x * scalar
            else:
                raise TypeError(
                    f"Absolute homogeneity check not supported for type {type(x)}"
                )

            # Compute the norm of the scaled input
            norm_scaled_x = self.compute(scaled_x)

            # Check absolute homogeneity
            expected = abs(scalar) * norm_x
            result = (
                abs(norm_scaled_x - expected) < 1e-10
            )  # Using small epsilon for floating-point comparison

            logger.debug(
                f"Absolute homogeneity check: norm(a*x)={norm_scaled_x}, |a|*norm(x)={expected}, result={result}"
            )
            return result

        except (TypeError, ValueError) as e:
            logger.error(f"Error checking absolute homogeneity: {e}")
            raise
