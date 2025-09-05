import logging
from typing import Callable, Literal, Optional, Sequence, TypeVar, Union

import numpy as np
from pydantic import Field, validator
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


@ComponentBase.register_type(NormBase, "GeneralLpNorm")
class GeneralLpNorm(NormBase):
    """
    General Lp norm implementation with parameter p in (1, ∞).

    This class implements the Lp norm for various magnitudes of p on real-valued functions.
    The Lp norm of a vector x is defined as (sum(|x_i|^p))^(1/p) for finite p > 1.

    Attributes
    ----------
    type : Literal["GeneralLpNorm"]
        The type identifier for this norm.
    p : float
        The parameter p for the Lp norm. Must be finite and greater than 1.
    resource : str, optional
        The resource type, defaults to NORM.
    """

    type: Literal["GeneralLpNorm"] = "GeneralLpNorm"
    p: float = Field(..., description="Parameter p for the Lp norm (must be > 1)")
    resource: Optional[str] = Field(default=ResourceTypes.NORM.value)

    @validator("p")
    def validate_p(cls, v):
        """
        Validate that p is greater than 1 and finite.

        Parameters
        ----------
        v : float
            The value to validate.

        Returns
        -------
        float
            The validated value.

        Raises
        ------
        ValueError
            If p is not greater than 1 or is not finite.
        """
        if v <= 1:
            raise ValueError(f"Parameter p must be greater than 1, got {v}")
        if not np.isfinite(v):
            raise ValueError(f"Parameter p must be finite, got {v}")
        return v

    def _convert_to_array(
        self, x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
    ) -> np.ndarray:
        """
        Convert the input to a numpy array for computation.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
            The input to convert.

        Returns
        -------
        np.ndarray
            The converted numpy array.

        Raises
        ------
        TypeError
            If the input type is not supported.
        """
        if isinstance(x, IVector):
            return x.to_array()
        elif isinstance(x, IMatrix):
            return x.to_array().flatten()
        elif isinstance(x, Sequence) and not isinstance(x, str):
            return np.array(x, dtype=float)
        elif isinstance(x, str):
            # Convert string to array of ASCII values
            return np.array([ord(c) for c in x], dtype=float)
        elif callable(x):
            # For callable, we need to define a domain
            # This is a simplified example - in practice, this would depend on the context
            domain = np.linspace(0, 1, 100)
            return np.array([x(t) for t in domain], dtype=float)
        else:
            raise TypeError(f"Unsupported input type: {type(x)}")

    def compute(
        self, x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
    ) -> float:
        """
        Compute the Lp norm of the input.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
            The input for which to compute the norm.

        Returns
        -------
        float
            The computed Lp norm value.

        Raises
        ------
        TypeError
            If the input type is not supported.
        ValueError
            If the norm cannot be computed for the given input.
        """
        try:
            # Convert input to numpy array
            x_array = self._convert_to_array(x)

            # Compute Lp norm: (sum(|x_i|^p))^(1/p)
            norm_value = np.sum(np.abs(x_array) ** self.p) ** (1 / self.p)

            logger.debug(f"Computed Lp norm with p={self.p}: {norm_value}")
            return float(norm_value)
        except Exception as e:
            logger.error(f"Error computing Lp norm: {str(e)}")
            raise

    def check_non_negativity(
        self, x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
    ) -> bool:
        """
        Check if the Lp norm satisfies the non-negativity property.

        The Lp norm is always non-negative by definition.

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
            logger.debug(f"Non-negativity check result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in non-negativity check: {str(e)}")
            return False

    def check_definiteness(
        self, x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType]
    ) -> bool:
        """
        Check if the Lp norm satisfies the definiteness property.

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
            x_array = self._convert_to_array(x)
            norm_value = self.compute(x)

            # Check if norm is 0 iff x is 0 (all elements are 0)
            is_zero = np.allclose(x_array, 0)
            norm_is_zero = np.isclose(norm_value, 0)

            result = (is_zero and norm_is_zero) or (not is_zero and not norm_is_zero)
            logger.debug(f"Definiteness check result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in definiteness check: {str(e)}")
            return False

    def check_triangle_inequality(
        self,
        x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType],
        y: Union[VectorType, MatrixType, SequenceType, StringType, CallableType],
    ) -> bool:
        """
        Check if the Lp norm satisfies the triangle inequality.

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
        """
        try:
            x_array = self._convert_to_array(x)
            y_array = self._convert_to_array(y)

            # Ensure arrays have the same shape
            if x_array.shape != y_array.shape:
                raise TypeError(
                    "Inputs must have the same shape for triangle inequality check"
                )

            # Compute norms
            norm_x = self.compute(x)
            norm_y = self.compute(y)

            # Compute norm of sum
            sum_array = x_array + y_array
            norm_sum = np.sum(np.abs(sum_array) ** self.p) ** (1 / self.p)

            # Check triangle inequality
            result = (
                norm_sum <= norm_x + norm_y + 1e-10
            )  # Small epsilon for numerical stability
            logger.debug(f"Triangle inequality check result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in triangle inequality check: {str(e)}")
            return False

    def check_absolute_homogeneity(
        self,
        x: Union[VectorType, MatrixType, SequenceType, StringType, CallableType],
        scalar: float,
    ) -> bool:
        """
        Check if the Lp norm satisfies the absolute homogeneity property.

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
            x_array = self._convert_to_array(x)

            # Compute norm of x
            norm_x = self.compute(x)

            # Compute norm of scaled x
            scaled_array = scalar * x_array
            norm_scaled = np.sum(np.abs(scaled_array) ** self.p) ** (1 / self.p)

            # Check absolute homogeneity
            expected = abs(scalar) * norm_x
            result = np.isclose(norm_scaled, expected, rtol=1e-10, atol=1e-10)
            logger.debug(f"Absolute homogeneity check result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in absolute homogeneity check: {str(e)}")
            return False
