from typing import Literal
from swarmauri_base.ComponentBase import ComponentBase
from base.swarmauri_base.inner_products.InnerProductBase import InnerProductBase
from base.swarmauri_core.inner_products.IInnerProduct import IInnerProduct
from base.swarmauri_standard.kernels.Kernel import Kernel
import logging

logger = logging.getLogger(__name__)


@ComponentBase.register_type(InnerProductBase, "RKHSInnerProduct")
class RKHSInnerProduct(InnerProductBase):
    """Implementation of the InnerProductBase interface using a Reproducing Kernel Hilbert Space (RKHS) kernel.

    This class provides an inner product implementation based on kernel evaluation in an RKHS.
    The inner product is defined as the evaluation of a positive-definite kernel function
    at pairs of vectors.

    Attributes:
        kernel: The kernel object used to compute the inner product.
    """

    type: Literal["RKHSInnerProduct"] = "RKHSInnerProduct"

    def __init__(self, kernel: Kernel):
        """Initialize the RKHSInnerProduct with a kernel.

        Args:
            kernel: The kernel object that will be used to compute inner products.
                  Must be a positive-definite kernel.
        """
        super().__init__()
        self.kernel = kernel

    def compute(self, x: IInnerProduct.IVector, y: IInnerProduct.IVector) -> float:
        """Compute the inner product between two vectors using the kernel.

        The inner product is defined as the evaluation of the kernel at the pair (x, y):
        <x, y> = k(x, y)

        Args:
            x: First vector
            y: Second vector

        Returns:
            The value of the inner product as a scalar.

        Raises:
            ValueError: If the kernel is not positive-definite
        """
        logger.debug(f"Computing inner product using kernel {self.kernel.__class__.__name__}")
        
        # Evaluate the kernel at x and y
        return self.kernel.evaluate(x, y)

    def check_conjugate_symmetry(self, x: IInnerProduct.IVector, y: IInnerProduct.IVector) -> bool:
        """Check if the inner product satisfies conjugate symmetry.

        For the RKHS inner product, this requires that:
        k(x, y) = conjugate(k(y, x))

        Args:
            x: First vector
            y: Second vector

        Returns:
            True if conjugate symmetry holds, False otherwise.
        """
        logger.debug("Checking conjugate symmetry")
        
        # Compute both directions
        k_xy = self.compute(x, y)
        k_yx = self.compute(y, x)
        
        # Check if they are conjugate symmetric
        return k_xy == k_yx.conjugate()

    def check_linearity_first_argument(self, 
                                      x: IInnerProduct.IVector, 
                                      y: IInnerProduct.IVector, 
                                      z: IInnerProduct.IVector,
                                      a: float = 1.0, 
                                      b: float = 1.0) -> bool:
        """Check if the inner product is linear in the first argument.

        Linearity requires that:
        <a*x + b*y, z> = a*<x, z> + b*<y, z>

        Args:
            x: First vector
            y: Second vector
            z: Third vector
            a: Scalar coefficient for x
            b: Scalar coefficient for y

        Returns:
            True if linearity holds, False otherwise.
        """
        logger.debug("Checking linearity in first argument")
        
        # Compute left-hand side: <a*x + b*y, z>
        lhs = self.compute(x * a + y * b, z)
        
        # Compute right-hand side: a*<x, z> + b*<y, z>
        rhs = a * self.compute(x, z) + b * self.compute(y, z)
        
        # Compare with some tolerance for floating point errors
        return abs(lhs - rhs) < 1e-12

    def check_positivity(self, x: IInnerProduct.IVector) -> bool:
        """Check if the inner product is positive definite.

        Positive definiteness requires that for any non-zero vector x:
        <x, x> > 0

        Args:
            x: Vector to check

        Returns:
            True if positive definite, False otherwise.
        """
        logger.debug("Checking positive definiteness")
        
        # Compute the inner product of x with itself
        value = self.compute(x, x)
        
        # Check if it's positive and x is non-zero
        return value > 0 and x.norm() > 0