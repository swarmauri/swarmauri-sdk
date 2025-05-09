from typing import Literal, Optional, Sequence, Union
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.similarities.SimilarityBase import SimilarityBase
import numpy as np
import logging

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "BrayCurtisSimilarity")
class BrayCurtisSimilarity(SimilarityBase):
    """
    Provides implementation for Bray-Curtis similarity measure.

    The Bray-Curtis similarity is a normalized measure of similarity
    between two vectors, commonly used in ecology. It is calculated as:

    S = 1 - (sum(|x_i - y_i|) / sum(x_i + y_i))

    This implementation ensures non-negativity of input vectors and provides
    comprehensive validation of input data.
    """

    type: Literal["BrayCurtisSimilarity"] = "BrayCurtisSimilarity"
    resource: Optional[str] = "SIMILARITY"

    def __init__(self):
        """
        Initializes the BrayCurtisSimilarity instance.
        """
        super().__init__()
        logger.debug("BrayCurtisSimilarity instance initialized")

    def similarity(
        self,
        x: Union[np.ndarray, Sequence[float]],
        y: Union[np.ndarray, Sequence[float]],
    ) -> float:
        """
        Calculates the Bray-Curtis similarity between two non-negative vectors.

        Args:
            x: First vector for comparison
            y: Second vector for comparison

        Returns:
            float: Similarity score between 0 and 1

        Raises:
            ValueError: If input vectors are invalid
        """
        logger.debug(f"Calculating Bray-Curtis similarity between vectors {x} and {y}")

        # Validate input vectors
        self._validate_vectors(x, y)

        # Convert to numpy arrays for efficient computation
        x_vec = np.asarray(x, dtype=np.float64)
        y_vec = np.asarray(y, dtype=np.float64)

        # Compute absolute differences sum
        difference = np.sum(np.abs(x_vec - y_vec))

        # Compute total sum of both vectors
        total = np.sum(x_vec + y_vec)

        # Handle division by zero case
        if total == 0:
            logger.warning(
                "Both input vectors are zero vectors - similarity is 1 by definition"
            )
            return 1.0

        similarity = 1.0 - (difference / total)

        logger.debug(f"Bray-Curtis similarity score: {similarity}")
        return similarity

    def dissimilarity(
        self,
        x: Union[np.ndarray, Sequence[float]],
        y: Union[np.ndarray, Sequence[float]],
    ) -> float:
        """
        Calculates the Bray-Curtis dissimilarity between two vectors.
        This is simply 1 minus the similarity score.

        Args:
            x: First vector for comparison
            y: Second vector for comparison

        Returns:
            float: Dissimilarity score between 0 and 1
        """
        logger.debug(
            f"Calculating Bray-Curtis dissimilarity between vectors {x} and {y}"
        )
        return 1.0 - self.similarity(x, y)

    def check_boundedness(self) -> bool:
        """
        Checks if the similarity measure is bounded.
        Bray-Curtis similarity is bounded between 0 and 1.

        Returns:
            bool: True if the measure is bounded, False otherwise
        """
        return True

    def check_reflexivity(self) -> bool:
        """
        Checks if the similarity measure satisfies reflexivity.
        Bray-Curtis similarity is reflexive as s(x, x) = 1 for all x.

        Returns:
            bool: True if the measure is reflexive, False otherwise
        """
        return True

    def check_symmetry(self) -> bool:
        """
        Checks if the similarity measure is symmetric.
        Bray-Curtis similarity is symmetric as s(x, y) = s(y, x).

        Returns:
            bool: True if the measure is symmetric, False otherwise
        """
        return True

    def check_identity(self) -> bool:
        """
        Checks if the similarity measure satisfies identity of discernibles.
        Bray-Curtis similarity satisfies this property as s(x, y) = 1 if and only if x = y.

        Returns:
            bool: True if the measure satisfies identity of discernibles, False otherwise
        """
        return True

    def _validate_vectors(
        self,
        x: Union[np.ndarray, Sequence[float]],
        y: Union[np.ndarray, Sequence[float]],
    ) -> None:
        """
        Validates input vectors for Bray-Curtis similarity calculation.

        Args:
            x: First vector to validate
            y: Second vector to validate

        Raises:
            ValueError: If vectors contain negative values or have different lengths
        """
        if len(x) != len(y):
            raise ValueError("Input vectors must have the same length")

        if np.any(np.array(x) < 0) or np.any(np.array(y) < 0):
            raise ValueError("Input vectors must contain non-negative values")
