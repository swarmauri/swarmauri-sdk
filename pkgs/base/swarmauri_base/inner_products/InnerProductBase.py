import logging
from typing import Callable, Literal, TypeVar, Union

import numpy as np
from swarmauri_core.inner_products.IInnerProduct import IInnerProduct
from swarmauri_core.vectors.IVector import IVector

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar("T")
Vector = TypeVar("Vector", bound="IVector")
Matrix = TypeVar("Matrix", bound=np.ndarray)


@ComponentBase.register_model()
class InnerProductBase(IInnerProduct, ComponentBase):
    """
    Abstract base class implementing partial methods for inner product calculations.

    This class provides a base implementation of all abstract methods defined in
    the IInnerProduct interface. It serves as a foundation for specific inner
    product implementations, offering common functionality and ensuring
    adherence to the interface contract.

    Attributes
    ----------
    resource : str
        The resource type identifier, defaulting to INNER_PRODUCT
    """

    resource: str = ResourceTypes.INNER_PRODUCT.value
    type: Literal["InnerProductBase"] = "InnerProductBase"

    def compute(
        self, a: Union[Vector, Matrix, Callable], b: Union[Vector, Matrix, Callable]
    ) -> float:
        """
        Compute the inner product between two objects.

        Parameters
        ----------
        a : Union[Vector, Matrix, Callable]
            The first object for inner product calculation
        b : Union[Vector, Matrix, Callable]
            The second object for inner product calculation

        Returns
        -------
        float
            The inner product value

        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses
        """
        logger.debug(
            f"Attempting to compute inner product between {type(a)} and {type(b)}"
        )
        raise NotImplementedError("Method 'compute' must be implemented by subclasses")

    def check_conjugate_symmetry(
        self, a: Union[Vector, Matrix, Callable], b: Union[Vector, Matrix, Callable]
    ) -> bool:
        """
        Check if the inner product satisfies the conjugate symmetry property:
        <a, b> = <b, a>* (complex conjugate).

        Parameters
        ----------
        a : Union[Vector, Matrix, Callable]
            The first object
        b : Union[Vector, Matrix, Callable]
            The second object

        Returns
        -------
        bool
            True if conjugate symmetry holds, False otherwise

        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses
        """
        logger.debug(
            f"Attempting to check conjugate symmetry for {type(a)} and {type(b)}"
        )
        raise NotImplementedError(
            "Method 'check_conjugate_symmetry' must be implemented by subclasses"
        )

    def check_linearity_first_argument(
        self,
        a1: Union[Vector, Matrix, Callable],
        a2: Union[Vector, Matrix, Callable],
        b: Union[Vector, Matrix, Callable],
        alpha: float,
        beta: float,
    ) -> bool:
        """
        Check if the inner product satisfies linearity in the first argument:
        <alpha*a1 + beta*a2, b> = alpha*<a1, b> + beta*<a2, b>.

        Parameters
        ----------
        a1 : Union[Vector, Matrix, Callable]
            First component of the first argument
        a2 : Union[Vector, Matrix, Callable]
            Second component of the first argument
        b : Union[Vector, Matrix, Callable]
            The second object
        alpha : float
            Scalar multiplier for a1
        beta : float
            Scalar multiplier for a2

        Returns
        -------
        bool
            True if linearity in the first argument holds, False otherwise

        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses
        """
        logger.debug(
            f"Attempting to check linearity in first argument with alpha={alpha}, beta={beta}"
        )
        raise NotImplementedError(
            "Method 'check_linearity_first_argument' must be implemented by subclasses"
        )

    def check_positivity(self, a: Union[Vector, Matrix, Callable]) -> bool:
        """
        Check if the inner product satisfies the positivity property:
        <a, a> >= 0 and <a, a> = 0 iff a = 0.

        Parameters
        ----------
        a : Union[Vector, Matrix, Callable]
            The object to check positivity for

        Returns
        -------
        bool
            True if positivity holds, False otherwise

        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses
        """
        logger.debug(f"Attempting to check positivity for {type(a)}")
        raise NotImplementedError(
            "Method 'check_positivity' must be implemented by subclasses"
        )
