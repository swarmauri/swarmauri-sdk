from typing import Union, Literal
import numpy as np
import logging

from swarmauri_base.inner_products.InnerProductBase import InnerProductBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(InnerProductBase, "HermitianInnerProduct")
class HermitianInnerProduct(InnerProductBase):
    """
    Provides a concrete implementation of an inner product for complex vectors with
    Hermitian symmetry. This class handles inner product operations for complex
    vector spaces, ensuring conjugate symmetry and L2 structure.

    Inherits from:
        InnerProductBase: The base class for all inner product implementations.

    Implements:
        IInnerProduct: Interface for inner product operations.

    Properties:
        type: Literal["HermitianInnerProduct"] = "HermitianInnerProduct"
    """

    type: Literal["HermitianInnerProduct"] = "HermitianInnerProduct"

    def __init__(self) -> None:
        """
        Initializes the HermitianInnerProduct instance.
        """
        super().__init__()
        logger.debug("HermitianInnerProduct instance initialized")

    def compute(
        self,
        a: Union[IVector, np.ndarray, Callable],
        b: Union[IVector, np.ndarray, Callable],
    ) -> float:
        """
        Computes the Hermitian inner product of two complex vectors.

        The Hermitian inner product is defined as:
            ⟨a, b⟩ = conjugate(a) · b

        Args:
            a: The first complex vector or callable producing a complex vector
            b: The second complex vector or callable producing a complex vector

        Returns:
            float: The result of the inner product operation

        Raises:
            ValueError: If input vectors are not complex or dimensions don't match
        """
        logger.debug("Computing Hermitian inner product")

        # Evaluate callables if necessary
        if callable(a):
            a = a()
        if callable(b):
            b = b()

        # Ensure inputs are complex vectors
        if not (isinstance(a, (np.ndarray)) and isinstance(b, (np.ndarray))):
            raise ValueError(
                "Inputs must be complex vectors or callable producing complex vectors"
            )
        if a.dtype != np.complex_ or b.dtype != np.complex_:
            raise ValueError("Inputs must be complex vectors")

        # Ensure compatible dimensions
        if a.shape != b.shape:
            raise ValueError("Vector dimensions must match for inner product")

        # Compute the inner product with conjugate symmetry
        result = np.sum(np.conj(a) * b)

        logger.debug(f"Inner product result: {result}")
        return result

    def check_conjugate_symmetry(
        self,
        a: Union[IVector, np.ndarray, Callable],
        b: Union[IVector, np.ndarray, Callable],
    ) -> None:
        """
        Verifies the conjugate symmetry property of the inner product.

        For Hermitian inner product, we should have:
            ⟨a, b⟩ = conjugate(⟨b, a⟩)

        Args:
            a: The first vector for symmetry check
            b: The second vector for symmetry check

        Raises:
            ValueError: If conjugate symmetry is not satisfied
        """
        logger.debug("Checking conjugate symmetry")
        super().check_conjugate_symmetry(a, b)

    def check_linearity_first_argument(
        self,
        a: Union[IVector, np.ndarray, Callable],
        b: Union[IVector, np.ndarray, Callable],
        c: Union[IVector, np.ndarray, Callable],
    ) -> None:
        """
        Verifies the linearity property in the first argument.

        For vectors a, b, c and scalar α:
            ⟨a + b, c⟩ = ⟨a, c⟩ + ⟨b, c⟩
            ⟨αa, c⟩ = α ⟨a, c⟩

        Args:
            a: First vector for linearity check
            b: Second vector for linearity check
            c: Vector against which the inner product is computed

        Raises:
            ValueError: If linearity in the first argument is not satisfied
        """
        logger.debug("Checking linearity in first argument")
        super().check_linearity_first_argument(a, b, c)

    def check_positivity(self, a: Union[IVector, np.ndarray, Callable]) -> None:
        """
        Verifies the positivity property.

        For any non-zero vector a:
            ⟨a, a⟩ > 0

        Args:
            a: Vector to check for positivity

        Raises:
            ValueError: If positivity property is not satisfied
        """
        logger.debug("Checking positivity")
        super().check_positivity(a)

    def __str__(self) -> str:
        """
        Returns a string representation of the HermitianInnerProduct instance.
        """
        return f"HermitianInnerProduct()"

    def __repr__(self) -> str:
        """
        Returns the string representation of the HermitianInnerProduct instance.
        """
        return self.__str__()
