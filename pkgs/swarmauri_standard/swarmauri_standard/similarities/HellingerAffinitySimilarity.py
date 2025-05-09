from typing import Sequence, Tuple, TypeVar, Union
import logging
import math

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.similarities.ISimilarity import ISimilarity

# Configure logging
logger = logging.getLogger(__name__)

InputType = TypeVar("InputType", str, bytes, Union[float, int])
OutputType = TypeVar("OutputType", float)


@ComponentBase.register_model()
class HellingerAffinitySimilarity(SimilarityBase):
    """
    Implementation of the Hellinger affinity similarity measure for discrete probability distributions.

    This class provides a concrete implementation of the SimilarityBase class for calculating
    the Hellinger affinity between two probability vectors. The Hellinger affinity is
    defined as the square root of the sum of the square roots of the product of corresponding
    probabilities.

    The measure operates on discrete probability vectors and provides a similarity score
    in the range [0, 1], where 1 indicates identical distributions and 0 indicates complete
    dissimilarity.
    """

    resource: str = ResourceTypes.SIMILARITY.value
    type: Literal["HellingerAffinitySimilarity"] = "HellingerAffinitySimilarity"

    def __init__(self):
        """
        Initialize the HellingerAffinitySimilarity instance.
        """
        super().__init__()
        logger.debug("Initialized HellingerAffinitySimilarity instance")

    def similarity(self, x: InputType, y: InputType) -> float:
        """
        Calculate the Hellinger affinity similarity between two probability vectors.

        Args:
            x: InputType
                The first probability vector
            y: InputType
                The second probability vector

        Returns:
            float:
                The Hellinger affinity similarity score in the range [0, 1]

        Raises:
            ValueError: If input vectors are invalid probability distributions
        """
        logger.debug("Calculating Hellinger affinity similarity")

        # Validate input vectors
        if not self._is_valid_probability_vector(
            x
        ) or not self._is_valid_probability_vector(y):
            raise ValueError("Invalid probability vectors")

        # Calculate element-wise product and square root
        sqrt_products = [math.sqrt(x_i * y_i) for x_i, y_i in zip(x, y)]

        # Sum the square roots
        affinity = sum(sqrt_products)

        logger.debug(f"Hellinger affinity similarity score: {affinity}")
        return affinity

    def similarities(
        self, pairs: Sequence[Tuple[InputType, InputType]]
    ) -> Sequence[float]:
        """
        Calculate Hellinger affinity similarities for multiple pairs of probability vectors.

        Args:
            pairs: Sequence[Tuple[InputType, InputType]]
                A sequence of probability vector pairs to compare

        Returns:
            Sequence[float]:
                A sequence of Hellinger affinity similarity scores
        """
        logger.debug("Calculating Hellinger affinity similarities for multiple pairs")
        return [self.similarity(x, y) for x, y in pairs]

    def _is_valid_probability_vector(self, vector: InputType) -> bool:
        """
        Validate if a given vector is a valid probability distribution.

        Args:
            vector: InputType
                The vector to validate

        Returns:
            bool:
                True if the vector is a valid probability distribution, False otherwise
        """
        # Check if all elements are non-negative
        if any(value < 0 for value in vector):
            logger.error("Probability vector contains negative values")
            return False

        # Check if elements sum to 1 (allowing for floating point precision)
        total = sum(vector)
        if not math.isclose(total, 1.0, rel_tol=1e-9, abs_tol=1e-9):
            logger.error(f"Probability vector sums to {total}, not 1")
            return False

        return True
