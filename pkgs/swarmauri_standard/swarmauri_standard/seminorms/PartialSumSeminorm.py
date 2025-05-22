import logging
from typing import Literal, Optional, Sequence, Union

import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.seminorms.SeminormBase import SeminormBase
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.seminorms.ISeminorm import InputType, T
from swarmauri_core.vectors.IVector import IVector

# Configure logging
logger = logging.getLogger(__name__)


@ComponentBase.register_type(SeminormBase, "PartialSumSeminorm")
class PartialSumSeminorm(SeminormBase):
    """
    Seminorm computed via summing only part of the vector.

    This seminorm evaluates the norm on a partial segment of the input,
    ignoring the rest. It is particularly useful when only specific
    elements of a vector or matrix are relevant for a given analysis.

    Attributes
    ----------
    type : Literal["PartialSumSeminorm"]
        The type identifier for this seminorm
    start_idx : Optional[int]
        Starting index for the summation (inclusive)
    end_idx : Optional[int]
        Ending index for the summation (exclusive)
    indices : Optional[Sequence[int]]
        Specific indices to include in the summation
    """

    type: Literal["PartialSumSeminorm"] = "PartialSumSeminorm"
    start_idx: Optional[int] = None
    end_idx: Optional[int] = None
    indices: Optional[Sequence[int]] = None

    def __init__(
        self,
        start_idx: Optional[int] = None,
        end_idx: Optional[int] = None,
        indices: Optional[Sequence[int]] = None,
        **kwargs,
    ):
        """
        Initialize the PartialSumSeminorm.

        Parameters
        ----------
        start_idx : Optional[int], optional
            Starting index for the summation (inclusive), by default None
        end_idx : Optional[int], optional
            Ending index for the summation (exclusive), by default None
        indices : Optional[Sequence[int]], optional
            Specific indices to include in the summation, by default None

        Notes
        -----
        Either provide start_idx and end_idx to define a range, or
        provide indices to specify exact elements to include.
        """
        super().__init__(**kwargs)
        self.start_idx = start_idx
        self.end_idx = end_idx
        self.indices = indices

        # Validate that we have either range or indices
        if (start_idx is None or end_idx is None) and indices is None:
            logger.warning(
                "Neither range nor indices specified. Will use entire input."
            )
        elif indices is not None and (start_idx is not None or end_idx is not None):
            logger.warning("Both range and indices provided. Will use indices.")

        logger.debug(
            f"Initialized PartialSumSeminorm with start_idx={start_idx}, "
            f"end_idx={end_idx}, indices={indices}"
        )

    def _extract_partial_data(self, x: Union[Sequence, np.ndarray]) -> np.ndarray:
        """
        Extract the partial data from the input based on configured indices.

        Parameters
        ----------
        x : Union[Sequence, np.ndarray]
            Input data to extract partial elements from

        Returns
        -------
        np.ndarray
            Array containing only the selected elements

        Raises
        ------
        ValueError
            If indices are out of bounds
        """
        try:
            # Convert to numpy array for easier manipulation
            data = np.asarray(x)

            # Use indices if provided, otherwise use range
            if self.indices is not None:
                # Check if any indices are out of bounds
                if max(self.indices) >= len(data) or min(self.indices) < 0:
                    raise ValueError(
                        f"Indices {self.indices} out of bounds for input of length {len(data)}"
                    )
                return data[list(self.indices)]
            elif self.start_idx is not None and self.end_idx is not None:
                # Check if range is valid
                if self.start_idx < 0 or self.end_idx > len(data):
                    raise ValueError(
                        f"Range [{self.start_idx}:{self.end_idx}] out of bounds "
                        f"for input of length {len(data)}"
                    )
                return data[self.start_idx : self.end_idx]
            else:
                # Use entire input if no indices or range specified
                return data
        except Exception as e:
            logger.error(f"Error extracting partial data: {str(e)}")
            raise

    def compute(self, x: InputType) -> float:
        """
        Compute the seminorm by summing the absolute values of the partial vector elements.

        Parameters
        ----------
        x : InputType
            The input to compute the seminorm for

        Returns
        -------
        float
            The seminorm value

        Raises
        ------
        TypeError
            If the input type is not supported
        ValueError
            If the computation cannot be performed on the given input
        """
        logger.debug(f"Computing PartialSumSeminorm for input of type {type(x)}")

        try:
            # Handle different input types
            if isinstance(x, (IVector, Sequence, list, tuple, str)):
                if isinstance(x, str):
                    # Convert string to ASCII values
                    x = [ord(char) for char in x]

                # Convert to flat array and extract partial data
                partial_data = self._extract_partial_data(x)
                # Sum absolute values
                return float(np.sum(np.abs(partial_data)))

            elif isinstance(x, (IMatrix, np.ndarray)):
                # Flatten matrix/array and extract partial data
                flat_data = np.asarray(x).flatten()
                partial_data = self._extract_partial_data(flat_data)
                # Sum absolute values
                return float(np.sum(np.abs(partial_data)))

            elif callable(x):
                # For callable objects, we need a domain to evaluate on
                domain = np.linspace(-1, 1, 100)
                values = np.array([x(t) for t in domain])
                partial_data = self._extract_partial_data(values)
                # Sum absolute values
                return float(np.sum(np.abs(partial_data)))

            else:
                raise TypeError(f"Unsupported input type: {type(x)}")

        except Exception as e:
            logger.error(f"Error computing PartialSumSeminorm: {str(e)}")
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
            # Ensure inputs are of the same type
            if type(x) is not type(y):
                raise TypeError(
                    f"Inputs must be of the same type, got {type(x)} and {type(y)}"
                )

            # Handle different input types
            if isinstance(x, (IVector, Sequence, list, tuple)):
                # Ensure inputs have the same length
                if len(x) != len(y):
                    raise ValueError(
                        f"Inputs must have the same length, got {len(x)} and {len(y)}"
                    )

                # Compute the sum of x and y
                z = [x[i] + y[i] for i in range(len(x))]

            elif isinstance(x, IMatrix):
                # Ensure matrices have the same shape
                x_array = np.asarray(x)
                y_array = np.asarray(y)
                if x_array.shape != y_array.shape:
                    raise ValueError(
                        f"Matrices must have the same shape, got {x_array.shape} and {y_array.shape}"
                    )

                # Compute the sum of x and y
                z = x_array + y_array

            elif isinstance(x, str):
                # For strings, we'll convert to ASCII and add
                x_ascii = [ord(char) for char in x]
                y_ascii = [ord(char) for char in y]
                if len(x_ascii) != len(y_ascii):
                    raise ValueError(
                        f"Strings must have the same length, got {len(x)} and {len(y)}"
                    )

                z = [x_ascii[i] + y_ascii[i] for i in range(len(x_ascii))]

            elif callable(x):
                # For callable objects, create a new callable that returns the sum
                def z(t):
                    return x(t) + y(t)

            else:
                raise TypeError(f"Unsupported input type: {type(x)}")

            # Check triangle inequality
            norm_x_plus_y = self.compute(z)
            norm_x = self.compute(x)
            norm_y = self.compute(y)

            # Account for floating-point precision issues
            epsilon = 1e-10
            return norm_x_plus_y <= norm_x + norm_y + epsilon

        except Exception as e:
            logger.error(f"Error checking triangle inequality: {str(e)}")
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
            # Handle different input types
            if isinstance(x, (IVector, Sequence, list, tuple)):
                # Multiply each element by alpha
                scaled_x = [alpha * xi for xi in x]

            elif isinstance(x, IMatrix):
                # Multiply matrix by alpha
                x_array = np.asarray(x)
                scaled_x = alpha * x_array

            elif isinstance(x, str):
                # For strings, we'll convert to ASCII and scale
                x_ascii = [ord(char) for char in x]
                scaled_x = [alpha * val for val in x_ascii]

            elif callable(x):
                # For callable objects, create a new callable that returns the scaled value
                def scaled_x(t):
                    return alpha * x(t)

            else:
                raise TypeError(f"Unsupported input type: {type(x)}")

            # Check scalar homogeneity
            norm_scaled_x = self.compute(scaled_x)
            norm_x = self.compute(x)
            abs_alpha = abs(alpha)

            # Account for floating-point precision issues
            epsilon = 1e-10
            return abs(norm_scaled_x - abs_alpha * norm_x) < epsilon

        except Exception as e:
            logger.error(f"Error checking scalar homogeneity: {str(e)}")
            raise
