from abc import ABC, abstractmethod
from typing import Union, Optional
import logging

# Define logger
logger = logging.getLogger(__name__)

# Type alias for vector types
IVector = "IVector"

# Type alias for matrix types
Matrix = "Matrix"

# Type alias for callable types
Callable = "Callable"

class IInnerProduct(ABC):
    """
    Defines the interface for computing inner products between vectors, matrices, and callables.
    This interface enforces implementation of core inner product properties and checks.
    """

    @abstractmethod
    def compute(self, a: Union[IVector, Matrix, Callable], b: Union[IVector, Matrix, Callable]) -> Union[float, complex]:
        """
        Computes the inner product between two vectors, matrices, or callables.

        Args:
            a: The first element in the inner product operation. Can be a vector, matrix, or callable.
            b: The second element in the inner product operation. Can be a vector, matrix, or callable.

        Returns:
            Union[float, complex]: The result of the inner product computation.
        """
        pass

    def check_conjugate_symmetry(self, a: Union[IVector, Matrix, Callable], b: Union[IVector, Matrix, Callable]) -> bool:
        """
        Checks if the inner product implementation satisfies conjugate symmetry.
        For any elements a and b, the inner product of a and b should equal the conjugate of the inner product of b and a.

        Args:
            a: The first element to check
            b: The second element to check

        Returns:
            bool: True if conjugate symmetry holds, False otherwise
        """
        logger.info("Checking conjugate symmetry")
        result_ab = self.compute(a, b)
        result_ba = self.compute(b, a)
        
        # Check if result_ab equals the conjugate of result_ba
        if result_ab == result_ba.conjugate():
            logger.info("Conjugate symmetry check passed")
            return True
        else:
            logger.warning("Conjugate symmetry check failed")
            return False

    def check_linearity_first_argument(self, a: Union[IVector, Matrix, Callable], b: Union[IVector, Matrix, Callable], c: Union[IVector, Matrix, Callable]) -> bool:
        """
        Checks if the inner product implementation is linear in the first argument.
        For any elements a, b, and scalar s, the inner product of (a + b) with c should equal the sum of the inner products of a and b with c.
        Similarly, the inner product of (s * a) with b should equal s times the inner product of a and b.

        Args:
            a: The first element for linearity check
            b: The second element for linearity check
            c: The third element for linearity check

        Returns:
            bool: True if linearity in the first argument holds, False otherwise
        """
        logger.info("Checking linearity in first argument")
        
        # Check additivity
        result_add = self.compute(a + b, c)
        result_split = self.compute(a, c) + self.compute(b, c)
        
        if result_add != result_split:
            logger.warning("Additivity check failed")
            return False

        # Check homogeneity
        scalar = 2.0
        result_scale = self.compute(scalar * a, c)
        result_scaled = scalar * self.compute(a, c)
        
        if result_scale != result_scaled:
            logger.warning("Homogeneity check failed")
            return False

        logger.info("Linearity check passed")
        return True

    def check_positivity(self, a: Union[IVector, Matrix, Callable]) -> bool:
        """
        Checks if the inner product implementation satisfies positive definiteness.
        For any non-zero element a, the inner product of a with itself should be positive.

        Args:
            a: The element to check for positivity

        Returns:
            bool: True if positivity holds, False otherwise
        """
        logger.info("Checking positivity")
        result = self.compute(a, a)
        
        if result > 0:
            logger.info("Positivity check passed")
            return True
        else:
            logger.warning("Positivity check failed")
            return False