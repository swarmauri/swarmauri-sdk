from typing import Callable, List, Literal, Sequence, TypeVar, Union
import logging
from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.pseudometrics.IPseudometric import IPseudometric
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix

# Set up logging
logger = logging.getLogger(__name__)

# Type variables
T = TypeVar("T")

# Type literals for IVector and IMatrix
VectorType = Literal[IVector]
MatrixType = Literal[IMatrix]


@ComponentBase.register_model()
class PseudometricBase(IPseudometric, ComponentBase):
    """
    Abstract base class implementing pseudometric behavior.

    A pseudometric satisfies:
    1. Non-negativity: d(x,y) ≥ 0
    2. Symmetry: d(x,y) = d(y,x)
    3. Triangle inequality: d(x,z) ≤ d(x,y) + d(y,z)

    Unlike a metric, a pseudometric allows d(x,y) = 0 for x ≠ y, meaning it may not
    distinguish between distinct points.

    This base class provides skeleton implementations for all required methods
    of the IPseudometric interface. Derived classes should override these methods
    with actual implementations.
    """

    resource: str = Field(default=ResourceTypes.PSEUDOMETRIC.value)

    def distance(
        self,
        x: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        y: Union[VectorType, MatrixType, Sequence[T], str, Callable],
    ) -> float:
        """
        Calculate the pseudometric distance between two objects.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The first object
        y : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The second object

        Returns
        -------
        float
            The distance between x and y

        Raises
        ------
        TypeError
            If inputs are of incompatible types
        ValueError
            If inputs have incompatible dimensions
        NotImplementedError
            If the method is not implemented by a derived class
        """
        logger.error("distance method not implemented")
        raise NotImplementedError(
            "The distance method must be implemented by derived classes"
        )

    def distances(
        self,
        xs: Sequence[Union[VectorType, MatrixType, Sequence[T], str, Callable]],
        ys: Sequence[Union[VectorType, MatrixType, Sequence[T], str, Callable]],
    ) -> List[List[float]]:
        """
        Calculate the pairwise distances between two collections of objects.

        Parameters
        ----------
        xs : Sequence[Union[VectorType, MatrixType, Sequence[T], str, Callable]]
            The first collection of objects
        ys : Sequence[Union[VectorType, MatrixType, Sequence[T], str, Callable]]
            The second collection of objects

        Returns
        -------
        List[List[float]]
            A matrix of distances where distances[i][j] is the distance between xs[i] and ys[j]

        Raises
        ------
        TypeError
            If inputs contain incompatible types
        ValueError
            If inputs have incompatible dimensions
        NotImplementedError
            If the method is not implemented by a derived class
        """
        logger.error("distances method not implemented")
        raise NotImplementedError(
            "The distances method must be implemented by derived classes"
        )

    def check_non_negativity(
        self,
        x: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        y: Union[VectorType, MatrixType, Sequence[T], str, Callable],
    ) -> bool:
        """
        Check if the distance function satisfies the non-negativity property.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The first object
        y : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The second object

        Returns
        -------
        bool
            True if d(x,y) ≥ 0, False otherwise

        Raises
        ------
        NotImplementedError
            If the method is not implemented by a derived class
        """
        logger.error("check_non_negativity method not implemented")
        raise NotImplementedError(
            "The check_non_negativity method must be implemented by derived classes"
        )

    def check_symmetry(
        self,
        x: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        y: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        tolerance: float = 1e-10,
    ) -> bool:
        """
        Check if the distance function satisfies the symmetry property.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The first object
        y : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The second object
        tolerance : float, optional
            The tolerance for floating-point comparisons, by default 1e-10

        Returns
        -------
        bool
            True if d(x,y) = d(y,x) within tolerance, False otherwise

        Raises
        ------
        NotImplementedError
            If the method is not implemented by a derived class
        """
        logger.error("check_symmetry method not implemented")
        raise NotImplementedError(
            "The check_symmetry method must be implemented by derived classes"
        )

    def check_triangle_inequality(
        self,
        x: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        y: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        z: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        tolerance: float = 1e-10,
    ) -> bool:
        """
        Check if the distance function satisfies the triangle inequality.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The first object
        y : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The second object
        z : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The third object
        tolerance : float, optional
            The tolerance for floating-point comparisons, by default 1e-10

        Returns
        -------
        bool
            True if d(x,z) ≤ d(x,y) + d(y,z) within tolerance, False otherwise

        Raises
        ------
        NotImplementedError
            If the method is not implemented by a derived class
        """
        logger.error("check_triangle_inequality method not implemented")
        raise NotImplementedError(
            "The check_triangle_inequality method must be implemented by derived classes"
        )

    def check_weak_identity(
        self,
        x: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        y: Union[VectorType, MatrixType, Sequence[T], str, Callable],
    ) -> bool:
        """
        Check if the distance function satisfies the weak identity property.

        In a pseudometric, d(x,y) = 0 is allowed even when x ≠ y.
        This method verifies that this property is properly handled.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The first object
        y : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The second object

        Returns
        -------
        bool
            True if the pseudometric properly handles the weak identity property

        Raises
        ------
        NotImplementedError
            If the method is not implemented by a derived class
        """
        logger.error("check_weak_identity method not implemented")
        raise NotImplementedError(
            "The check_weak_identity method must be implemented by derived classes"
        )
