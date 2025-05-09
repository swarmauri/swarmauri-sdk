from typing import Union, List, Optional
import logging
import numpy as np

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.seminorms.SeminormBase import SeminormBase

# Configure logging
logger = logging.getLogger(__name__)

@ComponentBase.register_type(SeminormBase, "CoordinateProjectionSeminorm")
class CoordinateProjectionSeminorm(SeminormBase):
    """
    A class providing a seminorm implementation that projects onto a subset of coordinates.

    This class implements the seminorm by projecting the input vector onto a specified
    set of coordinates and computing the L2 norm of the projected vector. The projection
    is defined by the indices provided during initialization. This implementation inherits
    from the base :class:`SeminormBase` class and implements the required methods.

    Attributes:
        projection_indices: List[int]
            A list of indices to project onto. These indices define the subset of
            coordinates that will be considered in the seminorm computation.
        resource: str
            The resource type identifier for this component.
    """

    def __init__(self, projection_indices: List[int]):
        """
        Initializes the CoordinateProjectionSeminorm instance.

        Args:
            projection_indices: List[int]
                A list of integer indices representing the coordinates to project onto.
                These indices must be valid for the input data structure.

        Raises:
            ValueError:
                If the projection_indices list is empty or contains invalid indices.
        """
        super().__init__()
        self.projection_indices = projection_indices
        self.resource = ResourceTypes.SEMINORM.value

        if not projection_indices:
            raise ValueError("Projection indices list cannot be empty")

    def compute(self, input: Union[np.ndarray, list, str, callable]) -> float:
        """
        Computes the seminorm of the input by projecting onto the specified coordinates.

        The input is projected onto the specified coordinates, and the L2 norm of the
        projected vector is computed. This provides a seminorm that ignores certain
        components of the vector, potentially leading to degeneracy.

        Args:
            input: Union[np.ndarray, list, str, callable]
                The input to compute the seminorm on. This can be a vector, matrix,
                string, or callable, but it must be convertible to a numpy array.

        Returns:
            float:
                The computed seminorm value.

        Raises:
            ValueError:
                If the input cannot be converted to a numpy array or if the
                projection indices are out of bounds.
        """
        try:
            # Convert input to numpy array if not already
            if not isinstance(input, np.ndarray):
                input = np.asarray(input)
            
            # Check if projection indices are valid
            if max(self.projection_indices) >= input.size:
                raise ValueError("Projection indices exceed input dimensions")

            # Project input onto specified coordinates
            projected_input = input[self.projection_indices]

            # Compute and return L2 norm of projected input
            return np.linalg.norm(projected_input)

        except Exception as e:
            logger.error(f"Error in compute method: {str(e)}")
            raise

    def check_triangle_inequality(self, a: Union[np.ndarray, list], b: Union[np.ndarray, list]) -> bool:
        """
        Checks if the triangle inequality holds for the projected seminorm.

        The triangle inequality states that for any vectors a and b:
        seminorm(a + b) <= seminorm(a) + seminorm(b)

        This method computes the seminorms of a, b, and a + b, and checks if the
        inequality holds.

        Args:
            a: Union[np.ndarray, list]
                The first vector.
            b: Union[np.ndarray, list]
                The second vector.

        Returns:
            bool:
                True if the triangle inequality holds, False otherwise.
        """
        try:
            a_np = np.asarray(a)
            b_np = np.asarray(b)
            
            seminorm_a = self.compute(a_np)
            seminorm_b = self.compute(b_np)
            seminorm_a_plus_b = self.compute(a_np + b_np)

            return seminorm_a_plus_b <= seminorm_a + seminorm_b

        except Exception as e:
            logger.error(f"Error in check_triangle_inequality: {str(e)}")
            raise

    def check_scalar_homogeneity(self, a: Union[np.ndarray, list], scalar: float) -> bool:
        """
        Checks if scalar homogeneity holds for the projected seminorm.

        Scalar homogeneity states that for any vector a and scalar c >= 0:
        seminorm(c * a) = c * seminorm(a)

        This method checks if this property holds for the given input and scalar.

        Args:
            a: Union[np.ndarray, list]
                The input vector.
            scalar: float
                The scalar to check against.

        Returns:
            bool:
                True if scalar homogeneity holds, False otherwise.
        """
        try:
            a_np = np.asarray(a)
            
            scaled_a = scalar * a_np
            seminorm_scaled = self.compute(scaled_a)
            scalar_times_seminorm = scalar * self.compute(a_np)

            return np.isclose(seminorm_scaled, scalar_times_seminorm)

        except Exception as e:
            logger.error(f"Error in check_scalar_homogeneity: {str(e)}")
            raise