from typing import Union, Sequence
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.norms.NormBase import NormBase
import logging

logger = logging.getLogger(__name__)


@ComponentBase.register_type(NormBase, "L1ManhattanNorm")
class L1ManhattanNorm(NormBase):
    """
    Implementation of the L1 (Manhattan) norm for real vectors.

    Inherits From:
        NormBase: Base class for norm computations

    Attributes:
        type: Type identifier for this norm class
        resource: Type of resource this component represents
    """

    type: str = "L1ManhattanNorm"
    resource: str = "norm"

    def __init__(self):
        """
        Initialize the L1ManhattanNorm instance.
        """
        super().__init__()

    def compute(self, x: Union[Sequence, str, Callable]) -> float:
        """
        Compute the L1 (Manhattan) norm of a vector.

        The L1 norm is calculated as the sum of the absolute values of the vector components.

        Args:
            x: The input vector. Can be a sequence, string representation of a vector, or a callable.

        Returns:
            float: The computed L1 norm value.

        Raises:
            TypeError: If the input type is not supported
            ValueError: If the input cannot be converted to a valid vector
        """
        logger.debug("Computing L1 norm")

        try:
            # Convert input to a list of float values
            if isinstance(x, str):
                vector = list(map(float, x.strip().split()))
            elif isinstance(x, Callable):
                vector = x()
            else:
                vector = list(x)

            # Compute L1 norm as sum of absolute values
            norm = sum(abs(component) for component in vector)
            logger.debug(f"L1 norm computed: {norm}")
            return norm

        except TypeError as e:
            logger.error(f"TypeError in L1 computation: {str(e)}")
            raise TypeError(
                f"Unsupported type for L1 norm computation: {type(x)}"
            ) from e
        except Exception as e:
            logger.error(f"Error in L1 computation: {str(e)}")
            raise ValueError(f"Invalid input for L1 norm computation") from e

    def check_non_negativity(self, x: Union[Sequence, str, Callable]) -> None:
        """
        Verify the non-negativity property of the L1 norm.

        The norm must satisfy ||x|| >= 0 for all x, and ||x|| = 0 if and only if x = 0.

        Args:
            x: The input vector to verify non-negativity for.

        Raises:
            AssertionError: If non-negativity property is not satisfied
        """
        logger.debug("Checking non-negativity property")

        norm = self.compute(x)
        assert norm >= 0, "Non-negativity violation: Norm is negative"
        logger.debug("Non-negativity property verified")

    def check_triangle_inequality(
        self, x: Union[Sequence, str, Callable], y: Union[Sequence, str, Callable]
    ) -> None:
        """
        Verify the triangle inequality property of the L1 norm.

        The norm must satisfy ||x + y|| <= ||x|| + ||y|| for all x, y.

        Args:
            x: The first input vector
            y: The second input vector

        Raises:
            AssertionError: If triangle inequality property is not satisfied
        """
        logger.debug("Checking triangle inequality property")

        norm_x = self.compute(x)
        norm_y = self.compute(y)
        sum_xy = [
            x_i + y_i
            for x_i, y_i in zip(self._convert_to_vector(x), self._convert_to_vector(y))
        ]
        norm_sum = self.compute(sum_xy)

        assert norm_sum <= norm_x + norm_y, "Triangle inequality violation"
        logger.debug("Triangle inequality property verified")

    def check_absolute_homogeneity(
        self, x: Union[Sequence, str, Callable], alpha: float
    ) -> None:
        """
        Verify the absolute homogeneity property of the L1 norm.

        The norm must satisfy ||αx|| = |α| ||x|| for all scalars α and vectors x.

        Args:
            x: The input vector
            alpha: The scalar to scale the vector by

        Raises:
            AssertionError: If absolute homogeneity property is not satisfied
        """
        logger.debug("Checking absolute homogeneity property")

        scaled_vector = [alpha * component for component in self._convert_to_vector(x)]
        norm_scaled = self.compute(scaled_vector)
        norm_original = self.compute(x)

        assert norm_scaled == abs(alpha) * norm_original, (
            "Absolute homogeneity violation"
        )
        logger.debug("Absolute homogeneity property verified")

    def check_definiteness(self, x: Union[Sequence, str, Callable]) -> None:
        """
        Verify the definiteness property of the L1 norm.

        The norm must satisfy ||x|| = 0 if and only if x = 0.

        Args:
            x: The input vector to verify definiteness for.

        Raises:
            AssertionError: If definiteness property is not satisfied
        """
        logger.debug("Checking definiteness property")

        vector = self._convert_to_vector(x)
        norm = self.compute(vector)

        if norm == 0:
            assert all(component == 0 for component in vector), (
                "Definiteness violation: Non-zero vector with zero norm"
            )
        else:
            assert norm != 0, "Definiteness violation: Zero vector has non-zero norm"

        logger.debug("Definiteness property verified")

    def _convert_to_vector(self, x: Union[Sequence, str, Callable]) -> list:
        """
        Helper method to convert input to a list of float values.

        Args:
            x: The input to convert. Can be a sequence, string, or callable.

        Returns:
            list: The converted vector as a list of floats.

        Raises:
            ValueError: If conversion fails
        """
        try:
            if isinstance(x, str):
                return list(map(float, x.strip().split()))
            elif isinstance(x, Callable):
                return x()
            else:
                return list(x)
        except Exception as e:
            raise ValueError(f"Failed to convert input to vector: {str(e)}") from e
