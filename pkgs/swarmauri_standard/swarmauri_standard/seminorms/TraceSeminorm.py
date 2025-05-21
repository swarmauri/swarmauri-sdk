import logging
from typing import Literal

import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.seminorms.SeminormBase import SeminormBase
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.seminorms.ISeminorm import InputType, T
from swarmauri_core.vectors.IVector import IVector

# Configure logging
logger = logging.getLogger(__name__)


@ComponentBase.register_type(SeminormBase, "TraceSeminorm")
class TraceSeminorm(SeminormBase):
    """
    Trace seminorm implementation that computes the trace norm of a matrix.

    This seminorm uses the trace of a matrix in its computation without
    guaranteeing positive-definiteness. It calculates the sum of singular
    values of a matrix, which is equal to the trace of the square root of A*A^T.

    Attributes
    ----------
    type : Literal["TraceSeminorm"]
        The type identifier for this seminorm.
    """

    type: Literal["TraceSeminorm"] = "TraceSeminorm"

    def compute(self, x: InputType) -> float:
        """
        Compute the trace seminorm of the input matrix.

        For a matrix input, this computes the sum of singular values,
        which is equivalent to the trace norm.

        Parameters
        ----------
        x : InputType
            The input to compute the seminorm for. Should be a matrix or
            matrix-like object that supports the trace operation.

        Returns
        -------
        float
            The trace seminorm value (non-negative real number)

        Raises
        ------
        TypeError
            If the input type does not support trace operation
        ValueError
            If the computation cannot be performed on the given input
        """
        logger.debug(f"Computing trace seminorm for input of type {type(x)}")

        # Handle matrix inputs
        if isinstance(x, IMatrix):
            # Compute trace norm (nuclear norm) as sum of singular values
            try:
                # Get numpy representation for computation
                matrix_data = x.to_numpy()
                # Calculate singular values
                singular_values = np.linalg.svd(matrix_data, compute_uv=False)
                # Trace norm is the sum of singular values
                return float(np.sum(singular_values))
            except Exception as e:
                logger.error(f"Error computing trace seminorm: {str(e)}")
                raise ValueError(f"Failed to compute trace seminorm: {str(e)}")

        # Handle numpy arrays directly
        elif isinstance(x, np.ndarray):
            if x.ndim >= 2:  # Must be a matrix-like array
                try:
                    singular_values = np.linalg.svd(x, compute_uv=False)
                    return float(np.sum(singular_values))
                except Exception as e:
                    logger.error(
                        f"Error computing trace seminorm for numpy array: {str(e)}"
                    )
                    raise ValueError(
                        f"Failed to compute trace seminorm for numpy array: {str(e)}"
                    )
            else:
                raise TypeError("Input numpy array must have at least 2 dimensions")

        # If input is a vector, treat it as a column matrix
        elif isinstance(x, IVector):
            try:
                vector_data = x.to_numpy()
                # Reshape to column matrix
                matrix_data = vector_data.reshape(-1, 1)
                singular_values = np.linalg.svd(matrix_data, compute_uv=False)
                return float(np.sum(singular_values))
            except Exception as e:
                logger.error(f"Error computing trace seminorm for vector: {str(e)}")
                raise ValueError(
                    f"Failed to compute trace seminorm for vector: {str(e)}"
                )

        else:
            logger.error(f"Unsupported input type for trace seminorm: {type(x)}")
            raise TypeError(
                f"Trace seminorm requires a matrix or matrix-like input, got {type(x)}"
            )

    def check_triangle_inequality(self, x: InputType, y: InputType) -> bool:
        """
        Check if the triangle inequality property holds for the given inputs.

        The triangle inequality for trace norm states that:
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

        # Ensure we can add the inputs
        try:
            # Convert inputs to numpy arrays if they're IMatrix or IVector
            x_data = x.to_numpy() if hasattr(x, "to_numpy") else np.array(x)
            y_data = y.to_numpy() if hasattr(y, "to_numpy") else np.array(y)

            # Check if shapes are compatible for addition
            if x_data.shape != y_data.shape:
                logger.warning(
                    f"Incompatible shapes for triangle inequality check: {x_data.shape} vs {y_data.shape}"
                )
                return False

            # Compute the sum
            sum_data = x_data + y_data

            # Compute norms
            x_norm = self.compute(x)
            y_norm = self.compute(y)
            sum_norm = self.compute(sum_data)

            # Check triangle inequality
            # Add a small epsilon for floating point comparison
            epsilon = 1e-10
            return sum_norm <= x_norm + y_norm + epsilon

        except Exception as e:
            logger.error(f"Error checking triangle inequality: {str(e)}")
            raise ValueError(f"Failed to check triangle inequality: {str(e)}")

    def check_scalar_homogeneity(self, x: InputType, alpha: T) -> bool:
        """
        Check if the scalar homogeneity property holds for the given input and scalar.

        The scalar homogeneity for trace norm states that:
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
            # Convert alpha to a complex number to handle all numeric types
            alpha_complex = complex(alpha)
            alpha_abs = abs(alpha_complex)

            # Convert input to numpy array if it's IMatrix or IVector
            x_data = x.to_numpy() if hasattr(x, "to_numpy") else np.array(x)

            # Compute scaled input
            scaled_data = alpha_complex * x_data

            # Compute norms
            x_norm = self.compute(x)
            scaled_norm = self.compute(scaled_data)

            # Check scalar homogeneity
            # Add a small epsilon for floating point comparison
            epsilon = 1e-10
            return abs(scaled_norm - alpha_abs * x_norm) < epsilon

        except Exception as e:
            logger.error(f"Error checking scalar homogeneity: {str(e)}")
            raise ValueError(f"Failed to check scalar homogeneity: {str(e)}")

    def is_degenerate(self, x: InputType) -> bool:
        """
        Check if the seminorm is degenerate for the given input.

        A seminorm is degenerate if there exists a non-zero input for which
        the seminorm is zero.

        Parameters
        ----------
        x : InputType
            The input to check for degeneracy

        Returns
        -------
        bool
            True if the seminorm is degenerate for the input, False otherwise

        Raises
        ------
        TypeError
            If the input type is not supported
        ValueError
            If the check cannot be performed on the given input
        """
        logger.debug(f"Checking degeneracy for input of type {type(x)}")

        try:
            # Convert input to numpy array if it's IMatrix or IVector
            x_data = x.to_numpy() if hasattr(x, "to_numpy") else np.array(x)

            # Check if input is non-zero
            if not np.any(x_data):
                # Zero input is not interesting for degeneracy check
                return False

            # Compute the seminorm
            norm_value = self.compute(x)

            # If input is non-zero but norm is zero, the seminorm is degenerate
            epsilon = 1e-10  # Small threshold for floating point comparison
            return norm_value < epsilon

        except Exception as e:
            logger.error(f"Error checking degeneracy: {str(e)}")
            raise ValueError(f"Failed to check degeneracy: {str(e)}")
