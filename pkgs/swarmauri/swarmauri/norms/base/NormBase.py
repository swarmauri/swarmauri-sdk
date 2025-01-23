from math import isclose
from typing import Literal
from pydantic import ConfigDict, Field

from swarmauri_core.norms.INorm import INorm
from swarmauri.vectors.IVector import IVector
from swarmauri_core.typing import SubclassUnion
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes


class NormBase(INorm, ComponentBase):
    """
    Default implementation of a norm.

    This class provides default implementation logic for the checks of a norm. It includes methods to verify 
    non-negativity, definiteness, absolute scalability, and the triangle inequality for a given norm.

    Subclasses should implement the `compute` method to define how the norm of a vector is calculated.
    """

    resource: ResourceTypes = Field(default=ResourceTypes.NORM.value)
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    type: Literal['NormBase'] = 'NormBase'

    def compute(self, x: IVector) -> float:
        """
        Compute the norm of a vector x.

        This method must be implemented by subclasses to define how the norm is calculated for a specific vector space.

        Args:
            x: A vector (IVector) whose norm is to be computed.

        Returns:
            A float representing the norm of the vector.

        Raises:
            NotImplementedError: If this method is not implemented by the subclass.
        """
        raise NotImplementedError("compute must be implemented by norm subclasses")

    def verify_non_negativity(self, x: IVector) -> bool:
        """
        Verify the non-negativity axiom: ∥x∥ ≥ 0.

        This method checks if the computed norm of the vector is non-negative.

        Args:
            x: The vector (IVector) to verify.

        Returns:
            bool: Returns `True` if the axiom is satisfied, otherwise `False`.
        """
        norm_value = self.compute(x)
        return norm_value >= 0

    def verify_definiteness(self, x: IVector) -> bool:
        """
        Verify the definiteness axiom: ∥x∥ = 0 ⟺ x = 0.

        This method checks if the norm of a vector is zero if and only if the vector is the zero vector.

        Args:
            x: The vector (IVector) to verify.

        Returns:
            bool: Returns `True` if the axiom is satisfied, otherwise `False`.
        """
        norm_value = self.compute(x)
        # Check if the norm is zero and the vector is the zero vector
        if norm_value == 0 and x != 0:
            return False
        # Alternatively, ensure if the vector is zero, the norm is zero
        if x == 0 and not isclose(norm_value, 0):
            return False
        return True

    def verify_absolute_scalability(self, alpha: float, x: IVector) -> bool:
        """
        Verify the absolute scalability axiom: ∥αx∥ = |α| ⋅ ∥x∥.

        This method checks if the norm of the scaled vector is equal to the absolute value of the scalar 
        times the norm of the original vector.

        Args:
            alpha: The scalar multiplier.
            x: The vector (IVector) to verify.

        Returns:
            bool: Returns `True` if the axiom is satisfied, otherwise `False`.
        """
        norm_alpha_x = self.compute(alpha * x)
        norm_x = self.compute(x)
        return isclose(norm_alpha_x, abs(alpha) * norm_x)

    def verify_triangle_inequality(self, x: IVector, y: IVector) -> bool:
        """
        Verify the triangle inequality axiom: ∥x + y∥ ≤ ∥x∥ + ∥y∥.

        This method checks if the norm of the sum of two vectors is less than or equal to the sum of 
        the norms of the individual vectors.

        Args:
            x: The first vector (IVector).
            y: The second vector (IVector).

        Returns:
            bool: Returns `True` if the axiom is satisfied, otherwise `False`.
        """
        norm_x_y = self.compute(x + y)
        norm_x = self.compute(x)
        norm_y = self.compute(y)
        return norm_x_y <= norm_x + norm_y

    def check_all_norm_axioms(self, alpha: float, x: IVector, y: IVector) -> bool:
        """
        Check all the norm axioms: non-negativity, definiteness, absolute scalability, and triangle inequality.

        This method runs all individual checks for the properties of a norm. If any axiom is violated, it returns `False`.

        Args:
            alpha: A scalar for testing absolute scalability.
            x: The first vector (for all tests).
            y: The second vector (for triangle inequality).

        Returns:
            bool: Returns `True` if all axioms are satisfied, otherwise `False`.
        """
        # Non-negativity
        if not self.verify_non_negativity(x):
            return False

        # Definiteness
        if not self.verify_definiteness(x):
            return False

        # Absolute scalability
        if not self.verify_absolute_scalability(alpha, x):
            return False

        # Triangle inequality
        if not self.verify_triangle_inequality(x, y):
            return False

        return True
