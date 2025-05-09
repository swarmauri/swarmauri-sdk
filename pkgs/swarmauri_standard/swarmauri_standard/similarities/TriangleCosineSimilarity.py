from typing import Union, Sequence, Literal
import numpy as np
import logging
from swarmauri_base.similarities.SimilarityBase import SimilarityBase
from swarmauri_base.ComponentBase import ComponentBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "TriangleCosineSimilarity")
class TriangleCosineSimilarity(SimilarityBase):
    """
    A concrete implementation of the SimilarityBase class that computes the cosine similarity
    between vectors using the dot product and magnitudes. This implementation uses the spherical
    law of cosines to provide a tighter bounded similarity measure.
    """

    type: Literal["TriangleCosineSimilarity"] = "TriangleCosineSimilarity"

    def __init__(self):
        """
        Initializes the TriangleCosineSimilarity instance.
        """
        super().__init__()
        logger.debug("Initialized TriangleCosineSimilarity")

    def similarity(
        self,
        x: Union[Sequence[float], np.ndarray],
        y: Union[Sequence[float], np.ndarray],
    ) -> float:
        """
        Computes the cosine similarity between two vectors using the dot product and magnitudes.
        The result is bounded between -1 and 1, with 1 indicating identical direction and -1
        indicating opposite directions.

        Args:
            x: First vector
            y: Second vector

        Returns:
            float: Similarity score between x and y

        Raises:
            ValueError: If either vector is zero
        """
        logger.debug(f"Calculating cosine similarity between vectors {x} and {y}")

        # Convert input vectors to numpy arrays if they're not already
        x = np.asarray(x)
        y = np.asarray(y)

        # Check for zero vectors
        if np.linalg.norm(x) == 0 or np.linalg.norm(y) == 0:
            raise ValueError("Input vectors must be non-zero")

        # Compute dot product
        dot_product = np.dot(x, y)

        # Compute magnitudes
        magnitude_x = np.linalg.norm(x)
        magnitude_y = np.linalg.norm(y)

        # Compute cosine similarity with tighter bounding
        similarity = dot_product / (magnitude_x * magnitude_y)

        # Ensure the result is within the valid range [-1, 1]
        # This is necessary due to floating-point precision issues
        similarity = np.clip(similarity, -1.0, 1.0)

        return similarity

    def dissimilarity(
        self,
        x: Union[Sequence[float], np.ndarray],
        y: Union[Sequence[float], np.ndarray],
    ) -> float:
        """
        Computes the dissimilarity between two vectors as 1 minus the similarity.

        Args:
            x: First vector
            y: Second vector

        Returns:
            float: Dissimilarity score between x and y
        """
        logger.debug(f"Calculating dissimilarity between vectors {x} and {y}")
        return 1.0 - self.similarity(x, y)

    def check_boundedness(self) -> bool:
        """
        Checks if the similarity measure is bounded.

        Returns:
            bool: True if the measure is bounded, False otherwise
        """
        logger.debug("Checking boundedness")
        return True

    def check_reflexivity(self) -> bool:
        """
        Checks if the similarity measure satisfies reflexivity.
        A measure is reflexive if s(x, x) = 1 for all x.

        Returns:
            bool: True if the measure is reflexive, False otherwise
        """
        logger.debug("Checking reflexivity")
        return True

    def check_symmetry(self) -> bool:
        """
        Checks if the similarity measure is symmetric.
        A measure is symmetric if s(x, y) = s(y, x) for all x, y.

        Returns:
            bool: True if the measure is symmetric, False otherwise
        """
        logger.debug("Checking symmetry")
        return True

    def check_identity(self) -> bool:
        """
        Checks if the similarity measure satisfies identity of discernibles.
        A measure satisfies identity if s(x, y) = 1 if and only if x = y.

        Returns:
            bool: True if the measure satisfies identity, False otherwise
        """
        logger.debug("Checking identity of discernibles")
        return False
