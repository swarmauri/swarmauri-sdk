import logging
from abc import abstractmethod
from typing import Callable, Literal, Optional, Union

import numpy as np
from pydantic import ConfigDict, Field
from swarmauri_core.inner_products.IInnerProduct import IInnerProduct
from swarmauri_standard.vectors.Vector import Vector

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes

logger = logging.getLogger(__name__)


@ComponentBase.register_model()
class InnerProductBase(IInnerProduct, ComponentBase):
    """
    Provides a base implementation for inner product operations. This class serves as
    a foundation for various inner product implementations and defines the common
    interface and functionality according to the IInnerProduct contract.

    This class should be subclassed by specific inner product implementations.
    """

    type: Literal["InnerProductBase"] = "InnerProductBase"
    resource: Optional[str] = Field(default=ResourceTypes.INNER_PRODUCT.value)

    @abstractmethod
    def compute(
        self,
        a: Union[Vector, np.ndarray, Callable],
        b: Union[Vector, np.ndarray, Callable],
    ) -> float:
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
            NotImplementedError: This method must be implemented by subclasses
            ValueError: If the input types are not supported or dimensions are incompatible
            ZeroDivisionError: If any operation leads to division by zero
        """
        logger.error("compute() method not implemented in subclass")
        raise NotImplementedError("Subclasses must implement the compute() method")

    def check_conjugate_symmetry(
        self,
        a: Union[Vector, np.ndarray, Callable],
        b: Union[Vector, np.ndarray, Callable],
    ) -> None:
        """
        Verifies the conjugate symmetry property of the inner product implementation.

        The inner product <a, b> should be equal to the conjugate of <b, a>.

        Args:
            a: The first element in the inner product operation
            b: The second element in the inner product operation

        Raises:
            ValueError: If the conjugate symmetry property is not satisfied
        """
        super().check_conjugate_symmetry(a, b)

    def check_linearity_first_argument(
        self,
        a: Union[Vector, np.ndarray, Callable],
        b: Union[Vector, np.ndarray, Callable],
        c: Union[Vector, np.ndarray, Callable],
    ) -> None:
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
        super().check_linearity_first_argument(a, b, c)

    def check_positivity(self, a: Union[Vector, np.ndarray, Callable]) -> None:
        """
        Verifies the positivity property of the inner product implementation.

        For any non-zero vector a:
        - <a, a> > 0

        Args:
            a: The vector to check for positivity

        Raises:
            ValueError: If the positivity property is not satisfied
        """
        super().check_positivity(a)
