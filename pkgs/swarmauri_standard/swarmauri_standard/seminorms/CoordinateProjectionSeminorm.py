from typing import Union, Sequence, Tuple, Optional, Literal
from abc import ABC
from swarmauri_core.seminorms.ISeminorm import ISeminorm
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix
import logging
from ..ComponentBase import ComponentBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SeminormBase, "CoordinateProjectionSeminorm")
class CoordinateProjectionSeminorm(SeminormBase):
    """
    A seminorm that projects the input onto a specified subset of coordinates.

    This class implements a seminorm that projects the input vector onto a specified
    subset of coordinates before computing the norm. The projection operation can
    lead to degeneracy since certain components of the vector are ignored.

    Attributes:
        _projection_indices: A tuple of indices to project onto.
    """

    type: Literal["CoordinateProjectionSeminorm"] = "CoordinateProjectionSeminorm"

    def __init__(self, projection_indices: Sequence[int]):
        """
        Initialize the CoordinateProjectionSeminorm instance.

        Args:
            projection_indices: A sequence of indices to project onto.
        """
        super().__init__()
        self._projection_indices = tuple(projection_indices)
        logger.debug(
            "Initialized CoordinateProjectionSeminorm with projection indices: %s",
            self._projection_indices,
        )

    def compute(self, input: Union[IVector, IMatrix, Sequence, str, Callable]) -> float:
        """
        Compute the seminorm of the given input by projecting onto the specified coordinates.

        Args:
            input: The input to compute the seminorm for. Can be a vector, matrix, or sequence.

        Returns:
            float: The computed seminorm value.

        Raises:
            ValueError: If the input type is not supported.
            TypeError: If the input is of incorrect type.
        """
        logger.debug("Computing seminorm for input: %s", input)

        if isinstance(input, IVector):
            projected_input = input.values[:, self._projection_indices]
        elif isinstance(input, IMatrix):
            projected_input = input.values[:, self._projection_indices]
        elif isinstance(input, Sequence):
            projected_input = [input[i] for i in self._projection_indices]
        else:
            raise ValueError(f"Unsupported input type: {type(input)}")

        # Compute the norm of the projected input
        return self._compute_norm(projected_input)

    def _compute_norm(self, vector: Union[Sequence[float], IMatrix]) -> float:
        """
        Compute the Euclidean norm of the projected vector.

        Args:
            vector: The projected vector to compute the norm for.

        Returns:
            float: The computed norm value.
        """
        # Default implementation uses L2 norm
        # Subclasses can override this for different norms
        return sum(x**2 for x in vector) ** 0.5

    def check_triangle_inequality(
        self, a: Union[IVector, IMatrix, Sequence], b: Union[IVector, IMatrix, Sequence]
    ) -> bool:
        """
        Check if the triangle inequality holds for the projected inputs.

        Args:
            a: The first input to check.
            b: The second input to check.

        Returns:
            bool: True if the triangle inequality holds, False otherwise.
        """
        logger.debug("Checking triangle inequality for projected inputs")

        seminorm_a = self.compute(a)
        seminorm_b = self.compute(b)
        seminorm_a_plus_b = self.compute(a + b)

        return seminorm_a_plus_b <= seminorm_a + seminorm_b

    def check_scalar_homogeneity(
        self, input: Union[IVector, IMatrix, Sequence], scalar: float
    ) -> bool:
        """
        Check if the seminorm satisfies scalar homogeneity for the projected input.

        Args:
            input: The input to check.
            scalar: The scalar to scale the input by.

        Returns:
            bool: True if scalar homogeneity holds, False otherwise.
        """
        logger.debug("Checking scalar homogeneity for projected input")

        original_seminorm = self.compute(input)
        scaled_input = scalar * input
        scaled_seminorm = self.compute(scaled_input)

        return abs(scaled_seminorm - abs(scalar) * original_seminorm) < 1e-9

    @property
    def projection_indices(self) -> Tuple[int]:
        """
        Get the indices used for projection.

        Returns:
            Tuple[int]: The indices used for projection.
        """
        return self._projection_indices
