import logging
from typing import Callable, List, Literal, Sequence, TypeVar, Union

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.pseudometrics.PseudometricBase import PseudometricBase
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.vectors.IVector import IVector

# Set up logging
logger = logging.getLogger(__name__)

# Type variables
T = TypeVar("T")

# Type literals for IVector and IMatrix
VectorType = Literal[IVector]
MatrixType = Literal[IMatrix]


@ComponentBase.register_type(PseudometricBase, "ZeroPseudometric")
class ZeroPseudometric(PseudometricBase):
    """
    Trivial pseudometric that always returns 0 regardless of input.

    This pseudometric assigns zero distance between all points, making it
    a valid mathematical structure that satisfies all pseudometric axioms:
    1. Non-negativity: d(x,y) = 0 ≥ 0
    2. Symmetry: d(x,y) = 0 = d(y,x)
    3. Triangle inequality: d(x,z) = 0 ≤ d(x,y) + d(y,z) = 0 + 0 = 0

    While mathematically valid, this pseudometric doesn't provide any
    meaningful discrimination between different inputs.

    Attributes
    ----------
    type : Literal["ZeroPseudometric"]
        The type identifier for this class
    """

    type: Literal["ZeroPseudometric"] = "ZeroPseudometric"

    def distance(
        self,
        x: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        y: Union[VectorType, MatrixType, Sequence[T], str, Callable],
    ) -> float:
        """
        Calculate the pseudometric distance between two objects, always returning 0.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The first object (not used in calculation)
        y : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The second object (not used in calculation)

        Returns
        -------
        float
            Always returns 0.0
        """
        logger.debug(
            f"Computing ZeroPseudometric distance between objects of types {type(x)} and {type(y)}"
        )
        return 0.0

    def distances(
        self,
        xs: Sequence[Union[VectorType, MatrixType, Sequence[T], str, Callable]],
        ys: Sequence[Union[VectorType, MatrixType, Sequence[T], str, Callable]],
    ) -> List[List[float]]:
        """
        Calculate the pairwise distances between two collections of objects.

        For ZeroPseudometric, this creates a matrix of zeros with dimensions
        len(xs) × len(ys).

        Parameters
        ----------
        xs : Sequence[Union[VectorType, MatrixType, Sequence[T], str, Callable]]
            The first collection of objects
        ys : Sequence[Union[VectorType, MatrixType, Sequence[T], str, Callable]]
            The second collection of objects

        Returns
        -------
        List[List[float]]
            A matrix of zeros with dimensions len(xs) × len(ys)
        """
        logger.debug(
            f"Computing pairwise ZeroPseudometric distances between {len(xs)} and {len(ys)} objects"
        )
        # Create a matrix of zeros with dimensions len(xs) × len(ys)
        return [[0.0 for _ in range(len(ys))] for _ in range(len(xs))]

    def check_non_negativity(
        self,
        x: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        y: Union[VectorType, MatrixType, Sequence[T], str, Callable],
    ) -> bool:
        """
        Check if the distance function satisfies the non-negativity property.

        For ZeroPseudometric, this is always true since 0 ≥ 0.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The first object (not used in calculation)
        y : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The second object (not used in calculation)

        Returns
        -------
        bool
            Always returns True
        """
        logger.debug(
            f"Checking non-negativity for ZeroPseudometric with objects of types {type(x)} and {type(y)}"
        )
        # Non-negativity is always satisfied since 0 ≥ 0
        return True

    def check_symmetry(
        self,
        x: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        y: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        tolerance: float = 1e-10,
    ) -> bool:
        """
        Check if the distance function satisfies the symmetry property.

        For ZeroPseudometric, this is always true since d(x,y) = 0 = d(y,x).

        Parameters
        ----------
        x : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The first object (not used in calculation)
        y : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The second object (not used in calculation)
        tolerance : float, optional
            The tolerance for floating-point comparisons, by default 1e-10 (not used)

        Returns
        -------
        bool
            Always returns True
        """
        logger.debug(
            f"Checking symmetry for ZeroPseudometric with objects of types {type(x)} and {type(y)}"
        )
        # Symmetry is always satisfied since d(x,y) = 0 = d(y,x)
        return True

    def check_triangle_inequality(
        self,
        x: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        y: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        z: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        tolerance: float = 1e-10,
    ) -> bool:
        """
        Check if the distance function satisfies the triangle inequality.

        For ZeroPseudometric, this is always true since:
        d(x,z) = 0 ≤ d(x,y) + d(y,z) = 0 + 0 = 0

        Parameters
        ----------
        x : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The first object (not used in calculation)
        y : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The second object (not used in calculation)
        z : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The third object (not used in calculation)
        tolerance : float, optional
            The tolerance for floating-point comparisons, by default 1e-10 (not used)

        Returns
        -------
        bool
            Always returns True
        """
        logger.debug(
            f"Checking triangle inequality for ZeroPseudometric with objects of types {type(x)}, {type(y)}, and {type(z)}"
        )
        # Triangle inequality is always satisfied since d(x,z) = 0 ≤ d(x,y) + d(y,z) = 0 + 0 = 0
        return True

    def check_weak_identity(
        self,
        x: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        y: Union[VectorType, MatrixType, Sequence[T], str, Callable],
    ) -> bool:
        """
        Check if the distance function satisfies the weak identity property.

        For ZeroPseudometric, this is always true since d(x,y) = 0 for all x and y,
        which is consistent with the definition of a pseudometric (allowing d(x,y) = 0 when x ≠ y).

        Parameters
        ----------
        x : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The first object (not used in calculation)
        y : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The second object (not used in calculation)

        Returns
        -------
        bool
            Always returns True
        """
        logger.debug(
            f"Checking weak identity for ZeroPseudometric with objects of types {type(x)} and {type(y)}"
        )
        # Weak identity is always satisfied since d(x,y) = 0 for all x and y
        return True

    def __str__(self) -> str:
        """
        Return a string representation of the ZeroPseudometric.

        Returns
        -------
        str
            A string describing this pseudometric
        """
        return "ZeroPseudometric (trivial pseudometric that returns 0 for all inputs)"

    def __repr__(self) -> str:
        """
        Return a developer string representation of the ZeroPseudometric.

        Returns
        -------
        str
            A string representation suitable for debugging
        """
        return "ZeroPseudometric()"
