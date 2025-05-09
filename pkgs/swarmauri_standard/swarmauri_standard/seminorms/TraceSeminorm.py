from typing import TypeVar, Union, Optional, Literal
import logging
import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.seminorms.ISeminorm import ISeminorm

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar("T", Union[np.ndarray, np.matrix, str, callable])


@ComponentBase.register_model()
class TraceSeminorm(SeminormBase):
    """
    A concrete implementation of SeminormBase for computing the trace seminorm.

    This class implements the trace seminorm computation for matrices. The trace
    seminorm is computed as the absolute value of the trace of the matrix. The
    trace is the sum of the diagonal elements of the matrix. This implementation
    does not guarantee positive-definiteness.

    Attributes:
        resource: Optional[str] = ResourceTypes.SEMINORM.value
            The resource type identifier for this component.
    """

    resource: str = ComponentBase.ResourceTypes.SEMINORM.value

    def __init__(self):
        """
        Initialize the TraceSeminorm instance.
        """
        super().__init__()
        self._name = "TraceSeminorm"

    def compute(self, input: T) -> float:
        """
        Compute the trace seminorm of the given input.

        The input can be a matrix or a callable that returns a matrix when called.
        The trace seminorm is computed as the absolute value of the trace of the matrix.

        Args:
            input: T
                The input to compute the seminorm on. This can be a matrix or a callable.

        Returns:
            float:
                The computed trace seminorm value.

        Raises:
            ValueError:
                If the input is neither a matrix nor a callable that returns a matrix.
        """
        logger.debug("Computing trace seminorm")

        # Check if the input is a callable
        if callable(input):
            matrix = input()
        else:
            matrix = input

        # Verify that the input is a matrix
        if not isinstance(matrix, (np.ndarray, np.matrix)):
            raise ValueError(
                "Input must be a matrix or a callable that returns a matrix"
            )

        # Compute the trace
        trace = np.trace(matrix)

        # The trace seminorm is the absolute value of the trace
        seminorm_value = abs(trace)

        logger.debug(f"Computed trace seminorm: {seminorm_value}")
        return seminorm_value

    def check_triangle_inequality(self, a: T, b: T) -> bool:
        """
        Check if the triangle inequality holds for the given inputs.

        The triangle inequality states that for any two matrices a and b:
        trace_seminorm(a + b) <= trace_seminorm(a) + trace_seminorm(b)

        Args:
            a: T
                The first matrix or callable that returns a matrix.
            b: T
                The second matrix or callable that returns a matrix.

        Returns:
            bool:
                True if the triangle inequality holds, False otherwise.
        """
        logger.debug("Checking triangle inequality")

        # Compute seminorms
        seminorm_a = self.compute(a)
        seminorm_b = self.compute(b)

        # Compute a + b if they are matrices
        if not callable(a) and not callable(b):
            a_matrix = a
            b_matrix = b
            a_plus_b = a_matrix + b_matrix
        else:
            # If either is callable, we need to get their matrix forms
            a_matrix = a() if callable(a) else a
            b_matrix = b() if callable(b) else b
            a_plus_b = a_matrix + b_matrix

        seminorm_a_plus_b = self.compute(a_plus_b)

        # Check inequality
        holds = seminorm_a_plus_b <= (seminorm_a + seminorm_b)

        logger.debug(f"Triangle inequality holds: {holds}")
        return holds

    def check_scalar_homogeneity(self, a: T, scalar: float) -> bool:
        """
        Check if scalar homogeneity holds for the given input and scalar.

        Scalar homogeneity states that for any matrix a and scalar c >= 0:
        trace_seminorm(c * a) = c * trace_seminorm(a)

        Args:
            a: T
                The input to check.
            scalar: float
                The scalar to check against.

        Returns:
            bool:
                True if scalar homogeneity holds, False otherwise.
        """
        logger.debug("Checking scalar homogeneity")

        # Compute original seminorm
        original_seminorm = self.compute(a)

        # Compute scaled matrix
        if callable(a):
            scaled_matrix = scalar * a()
        else:
            scaled_matrix = scalar * a

        # Compute seminorm of scaled matrix
        scaled_seminorm = self.compute(scaled_matrix)

        # Check homogeneity
        homogeneous = np.isclose(scaled_seminorm, scalar * original_seminorm)

        logger.debug(f"Scalar homogeneity holds: {homogeneous}")
        return homogeneous
