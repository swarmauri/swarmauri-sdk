import logging
from abc import ABC
from typing import TypeVar, Union, Sequence, Literal, Optional, Type
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.seminorms.SeminormBase import SeminormBase
from swarmauri_core.seminorms.ISeminorm import IVector, IMatrix

logger = logging.getLogger(__name__)

T = TypeVar('T', IVector, IMatrix, Sequence)
S = TypeVar('S', bound='CoordinateProjectionSeminorm')

class CoordinateProjectionSeminorm(SeminormBase):
    """
    Implementation of a seminorm that projects onto a subset of coordinates.

    This seminorm implementation projects the input vector onto a specified subset
    of coordinates (indices) and computes the L2 norm of the projected components.
    The projection operation can lead to degeneracy if important components are ignored.

    Attributes:
        projection_indices: Sequence[int]
            The indices of the coordinates to project onto.
    """

    type: Literal["CoordinateProjectionSeminorm"] = "CoordinateProjectionSeminorm"
    """
    The type identifier for this seminorm implementation.
    """

    resource: str = ResourceTypes.SEMINORM.value
    """
    The resource type identifier for seminorm components.
    """

    def __init__(self, projection_indices: Sequence[int]) -> None:
        """
        Initializes the CoordinateProjectionSeminorm instance.

        Args:
            projection_indices: Sequence[int]
                The indices of the coordinates to project onto. Must be a sequence
                of non-negative integers that are valid indices for the input vectors.

        Raises:
            ValueError: If projection_indices contains negative integers or duplicates
        """
        super().__init__()
        
        # Validate projection indices
        if not isinstance(projection_indices, Sequence):
            raise TypeError("projection_indices must be a sequence")
            
        if not all(isinstance(idx, int) and idx >= 0 for idx in projection_indices):
            raise ValueError("All projection indices must be non-negative integers")
            
        if len(projection_indices) != len(set(projection_indices)):
            raise ValueError("Projection indices must be unique")
            
        self.projection_indices = tuple(projection_indices)
        """
        The indices of the coordinates to project onto.
        """

    def compute(self, input: T) -> float:
        """
        Computes the seminorm value by projecting the input onto the specified coordinates.

        Args:
            input: T
                The input to compute the seminorm for. Can be a vector, matrix,
                or sequence type.

        Returns:
            float: The computed seminorm value

        Raises:
            ValueError: If the input shape is incompatible with the projection indices
        """
        logger.debug(f"Computing seminorm for input of type {type(input).__name__}")
        
        # Get the components corresponding to the projection indices
        try:
            components = input[self.projection_indices]
        except IndexError:
            raise ValueError("Input does not have sufficient dimensions for the projection indices")
            
        # If input is a matrix, compute norm for each row and take the maximum
        if isinstance(input, IMatrix):
            # Assuming input is a matrix where each row is a vector
            norms = [self.compute(row) for row in input.rows()]
            return max(norms)
            
        # For vectors or sequences, compute the L2 norm of the projected components
        elif isinstance(input, (IVector, Sequence)):
            # Compute the L2 norm of the projected components
            return float(sum(x**2 for x in components) ** 0.5)
            
        else:
            raise ValueError(f"Unsupported input type: {type(input).__name__}")

    def check_triangle_inequality(self, a: T, b: T) -> bool:
        """
        Checks if the triangle inequality holds for this seminorm.

        The triangle inequality states that for any vectors a and b,
        ||a + b|| <= ||a|| + ||b||.

        Args:
            a: T
                The first vector
            b: T
                The second vector

        Returns:
            bool: True if the triangle inequality holds, False otherwise
        """
        logger.debug("Checking triangle inequality")
        
        norm_a = self.compute(a)
        norm_b = self.compute(b)
        norm_a_plus_b = self.compute(a + b)
        
        return norm_a_plus_b <= norm_a + norm_b

    def check_scalar_homogeneity(self, a: T, scalar: float) -> bool:
        """
        Checks if the scalar homogeneity property holds.

        For any vector a and scalar c, this checks that ||c * a|| = |c| * ||a||.

        Args:
            a: T
                The input vector
            scalar: float
                The scalar to test homogeneity with

        Returns:
            bool: True if scalar homogeneity holds, False otherwise
        """
        logger.debug(f"Checking scalar homogeneity with scalar {scalar}")
        
        norm_a = self.compute(a)
        scaled_a = a * scalar
        norm_scaled_a = self.compute(scaled_a)
        
        return norm_scaled_a == abs(scalar) * norm_a

__all__ = ["CoordinateProjectionSeminorm"]