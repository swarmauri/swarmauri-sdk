import logging
from typing import Literal, Sequence, Union

import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.norms.NormBase import NormBase
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.vectors.IVector import IVector

# Configure logging
logger = logging.getLogger(__name__)


@ComponentBase.register_type(NormBase, "L1ManhattanNorm")
class L1ManhattanNorm(NormBase):
    """
    Implementation of the L1 (Manhattan) norm.

    The L1 norm calculates the sum of the absolute values of vector components.
    Also known as the Manhattan or Taxicab norm, it represents the distance
    traveled along grid lines in a city block layout.

    Attributes
    ----------
    type : Literal["L1ManhattanNorm"]
        The type identifier for this norm implementation.
    resource : str, optional
        The resource type, defaults to NORM.
    """

    type: Literal["L1ManhattanNorm"] = "L1ManhattanNorm"

    def compute(self, x: Union[IVector, IMatrix, Sequence, str, float]) -> float:
        """
        Compute the L1 (Manhattan) norm of the input.

        Parameters
        ----------
        x : Union[IVector, IMatrix, Sequence, str, float]
            The input for which to compute the norm.

        Returns
        -------
        float
            The computed L1 norm value.

        Raises
        ------
        TypeError
            If the input type is not supported.
        ValueError
            If the norm cannot be computed for the given input.
        """
        logger.debug(f"Computing L1 Manhattan norm for input of type: {type(x)}")

        # Handle IVector implementation
        if isinstance(x, IVector):
            return float(sum(abs(val) for val in x.values))

        # Handle IMatrix implementation (flattening the matrix)
        elif isinstance(x, IMatrix):
            return float(sum(abs(val) for row in x.values for val in row))

        # Handle sequence types (lists, tuples, etc.)
        elif isinstance(x, Sequence) and not isinstance(x, str):
            # Convert all elements to float and compute sum of absolute values
            try:
                return float(sum(abs(float(val)) for val in x))
            except (ValueError, TypeError) as e:
                logger.error(
                    f"Cannot compute L1 norm for sequence with non-numeric elements: {e}"
                )
                raise TypeError(f"L1 norm requires numeric elements in sequence: {e}")

        # Handle numpy arrays
        elif hasattr(x, "__array__"):  # Check for numpy array compatibility
            try:
                return float(np.sum(np.abs(x)))
            except Exception as e:
                logger.error(f"Error computing L1 norm for numpy array: {e}")
                raise ValueError(
                    f"Cannot compute L1 norm for the given numpy array: {e}"
                )

        # Handle unsupported types
        else:
            logger.error(f"Unsupported input type for L1 norm: {type(x)}")
            raise TypeError(f"L1 norm computation not supported for type: {type(x)}")

    def check_non_negativity(
        self, x: Union[IVector, IMatrix, Sequence, str, float]
    ) -> bool:
        """
        Check if the L1 norm satisfies the non-negativity property.

        The L1 norm is always non-negative by definition (sum of absolute values).

        Parameters
        ----------
        x : Union[IVector, IMatrix, Sequence, str, float]
            The input to check.

        Returns
        -------
        bool
            True if the norm is non-negative, always True for L1 norm.
        """
        try:
            norm_value = self.compute(x)
            logger.debug(f"L1 norm value: {norm_value}, checking non-negativity")
            return norm_value >= 0
        except (TypeError, ValueError) as e:
            logger.error(f"Error checking non-negativity: {e}")
            return False

    def check_definiteness(
        self, x: Union[IVector, IMatrix, Sequence, str, float]
    ) -> bool:
        """
        Check if the L1 norm satisfies the definiteness property.

        The definiteness property states that the norm of x is 0 if and only if x is 0.

        Parameters
        ----------
        x : Union[IVector, IMatrix, Sequence, str, float]
            The input to check.

        Returns
        -------
        bool
            True if the norm satisfies the definiteness property.
        """
        try:
            # Check if all elements are zero
            is_zero = self._is_zero(x)
            norm_value = self.compute(x)

            logger.debug(f"L1 norm value: {norm_value}, is_zero: {is_zero}")

            # The norm is 0 if and only if x is 0
            return (norm_value == 0 and is_zero) or (norm_value > 0 and not is_zero)
        except (TypeError, ValueError) as e:
            logger.error(f"Error checking definiteness: {e}")
            return False

    def check_triangle_inequality(
        self,
        x: Union[IVector, IMatrix, Sequence, str, float],
        y: Union[IVector, IMatrix, Sequence, str, float],
    ) -> bool:
        """
        Check if the L1 norm satisfies the triangle inequality.

        The triangle inequality states that norm(x + y) <= norm(x) + norm(y).

        Parameters
        ----------
        x : Union[IVector, IMatrix, Sequence, str, float]
            The first input.
        y : Union[IVector, IMatrix, Sequence, str, float]
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
            # Verify inputs are compatible for addition
            if not self._are_compatible(x, y):
                logger.error("Inputs are not compatible for addition")
                raise TypeError(
                    "Inputs must be of the same type and dimension for triangle inequality check"
                )

            # Compute the sum of x and y
            x_plus_y = self._add(x, y)

            # Compute norms
            norm_x = self.compute(x)
            norm_y = self.compute(y)
            norm_x_plus_y = self.compute(x_plus_y)

            logger.debug(
                f"Triangle inequality check: norm(x+y)={norm_x_plus_y}, norm(x)+norm(y)={norm_x + norm_y}"
            )

            # Check triangle inequality
            # Allow for small floating-point errors
            return norm_x_plus_y <= (norm_x + norm_y) + 1e-10
        except (TypeError, ValueError) as e:
            logger.error(f"Error checking triangle inequality: {e}")
            raise

    def check_absolute_homogeneity(
        self, x: Union[IVector, IMatrix, Sequence, str, float], scalar: float
    ) -> bool:
        """
        Check if the L1 norm satisfies the absolute homogeneity property.

        The absolute homogeneity property states that norm(a*x) = |a|*norm(x) for scalar a.

        Parameters
        ----------
        x : Union[IVector, IMatrix, Sequence, str, float]
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
            # Scale the input by the scalar
            scaled_x = self._scale(x, scalar)

            # Compute norms
            norm_x = self.compute(x)
            norm_scaled_x = self.compute(scaled_x)
            expected_norm = abs(scalar) * norm_x

            logger.debug(
                f"Absolute homogeneity check: norm({scalar}*x)={norm_scaled_x}, |{scalar}|*norm(x)={expected_norm}"
            )

            # Check absolute homogeneity with a small tolerance for floating-point errors
            return abs(norm_scaled_x - expected_norm) < 1e-10
        except (TypeError, ValueError) as e:
            logger.error(f"Error checking absolute homogeneity: {e}")
            raise

    def _is_zero(self, x: Union[IVector, IMatrix, Sequence, str, float]) -> bool:
        """
        Check if all elements in the input are zero.

        Parameters
        ----------
        x : Union[IVector, IMatrix, Sequence, str, float]
            The input to check.

        Returns
        -------
        bool
            True if all elements are zero, False otherwise.

        Raises
        ------
        TypeError
            If the input type is not supported.
        """
        # Handle IVector implementation
        if isinstance(x, IVector):
            return all(val == 0 for val in x.values)

        # Handle IMatrix implementation
        elif isinstance(x, IMatrix):
            return all(val == 0 for row in x.values for val in row)

        # Handle sequence types (lists, tuples, etc.)
        elif isinstance(x, Sequence) and not isinstance(x, str):
            try:
                return all(float(val) == 0 for val in x)
            except (ValueError, TypeError):
                raise TypeError(
                    "Cannot check if sequence elements are zero: non-numeric elements"
                )

        # Handle numpy arrays
        elif hasattr(x, "__array__"):
            return np.all(x == 0)

        else:
            raise TypeError(f"Cannot check if elements are zero for type: {type(x)}")

    def _are_compatible(self, x: float, y: float) -> bool:
        """
        Check if two inputs are compatible for addition.

        Parameters
        ----------
        x : float
            The first input.
        y : float
            The second input.

        Returns
        -------
        bool
            True if inputs are compatible for addition, False otherwise.
        """
        # Both should be of the same type
        if type(x) is not type(y):
            return False

        # For IVector, check if dimensions match
        if isinstance(x, IVector):
            return len(x.values) == len(y.values)

        # For IMatrix, check if dimensions match
        elif isinstance(x, IMatrix):
            return len(x.values) == len(y.values) and all(
                len(x_row) == len(y_row) for x_row, y_row in zip(x.values, y.values)
            )

        # For sequences, check if lengths match
        elif isinstance(x, Sequence) and not isinstance(x, str):
            return len(x) == len(y)

        # For numpy arrays
        elif hasattr(x, "shape") and hasattr(y, "shape"):
            return x.shape == y.shape

        return False

    def _add(self, x: float, y: float) -> float:
        """
        Add two inputs together.

        Parameters
        ----------
        x : float
            The first input.
        y : float
            The second input.

        Returns
        -------
        float
            The result of adding x and y.

        Raises
        ------
        TypeError
            If the inputs cannot be added.
        """
        # For IVector
        if isinstance(x, IVector):
            result_values = [x_val + y_val for x_val, y_val in zip(x.values, y.values)]
            # Create a new vector with the same class as x
            new_vector = x.__class__()
            new_vector.values = result_values
            return new_vector

        # For IMatrix
        elif isinstance(x, IMatrix):
            result_values = [
                [x_val + y_val for x_val, y_val in zip(x_row, y_row)]
                for x_row, y_row in zip(x.values, y.values)
            ]
            # Create a new matrix with the same class as x
            new_matrix = x.__class__()
            new_matrix.values = result_values
            return new_matrix

        # For sequences
        elif isinstance(x, Sequence) and not isinstance(x, str):
            return [float(x_val) + float(y_val) for x_val, y_val in zip(x, y)]

        # For numpy arrays
        elif hasattr(x, "__array__") and hasattr(y, "__array__"):
            return x + y

        else:
            raise TypeError(f"Cannot add objects of type: {type(x)}")

    def _scale(self, x: float, scalar: float) -> float:
        """
        Scale an input by a scalar.

        Parameters
        ----------
        x : float
            The input to scale.
        scalar : float
            The scalar value.

        Returns
        -------
        float
            The result of scaling x by scalar.

        Raises
        ------
        TypeError
            If the input cannot be scaled.
        """
        # For IVector
        if isinstance(x, IVector):
            result_values = [scalar * val for val in x.values]
            # Create a new vector with the same class as x
            new_vector = x.__class__()
            new_vector.values = result_values
            return new_vector

        # For IMatrix
        elif isinstance(x, IMatrix):
            result_values = [[scalar * val for val in row] for row in x.values]
            # Create a new matrix with the same class as x
            new_matrix = x.__class__()
            new_matrix.values = result_values
            return new_matrix

        # For sequences
        elif isinstance(x, Sequence) and not isinstance(x, str):
            return [scalar * float(val) for val in x]

        # For numpy arrays
        elif hasattr(x, "__array__"):
            return scalar * x

        else:
            raise TypeError(f"Cannot scale object of type: {type(x)}")
