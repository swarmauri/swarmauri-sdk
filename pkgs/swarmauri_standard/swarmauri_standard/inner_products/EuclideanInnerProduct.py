from typing import Union, Literal
import numpy as np
import logging
from swarmauri_base.inner_products.InnerProductBase import InnerProductBase
from swarmauri_core.vectors.IVector import IVector

logger = logging.getLogger(__name__)


@ComponentBase.register_type(InnerProductBase, "EuclideanInnerProduct")
class EuclideanInnerProduct(InnerProductBase):
    type: Literal["EuclideanInnerProduct"] = "EuclideanInnerProduct"

    """
    Provides a concrete implementation of the InnerProductBase class for computing
    the Euclidean (L2) inner product. This implementation is suitable for real-
    valued, finite-dimensional vectors represented as numpy arrays or IVector objects.

    The Euclidean inner product is defined as the standard dot product in
    Euclidean geometry, which is computed as the sum of the element-wise products
    of the vectors. This implementation ensures that the input vectors are valid
    and real-valued before performing the computation.
    """

    def __init__(self) -> None:
        super().__init__()
        self.type = "EuclideanInnerProduct"

    def compute(self, a: Union[IVector, np.ndarray, Callable], 
                      b: Union[IVector, np.ndarray, Callable]) -> float:
        """
        Computes the Euclidean inner product (dot product) between two vectors.

        Args:
            a: The first vector in the inner product operation. This can be an
               instance of IVector, a numpy array, or a callable that returns
               a vector when called.
            b: The second vector in the inner product operation. This can be an
               instance of IVector, a numpy array, or a callable that returns
               a vector when called.

        Returns:
            float: The result of the Euclidean inner product operation.

        Raises:
            ValueError: If the input vectors are not compatible for the inner
                         product operation or if they contain non-real values.
            TypeError: If the input types are not supported.
        """
        try:
            # Convert inputs to numpy arrays if they are not already
            if callable(a):
                a = a()
            if callable(b):
                b = b()
            
            if isinstance(a, IVector):
                a = a.to_numpy()
            if isinstance(b, IVector):
                b = b.to_numpy()
            
            # Ensure inputs are numpy arrays
            if not isinstance(a, np.ndarray) or not isinstance(b, np.ndarray):
                raise TypeError("Inputs must be convertible to numpy arrays")
            
            # Verify that the arrays contain real numbers
            if a.dtype.kind not in ('f', 'i') or b.dtype.kind not in ('f', 'i'):
                raise ValueError("Input vectors must contain real numbers")
            
            # Compute the dot product
            result = np.dot(a, b)
            
            # Ensure the result is a scalar
            if np.isscalar(result):
                return float(result)
            else:
                raise ValueError("Result of the inner product is not a scalar")
            
        except ValueError as ve:
            logger.error(f"Value error in Euclidean inner product computation: {ve}")
            raise
        except TypeError as te:
            logger.error(f"Type error in Euclidean inner product computation: {te}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Euclidean inner product computation: {e}")
            raise