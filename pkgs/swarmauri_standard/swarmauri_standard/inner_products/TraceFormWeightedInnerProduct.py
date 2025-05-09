from typing import Literal
import numpy as np
import logging
from swarmauri_base.inner_products.InnerProductBase import InnerProductBase
from swarmauri_core.inner_products.IInnerProduct import IInnerProduct

logger = logging.getLogger(__name__)


@ComponentBase.register_type(InnerProductBase, "TraceFormWeightedInnerProduct")
class TraceFormWeightedInnerProduct(InnerProductBase):
    """Implementation of an inner product using weighted trace of matrix product.

    This class provides an implementation of the IInnerProduct interface that
    computes the inner product using the trace of the product of matrices
    modulated by an external weight matrix. The computation follows the formula:

    <x, y> = trace(x^T * W * y)

    Where W is the weight matrix provided during initialization.
    """

    type: Literal["TraceFormWeightedInnerProduct"] = "TraceFormWeightedInnerProduct"

    def __init__(self, weight_matrix: np.ndarray):
        """Initialize the TraceFormWeightedInnerProduct instance.

        Args:
            weight_matrix: The weight matrix W used in the computation
        """
        super().__init__()
        self._weight_matrix = weight_matrix

    def compute(self, x: IInnerProduct.IVector, y: IInnerProduct.IVector) -> float:
        """Compute the weighted trace inner product of two vectors.

        The computation follows the formula: trace(x^T * W * y)

        Args:
            x: First vector
            y: Second vector

        Returns:
            The computed inner product value

        Raises:
            ValueError: If dimensions of x, y, or weight matrix are incompatible
        """
        logger.debug("Computing weighted trace inner product")

        # Get underlying numpy arrays from vectors
        x_mat = x.get_matrix()
        y_mat = y.get_matrix()

        # Ensure compatible dimensions
        if x_mat.shape[0] != y_mat.shape[0]:
            raise ValueError("Incompatible vector dimensions")
        if x_mat.shape[0] != self._weight_matrix.shape[0]:
            raise ValueError("Weight matrix dimension mismatch")

        # Compute the product x^T * weight_matrix * y
        product = np.dot(x_mat.T, np.dot(self._weight_matrix, y_mat))

        # Return the trace of the product matrix
        return np.trace(product)

    def check_conjugate_symmetry(
        self, x: IInnerProduct.IVector, y: IInnerProduct.IVector
    ) -> bool:
        """Check if the inner product satisfies conjugate symmetry.

        Conjugate symmetry requires that <x, y> = conjugate(<y, x>)

        Args:
            x: First vector
            y: Second vector

        Returns:
            True if conjugate symmetry holds, False otherwise
        """
        logger.debug("Checking conjugate symmetry")
        inner_product_xy = self.compute(x, y)
        inner_product_yx = self.compute(y, x)

        # Check if inner_product_xy is the conjugate of inner_product_yx
        # and they are equal in real value
        return np.isclose(inner_product_xy, inner_product_yx.conjugate())

    def check_linearity_first_argument(
        self,
        x: IInnerProduct.IVector,
        y: IInnerProduct.IVector,
        z: IInnerProduct.IVector,
        a: float = 1.0,
        b: float = 1.0,
    ) -> bool:
        """Check linearity in the first argument.

        Linearity requires that <ax + by, z> = a<x, z> + b<y, z>

        Args:
            x: First vector
            y: Second vector
            z: Third vector
            a: Scalar coefficient for x
            b: Scalar coefficient for y

        Returns:
            True if linearity holds, False otherwise
        """
        logger.debug("Checking linearity in first argument")

        # Create new vectors for ax and by
        ax = x.scale(a)
        by = y.scale(b)
        ax_plus_by = ax.add(by)

        # Compute left-hand side
        lhs = self.compute(ax_plus_by, z)

        # Compute right-hand side
        rhs = a * self.compute(x, z) + b * self.compute(y, z)

        return np.isclose(lhs, rhs)

    def check_positivity(self, x: IInnerProduct.IVector) -> bool:
        """Check if the inner product is positive definite.

        Positive definiteness requires that <x, x> > 0 for all non-zero x

        Args:
            x: Vector to check

        Returns:
            True if positive definite, False otherwise
        """
        logger.debug("Checking positivity")
        value = self.compute(x, x)
        # Assuming real-valued inner product for simplicity
        return value > 0
