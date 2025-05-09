from typing import Union, Sequence, Optional, TypeVar
import logging
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.seminorms.ISeminorm import ISeminorm

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar("T", Union[Sequence[float], Sequence[Sequence[float]], str, callable])


@ComponentBase.register_type(SeminormBase, "PartialSumSeminorm")
class PartialSumSeminorm(SeminormBase):
    """
    A concrete implementation of SeminormBase that computes the seminorm by summing
    only a specified part of the input vector.

    Attributes:
        start: int
            The starting index (inclusive) of the segment to consider.
        end: int
            The ending index (exclusive) of the segment to consider.
        resource: str
            The resource type identifier for this component.
    """

    resource: str = ResourceTypes.SEMINORM.value

    def __init__(self, start: int = 0, end: Optional[int] = None):
        """
        Initialize the PartialSumSeminorm instance.

        Args:
            start: int
                The starting index (inclusive) of the segment to sum.
                Defaults to 0.
            end: Optional[int]
                The ending index (exclusive) of the segment to sum.
                Defaults to None, which means the end of the input.
        """
        super().__init__()
        self.start = start
        self.end = end
        logger.debug(
            "Initialized PartialSumSeminorm with start=%d, end=%s",
            start,
            end if end is not None else "None",
        )

    def compute(self, input: T) -> float:
        """
        Compute the seminorm by summing the specified segment of the input.

        Args:
            input: T
                The input to compute the seminorm on. This should be an iterable
                of numeric values.

        Returns:
            float
                The computed seminorm value.

        Raises:
            ValueError
                If the input is not iterable or the indices are out of bounds.
        """
        try:
            # Convert input to list for indexing operations
            input_list = list(input)

            # Get the actual end index, defaulting to the length of the input
            actual_end = self.end if self.end is not None else len(input_list)

            # Validate indices
            if self.start >= len(input_list):
                raise ValueError(
                    f"Start index {self.start} exceeds input length {len(input_list)}"
                )
            if actual_end > len(input_list):
                raise ValueError(
                    f"End index {actual_end} exceeds input length {len(input_list)}"
                )

            # Slice the input based on start and end indices
            segment = input_list[self.start : actual_end]

            # Compute the sum of absolute values
            return sum(abs(x) for x in segment)

        except Exception as e:
            logger.error("Error during compute: %s", str(e))
            raise

    def check_triangle_inequality(self, a: T, b: T) -> bool:
        """
        Check the triangle inequality for this seminorm.

        The triangle inequality states that:
        seminorm(a + b) <= seminorm(a) + seminorm(b)

        Args:
            a: T
                The first input vector.
            b: T
                The second input vector.

        Returns:
            bool
                True if the triangle inequality holds, False otherwise.
        """
        try:
            # Compute seminorms
            seminorm_a = self.compute(a)
            seminorm_b = self.compute(b)
            seminorm_ab = self.compute([a[i] + b[i] for i in range(len(a))])

            # Check inequality
            return seminorm_ab <= seminorm_a + seminorm_b

        except Exception as e:
            logger.error("Error during triangle inequality check: %s", str(e))
            return False

    def check_scalar_homogeneity(self, a: T, scalar: float) -> bool:
        """
        Check the scalar homogeneity property.

        The property states that for any scalar c >= 0:
        seminorm(c * a) = c * seminorm(a)

        Args:
            a: T
                The input vector to check.
            scalar: float
                The scalar to check against.

        Returns:
            bool
                True if scalar homogeneity holds, False otherwise.
        """
        try:
            if scalar < 0:
                raise ValueError("Scalar must be non-negative")

            # Compute original seminorm
            original = self.compute(a)

            # Compute scaled seminorm
            scaled = self.compute([scalar * x for x in a])

            # Check homogeneity
            return scaled == scalar * original

        except Exception as e:
            logger.error("Error during scalar homogeneity check: %s", str(e))
            return False
