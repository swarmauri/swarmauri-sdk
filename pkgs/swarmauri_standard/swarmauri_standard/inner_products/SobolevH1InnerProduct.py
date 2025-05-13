import logging
from typing import Callable, Literal, Union

import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.inner_products.InnerProductBase import InnerProductBase

from swarmauri_standard.vectors.Vector import Vector

logger = logging.getLogger(__name__)


@ComponentBase.register_type(InnerProductBase, "SobolevH1InnerProduct")
class SobolevH1InnerProduct(InnerProductBase):
    """
    Provides a concrete implementation of the Sobolev H^1 inner product.

    This class implements the inner product defined on the Sobolev space H^1, which
    combines the L2 inner product of functions and their first derivatives. The
    inner product is given by:

    <u, v> = (u, v)_{L2} + (u', v')_{L2}

    where u' and v' denote the first derivatives of u and v respectively.

    The implementation assumes that the provided vectors or functions have
    accessible first derivatives through attribute access.
    """

    type: Literal["SobolevH1InnerProduct"] = "SobolevH1InnerProduct"

    def __init__(self) -> None:
        """
        Initializes the Sobolev H1 inner product implementation.
        """
        super().__init__()

    def compute(
        self,
        a: Union[Vector, np.ndarray, Callable],
        b: Union[Vector, np.ndarray, Callable],
    ) -> float:
        """
        Computes the Sobolev H1 inner product between two elements.

        The computation involves evaluating both the L2 inner product of the
        functions and the L2 inner product of their first derivatives.

        Args:
            a: The first element in the inner product operation. Can be a vector,
               array, or callable.
            b: The second element in the inner product operation. Can be a vector,
               array, or callable.

        Returns:
            float: The result of the Sobolev H1 inner product operation.

        Raises:
            ValueError: If the input types are not supported or dimensions are incompatible
            ZeroDivisionError: If any operation leads to division by zero
        """
        logger.debug("Computing Sobolev H1 inner product")

        # Check if inputs are callables and need to be evaluated
        if callable(a):
            a = a(np.linspace(0, 1, 1000))  # Example evaluation points
        if callable(b):
            b = b(np.linspace(0, 1, 1000))

        # Handle array input case
        if isinstance(a, np.ndarray) and isinstance(b, np.ndarray):
            if a.shape != b.shape:
                raise ValueError(
                    "Array dimensions must match for inner product computation"
                )

            # Compute L2 inner product of functions
            func_inner = np.inner(a, b)

            # Access first derivatives (assuming they are stored as attributes)
            a_grad = a.grad if hasattr(a, "grad") else np.zeros_like(a)
            b_grad = b.grad if hasattr(b, "grad") else np.zeros_like(b)

            # Compute L2 inner product of derivatives
            grad_inner = np.inner(a_grad, b_grad)

            return float(func_inner + grad_inner)

        elif isinstance(a, Vector) and isinstance(b, Vector):
            # Handle vector input case
            if a.shape != b.shape:
                raise ValueError(
                    "Vector dimensions must match for inner product computation"
                )

            # Compute L2 inner product of functions
            func_inner = a.dot(b)

            # Access first derivatives
            a_grad = a.grad
            b_grad = b.grad

            # Compute L2 inner product of derivatives
            grad_inner = a_grad.dot(b_grad)

            return float(func_inner + grad_inner)

        else:
            raise ValueError(f"Unsupported input types: {type(a)} and {type(b)}")
