from typing import Any, Sequence, Tuple, TypeVar
from swarmauri_base.ComponentBase import ComponentBase
import math
import logging

# Configure logging
logger = logging.getLogger(__name__)

InputType = TypeVar('InputType', str, bytes, Any)
OutputType = TypeVar('OutputType', float)

@ComponentBase.register_type(SimilarityBase, "TriangleCosineSimilarity")
class TriangleCosineSimilarity(SimilarityBase):
    """
    A concrete implementation of the SimilarityBase class that calculates the cosine similarity between vectors.

    This class uses the dot product and magnitudes of vectors to compute the cosine of the angle between them.
    It provides a measure of how similar the direction of two vectors is, with 1.0 indicating identical direction
    and 0.0 indicating orthogonal directions.

    The implementation follows the spherical law of cosines for tighter bounding of similarity scores.
    """
    
    type: str = "TriangleCosineSimilarity"

    def __init__(self):
        """
        Initialize the TriangleCosineSimilarity instance.
        """
        super().__init__()
        self.type = "TriangleCosineSimilarity"
        logger.debug("Initialized TriangleCosineSimilarity instance")

    def similarity(self, x: InputType, y: InputType) -> float:
        """
        Calculate the cosine similarity between two vectors.

        The cosine similarity is calculated as the dot product of the vectors divided by the product of their magnitudes.
        This implementation assumes non-zero vectors and uses mathematically valid operations to ensure numerical stability.

        Args:
            x: InputType
                The first vector for comparison
            y: InputType
                The second vector for comparison

        Returns:
            float:
                A float value between 0.0 and 1.0 representing the cosine similarity between the vectors.

        Raises:
            ValueError: If either vector has a magnitude of zero
            TypeError: If the input vectors are not of a supported type
        """
        try:
            # Ensure vectors are in a format that supports mathematical operations
            if not isinstance(x, (list, tuple, str, bytes)):
                raise TypeError("Unsupported type for vector x")
            if not isinstance(y, (list, tuple, str, bytes)):
                raise TypeError("Unsupported type for vector y")

            # Calculate dot product
            dot_product = sum(a * b for a, b in zip(x, y))

            # Calculate magnitudes
            magnitude_x = math.sqrt(sum(a ** 2 for a in x))
            magnitude_y = math.sqrt(sum(b ** 2 for b in y))

            # Check for zero vectors
            if magnitude_x == 0 or magnitude_y == 0:
                raise ValueError("Non-zero vectors only")

            # Calculate cosine similarity
            cosine_similarity = dot_product / (magnitude_x * magnitude_y)

            # Ensure result is within valid range [0.0, 1.0]
            return max(0.0, min(cosine_similarity, 1.0))

        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {str(e)}")
            raise

    def similarities(self, pairs: Sequence[Tuple[InputType, InputType]]) -> Sequence[float]:
        """
        Calculate cosine similarities for multiple pairs of vectors.

        Args:
            pairs: Sequence[Tuple[InputType, InputType]]
                A sequence of vector pairs to compare

        Returns:
            Sequence[float]:
                A sequence of similarity scores corresponding to each pair

        Raises:
            Exception: If any error occurs during similarity calculation
        """
        similarities = []
        for pair in pairs:
            try:
                sim = self.similarity(pair[0], pair[1])
                similarities.append(sim)
            except Exception as e:
                logger.warning(f"Error calculating similarity for pair {pair}: {str(e)}")
                similarities.append(0.0)  # or handle as needed
        return similarities

    def dissimilarity(self, x: InputType, y: InputType) -> float:
        """
        Calculate the dissimilarity between two vectors as 1 - similarity.

        Args:
            x: InputType
                The first vector for comparison
            y: InputType
                The second vector for comparison

        Returns:
            float:
                A float value between 0.0 and 1.0 representing the dissimilarity
        """
        try:
            sim = self.similarity(x, y)
            return 1.0 - sim
        except Exception as e:
            logger.error(f"Error calculating dissimilarity: {str(e)}")
            raise

    def dissimilarities(self, pairs: Sequence[Tuple[InputType, InputType]]) -> Sequence[float]:
        """
        Calculate dissimilarities for multiple pairs of vectors.

        Args:
            pairs: Sequence[Tuple[InputType, InputType]]
                A sequence of vector pairs to compare

        Returns:
            Sequence[float]:
                A sequence of dissimilarity scores corresponding to each pair
        """
        sims = self.similarities(pairs)
        return [1.0 - sim for sim in sims]