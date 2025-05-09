from typing import Sequence, Tuple, TypeVar, Union
from swarmauri_base.similarities import SimilarityBase
from swarmauri_base.ComponentBase import ComponentBase
import math
import logging

# Configure logging
logger = logging.getLogger(__name__)

InputType = TypeVar("InputType", Sequence[float], Tuple[float, ...])
OutputType = TypeVar("OutputType", float)


@ComponentBase.register_type(SimilarityBase, "BhattacharyyaCoefficientSimilarity")
class BhattacharyyaCoefficientSimilarity(SimilarityBase):
    """
    A class to compute the Bhattacharyya Coefficient Similarity between two probability distributions.

    The Bhattacharyya Coefficient is a measure of similarity between two probability distributions.
    It is defined as the sum of the square roots of the product of corresponding probabilities.
    This implementation assumes that the input distributions are normalized, but it will automatically
    normalize them if they are not.

    Attributes:
        None

    Methods:
        similarity: Calculates the similarity between two distributions.
        similarities: Calculates similarities for multiple pairs of distributions.
    """

    type: Literal["BhattacharyyaCoefficientSimilarity"] = (
        "BhattacharyyaCoefficientSimilarity"
    )
    resource: str = "SIMILARITY"

    def __init__(self):
        """
        Initialize the BhattacharyyaCoefficientSimilarity instance.
        """
        super().__init__()
        logger.debug("Initialized BhattacharyyaCoefficientSimilarity instance")

    def similarity(self, x: InputType, y: InputType) -> float:
        """
        Calculate the Bhattacharyya Coefficient Similarity between two probability distributions.

        Args:
            x: InputType
                The first probability distribution
            y: InputType
                The second probability distribution

        Returns:
            float:
                The Bhattacharyya Coefficient Similarity value between x and y.
                The value ranges between 0 (completely dissimilar) and 1 (completely similar).

        Raises:
            ValueError: If the distributions have different lengths
            ValueError: If either distribution has a sum of zero
        """
        logger.debug("Calculating Bhattacharyya Coefficient Similarity")

        # Ensure both distributions have the same length
        if len(x) != len(y):
            raise ValueError("Distributions must have the same length")

        # Normalize the distributions if they are not already
        sum_x = sum(x)
        sum_y = sum(y)

        if sum_x == 0 or sum_y == 0:
            raise ValueError("Distribution sums to zero. Cannot normalize.")

        x_normalized = [xi / sum_x for xi in x]
        y_normalized = [yi / sum_y for yi in y]

        # Calculate the Bhattacharyya Coefficient
        bc = 0.0
        for xi, yi in zip(x_normalized, y_normalized):
            bc += math.sqrt(xi * yi)

        return bc

    def similarities(
        self, pairs: Sequence[Tuple[InputType, InputType]]
    ) -> Sequence[float]:
        """
        Calculate Bhattacharyya Coefficient Similarities for multiple pairs of distributions.

        Args:
            pairs: Sequence[Tuple[InputType, InputType]]
                A sequence of pairs of probability distributions to compare

        Returns:
            Sequence[float]:
                A sequence of Bhattacharyya Coefficient Similarity values corresponding to each pair
        """
        logger.debug(
            "Calculating Bhattacharyya Coefficient Similarities for multiple pairs"
        )
        return [self.similarity(x, y) for x, y in pairs]
