from typing import Union, Literal
import numpy as np
import logging
from swarmauri_base.inner_products.InnerProductBase import InnerProductBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(InnerProductBase, "TraceFormWeightedInnerProduct")
class TraceFormWeightedInnerProduct(InnerProductBase):
    """
    Provides a concrete implementation of an inner product based on the weighted trace of matrix product.

    This class computes the inner product using the trace of the product of two matrices, modulated by a weight matrix.
    """

    type: Literal["TraceFormWeightedInnerProduct"] = "TraceFormWeightedInnerProduct"

    def __init__(self, weight: np.ndarray):
        """
        Initializes the TraceFormWeightedInnerProduct instance with the specified weight matrix.

        Args:
            weight: A numpy array representing the weight matrix used to modulate the trace.

        Raises:
            ValueError: If the weight matrix is not a valid numpy array.
        """
        super().__init__()
        if not isinstance(weight, np.ndarray):
            raise ValueError("Weight must be a numpy array")
        self.weight = weight

    def compute(
        self, a: Union[np.ndarray, Callable], b: Union[np.ndarray, Callable]
    ) -> float:
        """
        Computes the inner product using the weighted trace of matrix product.

        The computation is performed as follows:
        1. Convert inputs to matrices if they are callables.
        2. Compute the matrix product of a and the transpose of b.
        3. Element-wise multiply the product with the weight matrix.
        4. Compute the trace of the resulting matrix.

        Args:
            a: The first matrix or callable that returns a matrix.
            b: The second matrix or callable that returns a matrix.

        Returns:
            float: The result of the weighted trace inner product.

        Raises:
            ValueError: If the matrix dimensions are incompatible for multiplication.
        """
        logger.debug("Computing weighted trace inner product")

        # Convert callables to matrices
        if callable(a):
            a_matrix = a()
        else:
            a_matrix = a

        if callable(b):
            b_matrix = b()
        else:
            b_matrix = b

        # Ensure inputs are numpy arrays
        a_matrix = np.asarray(a_matrix)
        b_matrix = np.asarray(b_matrix)

        # Compute matrix product
        try:
            product_matrix = np.matmul(a_matrix, b_matrix.T)
        except ValueError as e:
            logger.error("Matrix dimensions are incompatible for multiplication")
            raise ValueError("Incompatible matrix dimensions for multiplication") from e

        # Verify weight matrix dimensions match product matrix
        if product_matrix.shape != self.weight.shape:
            logger.error("Weight matrix dimensions do not match product matrix")
            raise ValueError(
                "Weight matrix dimensions do not match product matrix dimensions"
            )

        # Apply weight element-wise
        weighted_product = np.multiply(product_matrix, self.weight)

        # Compute and return trace
        trace_result = np.trace(weighted_product)
        logger.debug("Weighted trace computation completed successfully")
        return float(trace_result)
