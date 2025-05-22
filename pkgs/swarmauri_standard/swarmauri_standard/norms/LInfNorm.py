import logging
from typing import Callable, Literal, Optional, Sequence, TypeVar, Union

import numpy as np
from pydantic import Field, field_validator
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.norms.NormBase import NormBase
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.vectors.IVector import IVector

# Configure logging
logger = logging.getLogger(__name__)

# Define type variables for supported input types
T = TypeVar("T")
VectorType = TypeVar("VectorType", bound=IVector)
MatrixType = TypeVar("MatrixType", bound=IMatrix)
SequenceType = TypeVar("SequenceType", bound=Sequence)
StringType = TypeVar("StringType", bound=str)
CallableType = TypeVar("CallableType", bound=Callable)


@ComponentBase.register_type(NormBase, "LInfNorm")
class LInfNorm(NormBase):
    """
    L-infinity norm implementation for real-valued functions.

    This norm measures the largest absolute value in a function's domain.
    It requires a bounded domain for proper computation.

    Attributes
    ----------
    type : Literal["LInfNorm"]
        The type identifier for this norm.
    resource : str, optional
        The resource type, defaults to NORM.
    domain_bounds : tuple, optional
        The bounds of the domain (min, max), defaults to (-1, 1).
    """

    type: Literal["LInfNorm"] = "LInfNorm"
    resource: Optional[str] = Field(default=ResourceTypes.NORM.value)
    domain_bounds: tuple = Field(default=(-1, 1))

    @field_validator("domain_bounds")
    def validate_domain_bounds(cls, v):
        """
        Validate that the domain bounds are properly specified.

        Parameters
        ----------
        v : tuple
            The domain bounds to validate.

        Returns
        -------
        tuple
            The validated domain bounds.

        Raises
        ------
        ValueError
            If the domain bounds are not properly specified.
        """
        if not isinstance(v, tuple) or len(v) != 2:
            raise ValueError("Domain bounds must be a tuple of (min, max)")
        if v[0] >= v[1]:
            raise ValueError("Lower bound must be less than upper bound")
        return v

    def compute(
        self, x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
    ) -> float:
        """
        Compute the L-infinity norm of the input.

        For vectors, matrices, and sequences, this is the maximum absolute value.
        For callable functions, this is the maximum absolute value over the domain.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
            The input for which to compute the norm.

        Returns
        -------
        float
            The computed L-infinity norm value.

        Raises
        ------
        TypeError
            If the input type is not supported.
        ValueError
            If the norm cannot be computed for the given input.
        """
        logger.debug(f"Computing L-infinity norm for {type(x)}")

        # Handle different input types
        if isinstance(x, (IVector, IMatrix)):
            # For Vector and Matrix types, use their data representation
            return self._compute_for_sequence(x.data)
        elif isinstance(x, Sequence) and not isinstance(x, str):
            # For sequence types (lists, tuples, etc.)
            return self._compute_for_sequence(x)
        elif isinstance(x, str):
            # For strings, convert to ASCII values
            return self._compute_for_sequence([ord(char) for char in x])
        elif callable(x):
            # For callable functions
            return self._compute_for_function(x)
        else:
            raise TypeError(f"Unsupported input type for L-infinity norm: {type(x)}")

    def _compute_for_sequence(self, seq: Sequence) -> float:
        """
        Compute the L-infinity norm for a sequence.

        Parameters
        ----------
        seq : Sequence
            The sequence for which to compute the norm.

        Returns
        -------
        float
            The maximum absolute value in the sequence.

        Raises
        ------
        ValueError
            If the sequence is empty.
        """
        # Fix: Check for empty sequence using len() which works for both lists and NumPy arrays
        if len(seq) == 0:
            raise ValueError("Cannot compute L-infinity norm of an empty sequence")

        try:
            # Convert to numpy array for efficient computation
            array = np.asarray(seq, dtype=float)
            return float(np.max(np.abs(array)))
        except (ValueError, TypeError) as e:
            logger.error(f"Error converting sequence to numeric values: {e}")
            raise ValueError(f"L-infinity norm requires numeric values: {e}")

    def _compute_for_function(self, func: Callable) -> float:
        """
        Compute the L-infinity norm for a callable function.

        This is an approximation using sampling over the domain.

        Parameters
        ----------
        func : Callable
            The function for which to compute the norm.

        Returns
        -------
        float
            The maximum absolute value of the function over the domain.
        """
        # Sample the function over the domain
        lower, upper = self.domain_bounds
        num_samples = 1000  # Number of sample points

        try:
            # Create evenly spaced sample points
            sample_points = np.linspace(lower, upper, num_samples)
            # Evaluate function at sample points
            function_values = np.array([func(x) for x in sample_points])
            return float(np.max(np.abs(function_values)))
        except Exception as e:
            logger.error(f"Error evaluating function for L-infinity norm: {e}")
            raise ValueError(f"Failed to compute L-infinity norm for function: {e}")

    def check_non_negativity(
        self, x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
    ) -> bool:
        """
        Check if the L-infinity norm satisfies the non-negativity property.

        The L-infinity norm is always non-negative by definition.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
            The input to check.

        Returns
        -------
        bool
            True if the norm is non-negative, False otherwise.
        """
        try:
            norm_value = self.compute(x)
            result = norm_value >= 0
            return result
        except Exception as e:
            logger.error(f"Error checking non-negativity: {e}")
            return False

    def check_definiteness(
        self, x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
    ) -> bool:
        """
        Check if the L-infinity norm satisfies the definiteness property.

        The definiteness property states that the norm of x is 0 if and only if x is 0.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
            The input to check.

        Returns
        -------
        bool
            True if the norm satisfies the definiteness property, False otherwise.
        """
        try:
            norm_value = self.compute(x)

            # Check if x is "zero"
            is_zero = False

            if isinstance(x, IVector):
                is_zero = all(v == 0 for v in x.data)
            elif isinstance(x, IMatrix):
                # Fix: Convert numpy array to list before checking
                data_array = np.asarray(x.data)
                is_zero = np.all(data_array == 0)
            elif isinstance(x, Sequence) and not isinstance(x, str):
                # Handle case where sequence might be a numpy array
                if hasattr(x, "__array__") or isinstance(x, np.ndarray):
                    is_zero = np.all(np.asarray(x) == 0)
                else:
                    is_zero = all(v == 0 for v in x)
            elif isinstance(x, str):
                is_zero = len(x) == 0
            elif callable(x):
                # Sample function at multiple points to check if it's zero
                lower, upper = self.domain_bounds
                sample_points = np.linspace(lower, upper, 100)
                is_zero = all(abs(x(pt)) < 1e-10 for pt in sample_points)

            # The norm is 0 if and only if x is 0
            return (norm_value == 0) == is_zero
        except (TypeError, ValueError) as e:
            logger.error(f"Error checking definiteness: {e}")
            return False

    def check_triangle_inequality(
        self,
        x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType],
        y: Union[VectorType, MatrixType, SequenceType, StringType, CallableType],
    ) -> bool:
        """
        Check if the L-infinity norm satisfies the triangle inequality.

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
            True if the norm satisfies the triangle inequality, False otherwise.

        Raises
        ------
        TypeError
            If the inputs are not of the same type or cannot be added.
        ValueError
            If inputs have different dimensions or cannot be combined.
        """
        # Handle different input types
        if isinstance(x, IVector) and isinstance(y, type(x)):
            # For Vector types
            z = type(x)(data=[x_val + y_val for x_val, y_val in zip(x.data, y.data)])
        elif isinstance(x, IMatrix) and isinstance(y, type(x)):
            # For Matrix types - use numpy array handling
            x_array = np.asarray(x.data)
            y_array = np.asarray(y.data)
            # Check shapes match
            if x_array.shape != y_array.shape:
                raise ValueError("Matrices must have the same shape")
            sum_array = x_array + y_array
            # Create a new matrix of the same type with the summed data
            z = type(x)(data=sum_array.tolist())
        elif (
            isinstance(x, Sequence)
            and isinstance(y, type(x))
            and not isinstance(x, str)
        ):
            # For sequence types
            if len(x) != len(y):
                raise ValueError("Sequences must have the same length")

            # Handle numpy arrays
            if isinstance(x, np.ndarray) or isinstance(y, np.ndarray):
                z = np.asarray(x) + np.asarray(y)
            else:
                z = [x_val + y_val for x_val, y_val in zip(x, y)]
        elif isinstance(x, str) and isinstance(y, str):
            # For strings, we'll add their ASCII values
            if len(x) != len(y):
                raise ValueError("Strings must have the same length")
            z = "".join(
                chr(min(ord(x_char) + ord(y_char), 255)) for x_char, y_char in zip(x, y)
            )
        elif callable(x) and callable(y):
            # For callable functions
            def z(t):
                return x(t) + y(t)

        else:
            raise TypeError("Inputs must be of the same type and must support addition")

        try:
            # Compute norms
            norm_x = self.compute(x)
            norm_y = self.compute(y)
            norm_z = self.compute(z)

            # Check triangle inequality
            # Allow for small numerical errors
            return norm_z <= norm_x + norm_y + 1e-10
        except Exception as e:
            logger.error(f"Error checking triangle inequality: {e}")
            return False

    def check_absolute_homogeneity(
        self,
        x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType],
        scalar: float,
    ) -> bool:
        """
        Check if the L-infinity norm satisfies the absolute homogeneity property.

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
            True if the norm satisfies the absolute homogeneity property, False otherwise.

        Raises
        ------
        TypeError
            If the input cannot be scaled by the scalar.
        """
        try:
            # Handle different input types
            if isinstance(x, IVector):
                # For Vector types
                scaled_x = type(x)(data=[scalar * val for val in x.data])
            elif isinstance(x, IMatrix):
                # For Matrix types - properly handle numpy arrays
                data_array = np.asarray(x.data)
                scaled_array = scalar * data_array
                scaled_x = type(x)(data=scaled_array.tolist())
            elif isinstance(x, Sequence) and not isinstance(x, str):
                # For sequence types
                if isinstance(x, np.ndarray):
                    scaled_x = scalar * x
                else:
                    scaled_x = [scalar * val for val in x]
            elif isinstance(x, str):
                # For strings, scaling is not well-defined
                # We'll scale the ASCII values and ensure they're valid (0-255)
                scaled_x = "".join(
                    chr(max(0, min(255, int(scalar * ord(char))))) for char in x
                )
            elif callable(x):

                def scaled_x(t):
                    return scalar * x(t)

            else:
                raise TypeError(f"Unsupported input type for scaling: {type(x)}")

            # Compute norms
            norm_x = self.compute(x)
            norm_scaled_x = self.compute(scaled_x)

            # Check absolute homogeneity
            expected = abs(scalar) * norm_x
            # Allow for small numerical errors
            return abs(norm_scaled_x - expected) < 1e-10
        except Exception as e:
            logger.error(f"Error checking absolute homogeneity: {e}")
            return False
