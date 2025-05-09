from typing import Callable, Union, Literal
import numpy as np
import logging

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.inner_products.InnerProductBase import InnerProductBase
from swarmauri_core.vectors.IVector import IVector

logger = logging.getLogger(__name__)


@ComponentBase.register_type(InnerProductBase, "FrobeniusRealInnerProduct")
class FrobeniusRealInnerProduct(InnerProductBase):
    """
    Provides a concrete implementation of the Frobenius inner product for real-valued matrices.

    This class implements the InnerProductBase interface to compute the inner product
    between two real matrices using the Frobenius inner product, which is equivalent
    to the trace of the matrix product of the transpose of the first matrix with
    the second matrix.

    Inherits From:
        InnerProductBase: The base class for all inner product implementations.
    """

    type: Literal["FrobeniusRealInnerProduct"] = "FrobeniusRealInnerProduct"

    def __init__(self):
        """
        Initializes the FrobeniusRealInnerProduct instance.
        """
        super().__init__()

    def compute(
        self,
        a: Union[IVector, np.ndarray, Callable],
        b: Union[IVector, np.ndarray, Callable],
    ) -> float:
        """
        Computes the Frobenius inner product between two real matrices.

        The Frobenius inner product is computed as the sum of the element-wise
        products of the two matrices. This is equivalent to the trace of the
        product of the transpose of the first matrix and the second matrix.

        Args:
            a: The first real matrix.
            b: The second real matrix.

        Returns:
            float: The result of the Frobenius inner product.

        Raises:
            ValueError: If the input matrices are not of the same shape.
        """
        logger.debug("Starting computation of Frobenius inner product")

        # Convert inputs to numpy arrays if they are not already
        a = np.asarray(a)
        b = np.asarray(b)

        # Check if matrices have the same shape
        if a.shape != b.shape:
            raise ValueError("Input matrices must have the same shape")

        # Compute element-wise product and sum all elements
        inner_product = np.sum(a * b)

        logger.debug(f"Frobenius inner product result: {inner_product}")
        return float(inner_product)

    def check_conjugate_symmetry(
        self,
        a: Union[IVector, np.ndarray, Callable],
        b: Union[IVector, np.ndarray, Callable],
    ) -> None:
        """
        Verifies the conjugate symmetry property for the Frobenius inner product.

        For real matrices, the Frobenius inner product is symmetric, meaning
        <a, b> = <b, a>. This method checks that property.

        Args:
            a: The first matrix.
            b: The second matrix.

        Raises:
            ValueError: If the conjugate symmetry property is not satisfied.
        """
        # Convert inputs to numpy arrays if they are not already
        a = np.asarray(a)
        b = np.asarray(b)

        # Compute inner products
        inner_ab = self.compute(a, b)
        inner_ba = self.compute(b, a)

        # Check symmetry
        if not np.isclose(inner_ab, inner_ba):
            raise ValueError("Conjugate symmetry property not satisfied")

    def __repr__(self) -> str:
        """
        Returns a string representation of the class instance.
        """
        return "FrobeniusRealInnerProduct()"
