import logging
from typing import Callable, Optional, Union

import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.inner_products.InnerProductBase import InnerProductBase

from swarmauri_standard.vectors.Vector import Vector

logger = logging.getLogger(__name__)


@ComponentBase.register_type(InnerProductBase, "RKHSInnerProduct")
class RKHSInnerProduct(InnerProductBase):
    """Implements an inner product induced by a reproducing kernel.

    This class provides an implementation of the inner product in a Reproducing
    Kernel Hilbert Space (RKHS). The inner product is defined through evaluation
    of a positive-definite kernel function.

    Attributes:
        kernel: The kernel function used to induce the inner product.
        type: The type identifier for this inner product implementation.
    """

    type: str = "RKHSInnerProduct"

    def __init__(self, kernel: Optional[Callable] = None):
        """Initializes the RKHSInnerProduct with an optional kernel function.

        Args:
            kernel: A positive-definite kernel function. If not provided,
                must be set before use.
        """
        super().__init__()
        self.kernel = kernel

    def compute(
        self,
        a: Union[Vector, np.ndarray, Callable],
        b: Union[Vector, np.ndarray, Callable],
    ) -> float:
        """Computes the inner product using the kernel evaluation.

        The inner product is defined as ⟨a, b⟩_K = K(a, b), where K is the kernel.

        Args:
            a: The first element in the inner product operation. Can be a vector
               or a callable.
            b: The second element in the inner product operation. Can be a vector
               or a callable.

        Returns:
            float: The result of the inner product operation.

        Raises:
            ValueError: If the kernel is not set or if inputs are invalid
        """
        if self.kernel is None:
            raise ValueError("Kernel must be set before computing the inner product")

        # Convert callables to actual vectors
        a_val = a() if callable(a) else a
        b_val = b() if callable(b) else b

        # Apply the kernel to the values
        return self.kernel(a_val, b_val)

    def check_positive_definite(
        self, vector: Union[Vector, np.ndarray, Callable]
    ) -> None:
        """Checks if the kernel induces a positive-definite inner product.

        Args:
            vector: The vector or callable to test with.

        Raises:
            ValueError: If the kernel does not produce positive-definite results
        """
        value = self.compute(vector, vector)
        if value <= 0:
            raise ValueError(
                f"Kernel is not positive-definite. Computed value: {value}"
            )

    def set_kernel(self, kernel: Callable) -> None:
        """Sets the kernel function for the inner product.

        Args:
            kernel: A positive-definite kernel function.
        """
        self.kernel = kernel
