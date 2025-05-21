import logging
from typing import Literal, Sequence, Set

import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.seminorms.SeminormBase import SeminormBase
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.seminorms.ISeminorm import InputType, T
from swarmauri_core.vectors.IVector import IVector

# Configure logging
logger = logging.getLogger(__name__)


@ComponentBase.register_type(SeminormBase, "CoordinateProjectionSeminorm")
class CoordinateProjectionSeminorm(SeminormBase):
    """
    Seminorm via projection onto a subset of coordinates.

    This seminorm ignores certain components of the vector, resulting in possible degeneracy.
    It projects the input onto a specified subset of coordinates and computes the norm
    only on those coordinates.

    Attributes
    ----------
    type : Literal["CoordinateProjectionSeminorm"]
        The type identifier for this seminorm
    projection_indices : Set[int]
        The set of indices to project onto
    """

    type: Literal["CoordinateProjectionSeminorm"] = "CoordinateProjectionSeminorm"

    def __init__(self, projection_indices: Set[int]):
        """
        Initialize the coordinate projection seminorm.

        Parameters
        ----------
        projection_indices : Set[int]
            The set of indices to project onto. These are the components that will
            be considered when computing the seminorm, all other components will be ignored.

        Raises
        ------
        ValueError
            If projection_indices is empty
        """
        super().__init__()
        if not projection_indices:
            raise ValueError("Projection indices set cannot be empty")

        self.projection_indices = projection_indices
        logger.info(
            f"Initialized CoordinateProjectionSeminorm with projection indices: {projection_indices}"
        )

    def compute(self, x: InputType) -> float:
        """
        Compute the seminorm of the input by projecting onto specified coordinates.

        Parameters
        ----------
        x : InputType
            The input to compute the seminorm for. Can be a vector, matrix,
            sequence, or numpy array.

        Returns
        -------
        float
            The seminorm value (non-negative real number)

        Raises
        ------
        TypeError
            If the input type is not supported
        ValueError
            If the computation cannot be performed on the given input
        """
        logger.debug(f"Computing projection seminorm for input of type {type(x)}")

        # Handle different input types
        if isinstance(x, IVector):
            return self._compute_vector(x)
        elif isinstance(x, IMatrix):
            return self._compute_matrix(x)
        elif isinstance(x, (list, tuple, np.ndarray)):
            return self._compute_sequence(x)
        else:
            raise TypeError(f"Unsupported input type: {type(x)}")

    def _compute_vector(self, x: IVector) -> float:
        """
        Compute the seminorm for a vector by projecting onto specified coordinates.

        Parameters
        ----------
        x : IVector
            The vector to compute the seminorm for

        Returns
        -------
        float
            The seminorm value
        """
        # Extract the components corresponding to the projection indices
        components = x.components

        # Check if indices are valid for this vector
        max_index = max(self.projection_indices) if self.projection_indices else -1
        if max_index >= len(components):
            raise ValueError(
                f"Projection index {max_index} out of bounds for vector of length {len(components)}"
            )

        # Project onto the selected coordinates
        projected_components = [
            components[i] for i in self.projection_indices if i < len(components)
        ]

        # Compute the Euclidean norm of the projected components
        return np.sqrt(sum(abs(c) ** 2 for c in projected_components))

    def _compute_matrix(self, x: IMatrix) -> float:
        """
        Compute the seminorm for a matrix by projecting onto specified coordinates.

        For matrices, we flatten the matrix to a vector and then apply the projection.

        Parameters
        ----------
        x : IMatrix
            The matrix to compute the seminorm for

        Returns
        -------
        float
            The seminorm value
        """
        # Flatten the matrix into a 1D array
        flattened = []
        for row in x.rows:
            flattened.extend(row)

        # Check if indices are valid for this flattened matrix
        max_index = max(self.projection_indices) if self.projection_indices else -1
        if max_index >= len(flattened):
            raise ValueError(
                f"Projection index {max_index} out of bounds for flattened matrix of length {len(flattened)}"
            )

        # Project onto the selected coordinates
        projected_components = [
            flattened[i] for i in self.projection_indices if i < len(flattened)
        ]

        # Compute the Euclidean norm of the projected components
        return np.sqrt(sum(abs(c) ** 2 for c in projected_components))

    def _compute_sequence(self, x: Sequence) -> float:
        """
        Compute the seminorm for a sequence by projecting onto specified coordinates.

        Parameters
        ----------
        x : Sequence
            The sequence to compute the seminorm for

        Returns
        -------
        float
            The seminorm value
        """
        # Convert to a list if it's a numpy array
        if isinstance(x, np.ndarray):
            x = x.flatten().tolist()

        # Check if indices are valid for this sequence
        max_index = max(self.projection_indices) if self.projection_indices else -1
        if max_index >= len(x):
            raise ValueError(
                f"Projection index {max_index} out of bounds for sequence of length {len(x)}"
            )

        # Project onto the selected coordinates
        projected_components = [x[i] for i in self.projection_indices if i < len(x)]

        # Compute the Euclidean norm of the projected components
        return np.sqrt(sum(abs(complex(c)) ** 2 for c in projected_components))

    def check_triangle_inequality(self, x: InputType, y: InputType) -> bool:
        """
        Check if the triangle inequality property holds for the given inputs.

        The triangle inequality states that:
        ||x + y|| ≤ ||x|| + ||y||

        Parameters
        ----------
        x : InputType
            First input to check
        y : InputType
            Second input to check

        Returns
        -------
        bool
            True if the triangle inequality holds, False otherwise

        Raises
        ------
        TypeError
            If the input types are not supported or compatible
        ValueError
            If the check cannot be performed on the given inputs
        """
        logger.debug(
            f"Checking triangle inequality for inputs of types {type(x)} and {type(y)}"
        )

        # Compute norms
        norm_x = self.compute(x)
        norm_y = self.compute(y)

        # Compute x + y
        if isinstance(x, IVector) and isinstance(y, IVector):
            sum_xy = x + y
        elif isinstance(x, IMatrix) and isinstance(y, IMatrix):
            sum_xy = x + y
        elif isinstance(x, (list, tuple)) and isinstance(y, (list, tuple)):
            if len(x) != len(y):
                raise ValueError("Sequences must have the same length for addition")
            sum_xy = [x[i] + y[i] for i in range(len(x))]
        elif isinstance(x, np.ndarray) and isinstance(y, np.ndarray):
            if x.shape != y.shape:
                raise ValueError("Arrays must have the same shape for addition")
            sum_xy = x + y
        else:
            raise TypeError(
                f"Unsupported or incompatible input types: {type(x)} and {type(y)}"
            )

        # Compute norm of the sum
        norm_sum = self.compute(sum_xy)

        # Check triangle inequality
        # Use a small epsilon for floating-point comparison
        epsilon = 1e-10
        return norm_sum <= norm_x + norm_y + epsilon

    def check_scalar_homogeneity(self, x: InputType, alpha: T) -> bool:
        """
        Check if the scalar homogeneity property holds for the given input and scalar.

        The scalar homogeneity states that:
        ||αx|| = |α|·||x||

        Parameters
        ----------
        x : InputType
            The input to check
        alpha : T
            The scalar to multiply by

        Returns
        -------
        bool
            True if scalar homogeneity holds, False otherwise

        Raises
        ------
        TypeError
            If the input type is not supported
        ValueError
            If the check cannot be performed on the given input
        """
        logger.debug(
            f"Checking scalar homogeneity for input of type {type(x)} with scalar {alpha}"
        )

        # Compute ||x||
        norm_x = self.compute(x)

        # Compute αx
        if isinstance(x, IVector):
            alpha_x = x * alpha
        elif isinstance(x, IMatrix):
            alpha_x = x * alpha
        elif isinstance(x, (list, tuple)):
            alpha_x = [complex(item) * alpha for item in x]
        elif isinstance(x, np.ndarray):
            alpha_x = x * alpha
        else:
            raise TypeError(f"Unsupported input type: {type(x)}")

        # Compute ||αx||
        norm_alpha_x = self.compute(alpha_x)

        # Compute |α|·||x||
        abs_alpha_times_norm_x = abs(complex(alpha)) * norm_x

        # Check scalar homogeneity
        # Use a small epsilon for floating-point comparison
        epsilon = 1e-10
        return abs(norm_alpha_x - abs_alpha_times_norm_x) < epsilon
