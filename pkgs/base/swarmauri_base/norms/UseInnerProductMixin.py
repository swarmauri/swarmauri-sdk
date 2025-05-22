from typing import Literal, TypeVar, Any
import logging

from swarmauri_core.norms.IUseInnerProduct import IUseInnerProduct
from swarmauri_core.inner_products.IInnerProduct import IInnerProduct

# Configure logging
logger = logging.getLogger(__name__)

Vector = TypeVar("Vector")


class UseInnerProductMixin(IUseInnerProduct):
    """
    Base mixin class for structures dependent on inner products.

    This mixin provides functionality for components that require an inner product
    structure for their operations. It maintains a reference to an inner product
    object and implements the IUseInnerProduct interface.

    Attributes
    ----------
    _inner_product : IInnerProduct
        Reference to the inner product implementation used by this component
    """

    def __init__(self, inner_product: IInnerProduct, *args: Any, **kwargs: Any):
        """
        Initialize the mixin with an inner product.

        Parameters
        ----------
        inner_product : IInnerProduct
            The inner product implementation to use
        *args : Any
            Additional positional arguments for parent classes
        **kwargs : Any
            Additional keyword arguments for parent classes
        """
        self._inner_product = inner_product
        super().__init__(*args, **kwargs)
        logger.debug(
            f"Initialized {self.__class__.__name__} with inner product {inner_product}"
        )

    def get_inner_product(self) -> Literal[IInnerProduct]:
        """
        Get the inner product implementation used by this component.

        Returns
        -------
        IInnerProduct
            The inner product implementation
        """
        return self._inner_product

    def check_angle_between_vectors(self, v1: Vector, v2: Vector) -> float:
        """
        Calculate the angle between two vectors using the inner product.

        Parameters
        ----------
        v1 : Vector
            First vector
        v2 : Vector
            Second vector

        Returns
        -------
        float
            Angle between vectors in radians

        Raises
        ------
        NotImplementedError
            This is a base implementation that needs to be overridden
        """
        raise NotImplementedError(
            "check_angle_between_vectors must be implemented by subclasses"
        )

    def check_orthogonality(
        self, v1: Vector, v2: Vector, tolerance: float = 1e-10
    ) -> bool:
        """
        Verify if two vectors are orthogonal to each other.

        Parameters
        ----------
        v1 : Vector
            First vector
        v2 : Vector
            Second vector
        tolerance : float, optional
            Numerical tolerance for zero comparison, by default 1e-10

        Returns
        -------
        bool
            True if vectors are orthogonal, False otherwise

        Raises
        ------
        NotImplementedError
            This is a base implementation that needs to be overridden
        """
        raise NotImplementedError(
            "check_orthogonality must be implemented by subclasses"
        )

    def check_xy_projection(
        self, v: Vector, basis_x: Vector, basis_y: Vector
    ) -> tuple[float, float]:
        """
        Project a vector onto the plane defined by two basis vectors.

        Parameters
        ----------
        v : Vector
            Vector to project
        basis_x : Vector
            First basis vector (x-axis)
        basis_y : Vector
            Second basis vector (y-axis)

        Returns
        -------
        tuple[float, float]
            The (x, y) coordinates of the projection

        Raises
        ------
        NotImplementedError
            This is a base implementation that needs to be overridden
        """
        raise NotImplementedError(
            "check_xy_projection must be implemented by subclasses"
        )

    def check_parallelogram_law(
        self, v1: Vector, v2: Vector, tolerance: float = 1e-10
    ) -> bool:
        """
        Verify if the parallelogram law holds for two vectors:
        ||v1 + v2||² + ||v1 - v2||² = 2(||v1||² + ||v2||²)

        Parameters
        ----------
        v1 : Vector
            First vector
        v2 : Vector
            Second vector
        tolerance : float, optional
            Numerical tolerance for comparison, by default 1e-10

        Returns
        -------
        bool
            True if the parallelogram law holds, False otherwise

        Raises
        ------
        NotImplementedError
            This is a base implementation that needs to be overridden
        """
        raise NotImplementedError(
            "check_parallelogram_law must be implemented by subclasses"
        )
