import numpy as np
import logging
from typing import Union, Sequence, Tuple
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.similarities.SimilarityBase import SimilarityBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "CosineSimilarity")
class CosineSimilarity(SimilarityBase):
    """
    Computes the cosine similarity between vectors.

    This class implements the cosine similarity measure, which calculates the
    cosine of the angle between two vectors. The result indicates how similar
    the direction of the vectors is, with 1 meaning identical direction and -1
    meaning opposite directions.

    Inherits From:
        SimilarityBase: Base class for similarity measures

    Attributes:
        type: Literal["CosineSimilarity"] = "CosineSimilarity"
            Specifies the type of similarity measure
    """
    type: Literal["CosineSimilarity"] = "CosineSimilarity"

    def similarity(
            self, 
            a: Union[np.ndarray, None], 
            b: Union[np.ndarray, None]
    ) -> float:
        """
        Computes the cosine similarity between two vectors.

        The cosine similarity is calculated as the dot product of the vectors
        divided by the product of their magnitudes (norms). This implementation
        assumes non-zero vectors as per the problem constraints.

        Args:
            a: Union[np.ndarray, None]
                The first vector
            b: Union[np.ndarray, None]
                The second vector

        Returns:
            float:
                The cosine similarity score between the two vectors

        Raises:
            ValueError:
                If either vector is None or zero vector
        """
        if a is None or b is None:
            logger.error("Vectors cannot be None for cosine similarity calculation")
            raise ValueError("Vectors cannot be None")

        if np.count_nonzero(a) == 0 or np.count_nonzero(b) == 0:
            logger.error("Zero vectors are not allowed")
            raise ValueError("Zero vectors are not allowed")

        # Compute dot product
        dot_product = np.dot(a, b)
        # Compute norms
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        # Handle division by zero
        if norm_a == 0 or norm_b == 0:
            logger.error("Division by zero in cosine similarity calculation")
            raise ValueError("Division by zero in norms")

        similarity = dot_product / (norm_a * norm_b)
        logger.debug(f"Calculated cosine similarity: {similarity}")
        return similarity

    def similarities(
            self, 
            a: Union[np.ndarray, None], 
            b_list: Sequence[Union[np.ndarray, None]]
    ) -> Tuple[float, ...]:
        """
        Computes cosine similarities between one vector and a list of vectors.

        Args:
            a: Union[np.ndarray, None]
                The reference vector
            b_list: Sequence[Union[np.ndarray, None]]
                List of vectors to compare against

        Returns:
            Tuple[float, ...]:
                Tuple of cosine similarity scores

        Raises:
            ValueError:
                If input vectors are invalid
        """
        if a is None or len(b_list) == 0:
            logger.error("Invalid input for similarities calculation")
            raise ValueError("Invalid input vectors")

        similarities = []
        for b in b_list:
            try:
                sim = self.similarity(a, b)
                similarities.append(sim)
            except ValueError as e:
                logger.error(f"Error calculating similarity: {str(e)}")
                raise

        return tuple(similarities)

    def dissimilarity(
            self, 
            a: Union[np.ndarray, None], 
            b: Union[np.ndarray, None]
    ) -> float:
        """
        Computes the dissimilarity score as 1 - similarity.

        Args:
            a: Union[np.ndarray, None]
                The first vector
            b: Union[np.ndarray, None]
                The second vector

        Returns:
            float:
                The dissimilarity score
        """
        sim = self.similarity(a, b)
        dissim = 1.0 - sim
        logger.debug(f"Calculated dissimilarity: {dissim}")
        return dissim

    def dissimilarities(
            self, 
            a: Union[np.ndarray, None], 
            b_list: Sequence[Union[np.ndarray, None]]
    ) -> Tuple[float, ...]:
        """
        Computes dissimilarity scores for one vector against a list.

        Args:
            a: Union[np.ndarray, None]
                The reference vector
            b_list: Sequence[Union[np.ndarray, None]]
                List of vectors to compare against

        Returns:
            Tuple[float, ...]:
                Tuple of dissimilarity scores
        """
        sims = self.similarities(a, b_list)
        dissims = tuple(1.0 - sim for sim in sims)
        logger.debug(f"Calculated dissimilarities: {dissims}")
        return dissims

    def check_boundedness(
            self, 
            a: Union[np.ndarray, None], 
            b: Union[np.ndarray, None]
    ) -> bool:
        """
        Checks if the similarity measure is bounded.

        Cosine similarity is bounded between -1 and 1.

        Args:
            a: Union[np.ndarray, None]
                The first vector (unused)
            b: Union[np.ndarray, None]
                The second vector (unused)

        Returns:
            bool:
            True if the measure is bounded, False otherwise
        """
        return True

    def check_reflexivity(
            self, 
            a: Union[np.ndarray, None]
    ) -> bool:
        """
        Checks if the similarity measure is reflexive.

        For cosine similarity, s(x, x) = 1.

        Args:
            a: Union[np.ndarray, None]
                The vector to check reflexivity for

        Returns:
            bool:
            True if the measure is reflexive
        """
        if a is None or np.count_nonzero(a) == 0:
            return False
        return True

    def check_symmetry(
            self, 
            a: Union[np.ndarray, None], 
            b: Union[np.ndarray, None]
    ) -> bool:
        """
        Checks if the similarity measure is symmetric.

        Cosine similarity is symmetric as s(x, y) = s(y, x).

        Args:
            a: Union[np.ndarray, None]
                The first vector (unused)
            b: Union[np.ndarray, None]
                The second vector (unused)

        Returns:
            bool:
            True if the measure is symmetric
        """
        return True

    def check_identity(
            self, 
            a: Union[np.ndarray, None], 
            b: Union[np.ndarray, None]
    ) -> bool:
        """
        Checks if the similarity measure satisfies identity.

        For cosine similarity, s(x, y) = 1 if and only if x = y.

        Args:
            a: Union[np.ndarray, None]
                The first vector
            b: Union[np.ndarray, None]
                The second vector

        Returns:
            bool:
            True if x and y are identical
        """
        if a is None or b is None:
            return False
        return np.array_equal(a, b)