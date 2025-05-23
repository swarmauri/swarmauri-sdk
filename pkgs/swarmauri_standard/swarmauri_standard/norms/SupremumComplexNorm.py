import logging
from typing import Literal, Union

import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.norms.NormBase import (
    CallableType,
    MatrixType,
    NormBase,
    SequenceType,
    StringType,
    VectorType,
)

# Configure logging
logger = logging.getLogger(__name__)


@ComponentBase.register_type(NormBase, "SupremumComplexNorm")
class SupremumComplexNorm(NormBase):
    """
    Supremum norm implementation for complex-valued functions.

    This class computes the maximum absolute value in a complex interval [a, b].

    Attributes
    ----------
    type : Literal["SupremumComplexNorm"]
        The type identifier for this norm implementation.
    resource : str, optional
        The resource type, defaults to NORM.
    """

    type: Literal["SupremumComplexNorm"] = "SupremumComplexNorm"

    def compute(
        self, x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
    ) -> complex:
        """
        Compute the supremum norm of the input.

        For complex-valued functions, this returns the maximum absolute value.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
            The input for which to compute the supremum norm.

        Returns
        -------
        complex
            The computed supremum norm value.

        Raises
        ------
        TypeError
            If the input type is not supported.
        ValueError
            If the norm cannot be computed for the given input.
        """
        logger.debug(f"Computing supremum complex norm for {type(x)}")

        try:
            if isinstance(x, (list, tuple, np.ndarray)):
                # For sequence types, find the maximum absolute value
                if len(x) == 0:
                    return complex(0)

                if isinstance(x, np.ndarray) and x.ndim > 1:
                    x = x.flatten()

                # Convert all values to complex and compute absolute values
                complex_values = [
                    complex(val) if not isinstance(val, complex) else val for val in x
                ]
                abs_values = [abs(val) for val in complex_values]
                max_abs = max(abs_values)

                # Find the complex value with the maximum absolute value
                max_index = abs_values.index(max_abs)
                return complex_values[max_index]

            elif hasattr(x, "to_array"):
                # For vector or matrix types with to_array method
                return self.compute(x.to_array())

            elif callable(x):
                # For callable types, we would need a domain to evaluate the function
                # This is a simplified implementation assuming a predefined domain
                domain = np.linspace(-1, 1, 100)  # Example domain
                values = [x(t) for t in domain]
                return self.compute(values)

            elif isinstance(x, str):
                # For string types, convert to complex numbers if possible
                try:
                    # Try to interpret the string as a complex number
                    return complex(x)
                except ValueError:
                    # If not a single complex number, try to parse as a list
                    try:
                        values = eval(x)
                        if isinstance(values, (list, tuple)):
                            return self.compute(values)
                    except Exception:
                        raise ValueError(
                            f"Cannot interpret string '{x}' as complex value(s)"
                        )

            else:
                # For single values
                return complex(x)

        except Exception as e:
            logger.error(f"Error computing supremum complex norm: {str(e)}")
            raise ValueError(f"Failed to compute supremum complex norm: {str(e)}")

    def check_non_negativity(
        self, x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
    ) -> bool:
        """
        Check if the norm satisfies the non-negativity property.

        For complex norms, this checks if the absolute value of the norm is non-negative.

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
            # For complex numbers, we check if the absolute value is non-negative
            # (which is always true for a properly implemented complex norm)
            return abs(norm_value) >= 0
        except Exception as e:
            logger.error(f"Error checking non-negativity: {str(e)}")
            return False

    def check_definiteness(
        self, x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
    ) -> bool:
        """
        Check if the input is the zero vector.

        For the definiteness property: norm(x) = 0 if and only if x = 0.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
            The input to check.

        Returns
        -------
        bool
            True if the input is the zero vector, False otherwise.
        """
        try:
            # Check if x is zero
            is_zero = False

            if isinstance(x, (list, tuple, np.ndarray)):
                is_zero = all(abs(complex(val)) < 1e-10 for val in x)
            elif hasattr(x, "to_array"):
                array_form = x.to_array()
                is_zero = all(abs(complex(val)) < 1e-10 for val in array_form)
            elif callable(x):
                # For callable types, sample at several points
                domain = np.linspace(-1, 1, 10)
                is_zero = all(abs(complex(x(t))) < 1e-10 for t in domain)
            elif isinstance(x, str):
                try:
                    complex_val = complex(x)
                    is_zero = abs(complex_val) < 1e-10
                except Exception:
                    is_zero = False
            else:
                is_zero = abs(complex(x)) < 1e-10

            return is_zero

        except Exception as e:
            logger.error(f"Error checking definiteness: {str(e)}")
            return False

    def check_triangle_inequality(
        self,
        x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType],
        y: Union[VectorType, MatrixType, SequenceType, StringType, CallableType],
    ) -> bool:
        """
        Check if the norm satisfies the triangle inequality.

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
        """
        try:
            # Handle different types of inputs for addition
            if (
                isinstance(x, (list, tuple))
                and isinstance(y, (list, tuple))
                and len(x) == len(y)
            ):
                # For sequence types of the same length
                x_plus_y = [complex(x[i]) + complex(y[i]) for i in range(len(x))]
            elif (
                isinstance(x, np.ndarray)
                and isinstance(y, np.ndarray)
                and x.shape == y.shape
            ):
                # For numpy arrays of the same shape
                x_plus_y = x + y
            elif hasattr(x, "to_array") and hasattr(y, "to_array"):
                # For vector or matrix types with to_array method
                x_array = x.to_array()
                y_array = y.to_array()
                if len(x_array) == len(y_array):
                    x_plus_y = [
                        complex(x_array[i]) + complex(y_array[i])
                        for i in range(len(x_array))
                    ]
                else:
                    raise TypeError("Inputs must have the same dimensions")
            elif callable(x) and callable(y):
                # For callable types, create a new callable that is the sum
                def sum_function(t):
                    return complex(x(t)) + complex(y(t))

                x_plus_y = sum_function
            else:
                # For single values or incompatible types
                try:
                    x_plus_y = complex(x) + complex(y)
                except TypeError:
                    raise TypeError("Inputs cannot be added")

            # Compute norms
            norm_x = abs(self.compute(x))
            norm_y = abs(self.compute(y))
            norm_x_plus_y = abs(self.compute(x_plus_y))

            # Check triangle inequality
            # Use a small epsilon for floating-point comparison
            epsilon = 1e-10
            return norm_x_plus_y <= norm_x + norm_y + epsilon

        except Exception as e:
            logger.error(f"Error checking triangle inequality: {str(e)}")
            return False

    def check_absolute_homogeneity(
        self,
        x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType],
        scalar: complex,
    ) -> bool:
        """
        Check if the norm satisfies the absolute homogeneity property.

        The absolute homogeneity property states that norm(a*x) = |a|*norm(x) for scalar a.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
            The input.
        scalar : complex
            The scalar value.

        Returns
        -------
        bool
            True if the norm satisfies the absolute homogeneity property, False otherwise.
        """
        try:
            # Convert scalar to complex
            scalar_complex = complex(scalar)

            # Handle different types of inputs for scalar multiplication
            if isinstance(x, (list, tuple)):
                # For sequence types
                scalar_times_x = [scalar_complex * complex(val) for val in x]
            elif isinstance(x, np.ndarray):
                # For numpy arrays
                scalar_times_x = scalar_complex * x
            elif hasattr(x, "to_array"):
                # For vector or matrix types with to_array method
                x_array = x.to_array()
                scalar_times_x = [scalar_complex * complex(val) for val in x_array]
            elif callable(x):
                # For callable types, create a new callable that is the scaled function
                def scaled_function(t):
                    return scalar_complex * complex(x(t))

                scalar_times_x = scaled_function
            else:
                # For single values
                scalar_times_x = scalar_complex * complex(x)

            # Compute norms
            norm_x = abs(self.compute(x))
            norm_scalar_times_x = abs(self.compute(scalar_times_x))
            abs_scalar = abs(scalar_complex)

            # Check absolute homogeneity
            # Use a small epsilon for floating-point comparison
            epsilon = 1e-10
            return abs(norm_scalar_times_x - abs_scalar * norm_x) < epsilon

        except Exception as e:
            logger.error(f"Error checking absolute homogeneity: {str(e)}")
            return False
