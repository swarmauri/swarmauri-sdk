from typing import Union, Sequence, Literal
import math
import logging

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.similarities.SimilarityBase import SimilarityBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "HellingerAffinitySimilarity")
class HellingerAffinitySimilarity(SimilarityBase):
    """
    A class that implements the Hellinger Affinity Similarity measure for discrete probability vectors.

    This measure is based on the square root of the sum of the product of square roots of corresponding probabilities.
    It works on discrete probability vectors and ensures values are non-negative and sum to 1.

    Inherits from:
        SimilarityBase: Base class for similarity measures providing foundational structures and interfaces.

    Implements:
        similarity() method: Computes the similarity between two probability vectors using Hellinger affinity formula.
    """

    type: Literal["HellingerAffinitySimilarity"] = "HellingerAffinitySimilarity"

    def __init__(self):
        """
        Initializes the HellingerAffinitySimilarity class.
        """
        super().__init__()
        self._resource_type = "SIMILARITY"

    def similarity(
        self, x: Union[Sequence[float], str], y: Union[Sequence[float], str]
    ) -> float:
        """
        Computes the Hellinger Affinity Similarity between two discrete probability vectors.

        Args:
            x: First probability vector (must sum to 1)
            y: Second probability vector (must sum to 1)

        Returns:
            float: Hellinger affinity similarity score between x and y

        Raises:
            ValueError: If input vectors are invalid (negative values or don't sum to 1)
        """
        logger.debug(f"Calculating Hellinger affinity similarity between {x} and {y}")

        # Validate input vectors
        self._validate_probability_vector(x)
        self._validate_probability_vector(y)

        # Calculate element-wise product of square roots
        sqrt_product = (math.sqrt(x_i) * math.sqrt(y_i) for x_i, y_i in zip(x, y))

        # Sum the products and take square root
        similarity = math.sqrt(sum(sqrt_product))

        return similarity

    def _validate_probability_vector(self, vector: Sequence[float]) -> None:
        """
        Validates if a given sequence is a valid probability vector.

        Args:
            vector: Sequence to validate

        Raises:
            ValueError: If vector contains negative values or does not sum to 1
        """
        if any(val < 0 for val in vector):
            raise ValueError("Probability vector contains negative values")
        if not math.isclose(sum(vector), 1.0, rel_tol=1e-9, abs_tol=1e-9):
            raise ValueError("Probability vector does not sum to 1")
