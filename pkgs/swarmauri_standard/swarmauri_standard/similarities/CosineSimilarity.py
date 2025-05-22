import logging
from typing import List, Literal, Sequence

import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.similarities.SimilarityBase import SimilarityBase
from swarmauri_core.similarities.ISimilarity import ComparableType

# Set up logger
logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "CosineSimilarity")
class CosineSimilarity(SimilarityBase):
    """
    Cosine similarity implementation that measures the cosine of the angle between two vectors.

    Cosine similarity is a measure of similarity between two non-zero vectors defined by the cosine of
    the angle between them. It is calculated as the dot product of the vectors divided by the product
    of their magnitudes. The result ranges from -1 to 1, where 1 means the vectors are identical in
    direction, 0 means they are orthogonal, and -1 means they are opposite.

    Attributes
    ----------
    type : Literal["CosineSimilarity"]
        Type identifier for this similarity measure
    """

    type: Literal["CosineSimilarity"] = "CosineSimilarity"

    def similarity(self, x: ComparableType, y: ComparableType) -> float:
        """
        Calculate the cosine similarity between two vectors.

        Parameters
        ----------
        x : ComparableType
            First vector
        y : ComparableType
            Second vector

        Returns
        -------
        float
            Cosine similarity between x and y, ranging from -1 to 1

        Raises
        ------
        ValueError
            If either vector has zero magnitude or incompatible dimensions
        TypeError
            If the input types are not numeric arrays or lists
        """
        try:
            # Convert inputs to numpy arrays if they aren't already
            x_array = np.array(x, dtype=float)
            y_array = np.array(y, dtype=float)

            # Check for compatible dimensions
            if x_array.shape != y_array.shape:
                raise ValueError(
                    f"Incompatible dimensions: {x_array.shape} vs {y_array.shape}"
                )

            # Calculate vector norms
            x_norm = np.linalg.norm(x_array)
            y_norm = np.linalg.norm(y_array)

            # Check for zero vectors
            if x_norm < 1e-10 or y_norm < 1e-10:
                raise ValueError("Cosine similarity is undefined for zero vectors")

            # Calculate dot product
            dot_product = np.dot(x_array, y_array)

            # Calculate cosine similarity
            cosine_sim = dot_product / (x_norm * y_norm)

            # Handle potential numerical errors that might push the value outside [-1, 1]
            if cosine_sim > 1.0:
                cosine_sim = 1.0
            elif cosine_sim < -1.0:
                cosine_sim = -1.0

            return float(cosine_sim)

        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {str(e)}")
            raise

    def similarities(
        self, x: ComparableType, ys: Sequence[ComparableType]
    ) -> List[float]:
        """
        Calculate cosine similarities between one vector and multiple other vectors.

        Parameters
        ----------
        x : ComparableType
            Reference vector
        ys : Sequence[ComparableType]
            Sequence of vectors to compare against the reference

        Returns
        -------
        List[float]
            List of cosine similarity scores between x and each element in ys

        Raises
        ------
        ValueError
            If any vector has zero magnitude or incompatible dimensions
        TypeError
            If any input types are not numeric arrays or lists
        """
        try:
            # Convert reference vector to numpy array
            x_array = np.array(x, dtype=float)
            x_norm = np.linalg.norm(x_array)

            if x_norm < 1e-10:
                raise ValueError("Cosine similarity is undefined for zero vectors")

            results = []
            for y in ys:
                y_array = np.array(y, dtype=float)

                # Check for compatible dimensions
                if x_array.shape != y_array.shape:
                    raise ValueError(
                        f"Incompatible dimensions: {x_array.shape} vs {y_array.shape}"
                    )

                y_norm = np.linalg.norm(y_array)

                if y_norm < 1e-10:
                    raise ValueError("Cosine similarity is undefined for zero vectors")

                dot_product = np.dot(x_array, y_array)
                cosine_sim = dot_product / (x_norm * y_norm)

                # Handle potential numerical errors
                if cosine_sim > 1.0:
                    cosine_sim = 1.0
                elif cosine_sim < -1.0:
                    cosine_sim = -1.0

                results.append(float(cosine_sim))

            return results

        except Exception as e:
            logger.error(f"Error calculating multiple cosine similarities: {str(e)}")
            raise

    def dissimilarity(self, x: ComparableType, y: ComparableType) -> float:
        """
        Calculate the cosine dissimilarity between two vectors.

        For cosine similarity, dissimilarity is defined as 1 - similarity for
        the normalized range [0, 1], which corresponds to the angle-based distance.

        Parameters
        ----------
        x : ComparableType
            First vector
        y : ComparableType
            Second vector

        Returns
        -------
        float
            Cosine dissimilarity between x and y, ranging from 0 to 2

        Raises
        ------
        ValueError
            If either vector has zero magnitude or incompatible dimensions
        TypeError
            If the input types are not numeric arrays or lists
        """
        try:
            # Cosine dissimilarity is 1 - cosine similarity for normalized values
            # This maps the range [-1, 1] to [0, 2]
            similarity_value = self.similarity(x, y)
            return 1.0 - similarity_value

        except Exception as e:
            logger.error(f"Error calculating cosine dissimilarity: {str(e)}")
            raise

    def check_bounded(self) -> bool:
        """
        Check if the similarity measure is bounded.

        Cosine similarity is bounded in the range [-1, 1].

        Returns
        -------
        bool
            True, as cosine similarity is bounded
        """
        return True

    def check_symmetry(self, x: ComparableType, y: ComparableType) -> bool:
        """
        Check if the cosine similarity measure is symmetric: s(x,y) = s(y,x).

        Cosine similarity is inherently symmetric due to the commutative property
        of the dot product.

        Parameters
        ----------
        x : ComparableType
            First vector
        y : ComparableType
            Second vector

        Returns
        -------
        bool
            True, as cosine similarity is symmetric

        Raises
        ------
        ValueError
            If either vector has zero magnitude or incompatible dimensions
        TypeError
            If the input types are not numeric arrays or lists
        """
        try:
            # Cosine similarity is symmetric by definition
            # But we'll verify with an explicit check
            similarity_xy = self.similarity(x, y)
            similarity_yx = self.similarity(y, x)
            return abs(similarity_xy - similarity_yx) < 1e-10

        except Exception as e:
            logger.error(f"Error checking symmetry: {str(e)}")
            raise

    def check_identity_of_discernibles(
        self, x: ComparableType, y: ComparableType
    ) -> bool:
        """
        Check if the cosine similarity measure satisfies the identity of discernibles.

        For cosine similarity, this property is partially satisfied: parallel vectors
        with the same direction (even with different magnitudes) will have a similarity of 1.

        Parameters
        ----------
        x : ComparableType
            First vector
        y : ComparableType
            Second vector

        Returns
        -------
        bool
            True if the identity of discernibles property holds, False otherwise

        Raises
        ------
        ValueError
            If either vector has zero magnitude or incompatible dimensions
        TypeError
            If the input types are not numeric arrays or lists
        """
        try:
            # Convert inputs to numpy arrays
            x_array = np.array(x, dtype=float)
            y_array = np.array(y, dtype=float)

            # Check for zero vectors
            x_norm = np.linalg.norm(x_array)
            y_norm = np.linalg.norm(y_array)

            if x_norm < 1e-10 or y_norm < 1e-10:
                raise ValueError("Cosine similarity is undefined for zero vectors")

            # For cosine similarity, vectors are "identical" (sim=1) if they point in the same direction
            # This means they are scalar multiples of each other
            similarity_value = self.similarity(x, y)

            # Check if vectors are parallel (same direction)
            are_parallel = abs(similarity_value - 1.0) < 1e-10

            # For the identity of discernibles, we need to check if:
            # 1. If vectors are identical (same direction and magnitude), similarity should be 1
            # 2. If vectors are different in any way, similarity should be < 1

            # Check if vectors are identical (same values)
            are_identical = np.array_equal(x_array, y_array)

            # For cosine similarity, the identity of discernibles is satisfied if:
            # - Identical vectors have similarity 1 (always true for non-zero vectors)
            # - Different vectors that are not parallel have similarity < 1

            if are_identical:
                return are_parallel  # Should be True for identical non-zero vectors
            else:
                # For different vectors, we only care if the similarity correctly reflects
                # whether they're parallel or not
                if are_parallel:
                    # If vectors differ but are parallel, they're scalar multiples
                    # For cosine similarity, this is still considered "identical" in direction
                    return True
                else:
                    # If vectors are different and not parallel, similarity should be < 1
                    return similarity_value < 1.0 - 1e-10

        except Exception as e:
            logger.error(f"Error checking identity of discernibles: {str(e)}")
            raise
