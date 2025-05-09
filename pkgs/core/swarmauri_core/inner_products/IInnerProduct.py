from abc import ABC, abstractmethod
from typing import Union
import numpy as np
from typing import Callable
import logging

from swarmauri_core.vectors.IVector import IVector

logger = logging.getLogger(__name__)


class IInnerProduct(ABC):
    """
    Defines the contract for inner product operations. This abstract base class
    specifies the interface that must be implemented by any concrete inner product
    implementation.

    The inner product operation is a fundamental operation in various numerical
    and machine learning applications, particularly in the context of vector spaces.
    Implementations of this interface must provide the compute method which
    calculates the inner product of two vectors, matrices or callables.

    The interface also specifies methods for checking the mathematical properties
    of the inner product implementation:
    - Conjugate Symmetry: <a, b> = conjugate(<b, a>)
    - Linearity in the First Argument
    - Positivity: <a, a> > 0 for non-zero vectors
    """

    @abstractmethod
    def compute(self, a: Union[IVector, np.ndarray, Callable], b: Union[IVector, np.ndarray, Callable]) -> float:
        """
        Computes the inner product between two vectors, matrices, or callables.

        Args:
            a: The first element in the inner product operation. Can be a vector,
               matrix, or callable.
            b: The second element in the inner product operation. Can be a vector,
               matrix, or callable.

        Returns:
            float: The result of the inner product operation.

        Raises:
            ValueError: If the input types are not supported or dimensions are incompatible
            ZeroDivisionError: If any operation leads to division by zero
        """
        pass

    def check_conjugate_symmetry(self, a: Union[IVector, np.ndarray, Callable], b: Union[IVector, np.ndarray, Callable]) -> None:
        """
        Verifies the conjugate symmetry property of the inner product implementation.

        The inner product <a, b> should be equal to the conjugate of <b, a>.

        Args:
            a: The first element in the inner product operation
            b: The second element in the inner product operation

        Raises:
            ValueError: If the conjugate symmetry property is not satisfied
        """
        inner_product_ab = self.compute(a, b)
        inner_product_ba = self.compute(b, a)
        
        if not np.isclose(inner_product_ab, np.conj(inner_product_ba)):
            logger.error("Conjugate symmetry check failed")
            raise ValueError("Conjugate symmetry property not satisfied")

    def check_linearity_first_argument(self, a: Union[IVector, np.ndarray, Callable], b: Union[IVector, np.ndarray, Callable], c: Union[IVector, np.ndarray, Callable]) -> None:
        """
        Verifies the linearity property in the first argument of the inner product implementation.

        For vectors a, b, c and scalar α:
        - Linearity: <a + b, c> = <a, c> + <b, c>
        - Homogeneity: <αa, c> = α <a, c>

        Args:
            a: The first vector for linearity check
            b: The second vector for linearity check
            c: The vector against which the inner product is computed

        Raises:
            ValueError: If the linearity property in the first argument is not satisfied
        """
        # Test additivity
        inner_product_sum = self.compute(a + b, c)
        inner_product_a = self.compute(a, c)
        inner_product_b = self.compute(b, c)
        
        if not np.isclose(inner_product_sum, inner_product_a + inner_product_b):
            logger.error("Additivity check failed")
            raise ValueError("Additivity property not satisfied")

        # Test homogeneity
        alpha = np.random.rand() + 1  # Random scalar > 0
        scaled_a = alpha * a
        inner_product_scaled = self.compute(scaled_a, c)
        expected = alpha * self.compute(a, c)
        
        if not np.isclose(inner_product_scaled, expected):
            logger.error("Homogeneity check failed")
            raise ValueError("Homogeneity property not satisfied")

    def check_positivity(self, a: Union[IVector, np.ndarray, Callable]) -> None:
        """
        Verifies the positivity property of the inner product implementation.

        For any non-zero vector a:
        - <a, a> > 0

        Args:
            a: The vector to check for positivity

        Raises:
            ValueError: If the positivity property is not satisfied
        """
        inner_product_aa = self.compute(a, a)
        
        if inner_product_aa <= 0:
            logger.error("Positivity check failed")
            raise ValueError("Positivity property not satisfied")