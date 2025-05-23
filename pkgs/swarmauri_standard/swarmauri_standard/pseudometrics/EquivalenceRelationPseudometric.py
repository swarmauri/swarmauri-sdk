import logging
from typing import Any, Callable, List, Literal, Sequence, TypeVar, Union

from pydantic import Field
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


@ComponentBase.register_type(PseudometricBase, "EquivalenceRelationPseudometric")
class EquivalenceRelationPseudometric(PseudometricBase):
    """
    Implements a pseudometric based on equivalence relations.

    This pseudometric assigns distance 0 to points that are equivalent
    under a given equivalence relation, and distance 1 to points that are not.
    This effectively creates a quotient space where points in the same
    equivalence class are treated as identical.

    The equivalence relation must satisfy:
    1. Reflexivity: x ~ x for all x
    2. Symmetry: if x ~ y, then y ~ x
    3. Transitivity: if x ~ y and y ~ z, then x ~ z
    """

    type: Literal["EquivalenceRelationPseudometric"] = "EquivalenceRelationPseudometric"
    equivalence_relation: Callable[[Any, Any], bool] = Field(
        ..., description="Equivalence relation function"
    )

    def __init__(self, equivalence_relation: Callable[[Any, Any], bool], **kwargs):
        """
        Initialize the EquivalenceRelationPseudometric with an equivalence relation.

        Parameters
        ----------
        equivalence_relation : Callable[[Any, Any], bool]
            A function that takes two arguments and returns True if they are equivalent,
            False otherwise.
        kwargs : Any
            Additional keyword arguments for the base class.
        """
        super().__init__(**kwargs, equivalence_relation=equivalence_relation)

    def distance(
        self,
        x: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        y: Union[VectorType, MatrixType, Sequence[T], str, Callable],
    ) -> float:
        """
        Calculate the pseudometric distance based on equivalence relation.

        Returns 0 if x is equivalent to y, 1 otherwise.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The first object
        y : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The second object

        Returns
        -------
        float
            0.0 if x and y are equivalent, 1.0 otherwise
        """
        try:
            # Apply the equivalence relation to determine if x and y are equivalent
            if self.equivalence_relation(x, y):
                return 0.0
            else:
                return 1.0
        except Exception as e:
            logger.error(f"Error calculating distance: {str(e)}")
            raise ValueError(f"Failed to calculate distance: {str(e)}")

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
        """
        try:
            result = []
            for x in xs:
                row = []
                for y in ys:
                    row.append(self.distance(x, y))
                result.append(row)
            return result
        except Exception as e:
            logger.error(f"Error calculating distances matrix: {str(e)}")
            raise ValueError(f"Failed to calculate distances matrix: {str(e)}")

    def check_non_negativity(
        self,
        x: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        y: Union[VectorType, MatrixType, Sequence[T], str, Callable],
    ) -> bool:
        """
        Check if the distance function satisfies the non-negativity property.

        For an equivalence relation pseudometric, this is always true as the distance
        is either 0 or 1, both of which are non-negative.

        Parameters
        ----------
        x : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The first object
        y : Union[VectorType, MatrixType, Sequence[T], str, Callable]
            The second object

        Returns
        -------
        bool
            Always True for this pseudometric
        """
        # Distance is always either 0 or 1, so it's always non-negative
        return True

    def check_symmetry(
        self,
        x: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        y: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        tolerance: float = 1e-10,
    ) -> bool:
        """
        Check if the distance function satisfies the symmetry property.

        This checks if the equivalence relation is symmetric, i.e., if x ~ y then y ~ x.

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
        """
        try:
            # Check if the distance from x to y equals the distance from y to x
            d_xy = self.distance(x, y)
            d_yx = self.distance(y, x)
            return abs(d_xy - d_yx) <= tolerance
        except Exception as e:
            logger.error(f"Error checking symmetry: {str(e)}")
            raise ValueError(f"Failed to check symmetry: {str(e)}")

    def check_triangle_inequality(
        self,
        x: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        y: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        z: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        tolerance: float = 1e-10,
    ) -> bool:
        """
        Check if the distance function satisfies the triangle inequality.

        For an equivalence relation pseudometric, this is always true:
        - If x ~ z, then d(x,z) = 0 ≤ d(x,y) + d(y,z) for any y
        - If x !~ z, then d(x,z) = 1, and there are two cases:
          * If x ~ y and y ~ z, transitivity of the equivalence relation would imply x ~ z,
            contradicting our assumption. So this case is impossible.
          * If x !~ y or y !~ z, then d(x,y) + d(y,z) ≥ 1 = d(x,z)

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
        """
        try:
            d_xz = self.distance(x, z)
            d_xy = self.distance(x, y)
            d_yz = self.distance(y, z)

            # Check triangle inequality: d(x,z) ≤ d(x,y) + d(y,z)
            return d_xz <= d_xy + d_yz + tolerance
        except Exception as e:
            logger.error(f"Error checking triangle inequality: {str(e)}")
            raise ValueError(f"Failed to check triangle inequality: {str(e)}")

    def check_weak_identity(
        self,
        x: Union[VectorType, MatrixType, Sequence[T], str, Callable],
        y: Union[VectorType, MatrixType, Sequence[T], str, Callable],
    ) -> bool:
        """
        Check if the distance function satisfies the weak identity property.

        In a pseudometric, d(x,y) = 0 is allowed even when x ≠ y.
        For an equivalence relation pseudometric, d(x,y) = 0 exactly when x ~ y.

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
        """
        try:
            # For this pseudometric, d(x,y) = 0 if and only if x ~ y
            # So we check if the equivalence relation and distance are consistent
            are_equivalent = self.equivalence_relation(x, y)
            d_xy = self.distance(x, y)

            # If they're equivalent, distance should be 0; if not, distance should be 1
            return (are_equivalent and d_xy == 0.0) or (
                not are_equivalent and d_xy == 1.0
            )
        except Exception as e:
            logger.error(f"Error checking weak identity: {str(e)}")
            raise ValueError(f"Failed to check weak identity: {str(e)}")
