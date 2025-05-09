from typing import Union, Sequence, Optional, Literal
from abc import ABC
import logging
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.seminorms.ISeminorm import ISeminorm
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SeminormBase, "PartialSumSeminorm")
class PartialSumSeminorm(SeminormBase):
    """
    A seminorm that computes the sum of a specified subset of elements
    in the input vector.

    This implementation allows for specifying a range of indices to be
    included in the summation process. The indices can be specified
    either by start and end indices or by a list of specific indices.

    Attributes:
        start: The starting index of the range to be summed (inclusive)
        end: The ending index of the range to be summed (exclusive)
        indices: Optional list of specific indices to be summed
    """

    type: Literal["PartialSumSeminorm"] = "PartialSumSeminorm"

    def __init__(
        self,
        start: int = 0,
        end: Optional[int] = None,
        indices: Optional[Sequence[int]] = None,
    ):
        """
        Initialize the PartialSumSeminorm object.

        Args:
            start: The starting index of the range to be summed (inclusive)
            end: The ending index of the range to be summed (exclusive)
            indices: Optional list of specific indices to be summed

        Raises:
            ValueError: If both end and indices are specified or if neither is specified
        """
        super().__init__()

        if (end is not None and indices is not None) or (
            end is None and indices is None
        ):
            raise ValueError(
                "Either specify end or indices, but not both and not neither"
            )

        self.start = start
        self.end = end
        self.indices = indices

    def compute(self, input: Union[IVector, IMatrix, Sequence, str, Callable]) -> float:
        """
        Compute the seminorm of the given input.

        The seminorm is computed as the sum of the elements in the specified
        range or at the specified indices.

        Args:
            input: The input to compute the seminorm for. Currently supports
                vectors, sequences, and strings.

        Returns:
            float: The computed seminorm value.

        Raises:
            NotImplementedError: If the input type is not supported
            ValueError: If the input is of incorrect type
        """
        logger.debug("Computing partial sum seminorm")

        if isinstance(input, (IVector, Sequence, str)):
            vector = list(input)

            if self.end is not None:
                # Slice from start to end
                elements = vector[self.start : self.end]
            else:
                # Use specified indices
                elements = [vector[i] for i in self.indices]

            return abs(sum(elements))

        elif isinstance(input, IMatrix):
            raise NotImplementedError("Matrix support not implemented")

        elif isinstance(input, Callable):
            raise NotImplementedError("Callable support not implemented")

        else:
            raise ValueError(f"Unsupported input type: {type(input)}")
