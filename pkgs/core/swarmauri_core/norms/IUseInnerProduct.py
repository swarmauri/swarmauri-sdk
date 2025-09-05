import logging
from abc import ABC, abstractmethod
from typing import Literal, TypeVar

from swarmauri_core.inner_products.IInnerProduct import IInnerProduct

# Configure logging
logger = logging.getLogger(__name__)

Vector = TypeVar("Vector")


class IUseInnerProduct(ABC):
    """
    Abstract interface marking components using inner product geometry.

    This interface indicates dependency on inner product structure and defines
    methods for operations that rely on inner product geometry, such as computing
    angles between vectors, verifying orthogonality, projection, and validating
    the parallelogram law.
    """

    @abstractmethod
    def get_inner_product(self) -> Literal[IInnerProduct]:
        """
        Get the inner product implementation used by this component.

        Returns
        -------
        IInnerProduct
            The inner product implementation
        """
        pass

    @abstractmethod
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
        """
        pass

    @abstractmethod
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
        """
        pass

    @abstractmethod
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
        """
        pass

    @abstractmethod
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
        """
        pass
