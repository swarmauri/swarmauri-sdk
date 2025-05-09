from typing import Callable, Union
import logging
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_base.seminorms.SeminormBase import SeminormBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SeminormBase, "LpSeminorm")
class LpSeminorm(SeminormBase):
    """
    A concrete implementation of the SeminormBase class for the Lp seminorm.

    This class provides functionality to compute the Lp seminorm for different types of inputs.
    The Lp seminorm is defined as the p-th root of the sum of the absolute values of the elements
    raised to the power of p. It is a non-point-separating seminorm, meaning it might not distinguish
    all vectors.

    Attributes:
        p: float
            The order of the Lp seminorm. Must be in the range (0, ∞).

    Methods:
        compute: Computes the Lp seminorm for the given input.
        check_triangle_inequality: Checks if the triangle inequality holds for the given elements.
        check_scalar_homogeneity: Checks if the scalar homogeneity property holds.
    """

    def __init__(self, p: float):
        """
        Initializes the LpSeminorm instance with the given order p.

        Args:
            p: float - The order of the Lp seminorm. Must be greater than 0.

        Raises:
            ValueError: If p is not in the range (0, ∞)
        """
        super().__init__()
        if not (0 < p < float("inf")):
            raise ValueError("p must be in the range (0, ∞)")
        self.p = p
        logger.debug(f"Initialized LpSeminorm with p={p}")

    def compute(
        self, input: Union[IVector, IMatrix, str, Callable, list, tuple]
    ) -> float:
        """
        Computes the Lp seminorm for the given input.

        Args:
            input: Union[IVector, IMatrix, str, Callable, list, tuple] - The input to compute the seminorm for.
                Supported types are:
                - IVector: High-dimensional vector
                - IMatrix: Matrix structure
                - str: String input
                - Callable: Callable function
                - list: List of elements
                - tuple: Tuple of elements

        Returns:
            float: The computed Lp seminorm value.

        Raises:
            TypeError: If input type is not supported
            ValueError: If the input cannot be processed
        """
        logger.debug(f"Computing Lp seminorm for input of type {type(input).__name__}")

        if self._is_vector(input):
            vector = input
            elements = vector.get_elements()
        elif self._is_matrix(input):
            matrix = input
            elements = matrix.flatten()
        elif self._is_sequence(input):
            elements = list(input)
        elif isinstance(input, str):
            try:
                elements = [float(input)]
            except ValueError:
                raise ValueError(f"Cannot convert string '{input}' to float")
        elif self._is_callable(input):
            # For callables, we would need to define how to compute the seminorm
            # For example, integrate over a domain. This is a placeholder.
            logger.warning("Callable input type is not fully implemented")
            return 0.0
        else:
            raise TypeError(f"Unsupported input type: {type(input).__name__}")

        if not elements:
            return 0.0

        sum_powers = sum(abs(e) ** self.p for e in elements)
        if sum_powers == 0:
            return 0.0
        return sum_powers ** (1.0 / self.p)

    def check_triangle_inequality(
        self,
        a: Union[IVector, IMatrix, str, Callable, list, tuple],
        b: Union[IVector, IMatrix, str, Callable, list, tuple],
    ) -> bool:
        """
        Checks if the triangle inequality holds for the given elements a and b.

        The triangle inequality states that:
        seminorm(a + b) <= seminorm(a) + seminorm(b)

        Args:
            a: Union[IVector, IMatrix, str, Callable, list, tuple] - First element to check
            b: Union[IVector, IMatrix, str, Callable, list, tuple] - Second element to check

        Returns:
            bool: True if the triangle inequality holds, False otherwise
        """
        logger.debug("Checking triangle inequality")

        seminorm_a = self.compute(a)
        seminorm_b = self.compute(b)
        if seminorm_a == 0 and seminorm_b == 0:
            return True

        try:
            a_plus_b = a + b
        except TypeError:
            logger.warning("Could not add elements a and b")
            return False

        seminorm_a_plus_b = self.compute(a_plus_b)

        return seminorm_a_plus_b <= seminorm_a + seminorm_b

    def check_scalar_homogeneity(
        self,
        a: Union[IVector, IMatrix, str, Callable, list, tuple],
        scalar: Union[int, float],
    ) -> bool:
        """
        Checks if the scalar homogeneity property holds for the given element a and scalar.

        The scalar homogeneity property states that:
        seminorm(s * a) = |s| * seminorm(a)

        Args:
            a: Union[IVector, IMatrix, str, Callable, list, tuple] - Element to check
            scalar: Union[int, float] - Scalar value to scale with

        Returns:
            bool: True if the scalar homogeneity holds, False otherwise
        """
        logger.debug(f"Checking scalar homogeneity with scalar {scalar}")

        seminorm_a = self.compute(a)
        if seminorm_a == 0:
            return True

        try:
            scaled_a = scalar * a
        except TypeError:
            logger.warning(f"Could not scale element a with scalar {scalar}")
            return False

        seminorm_scaled_a = self.compute(scaled_a)
        expected = abs(scalar) * seminorm_a

        return seminorm_scaled_a == expected

    def __str__(self) -> str:
        """
        Returns a string representation of the LpSeminorm instance.

        Returns:
            str: String representation
        """
        return f"LpSeminorm(p={self.p})"

    def __repr__(self) -> str:
        """
        Returns the official string representation of the LpSeminorm instance.

        Returns:
            str: Official string representation
        """
        return self.__str__()
