import logging
import math
from typing import List, Literal, Sequence

import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.similarities.SimilarityBase import SimilarityBase
from swarmauri_core.similarities.ISimilarity import ComparableType

# Set up logger
logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "TriangleCosineSimilarity")
class TriangleCosineSimilarity(SimilarityBase):
    """
    Triangle Cosine Similarity implementation that compares direction between vectors.

    This similarity measure uses a tighter bound derived from the spherical law of cosines,
    providing a more accurate measure of directional similarity between non-zero vectors.

    Attributes
    ----------
    type : Literal["TriangleCosineSimilarity"]
        The type identifier for this similarity measure
    """

    type: Literal["TriangleCosineSimilarity"] = "TriangleCosineSimilarity"

    def _validate_vector(self, vector: ComparableType) -> np.ndarray:
        """
        Validate and convert input to numpy array.

        Parameters
        ----------
        vector : ComparableType
            Input vector to validate

        Returns
        -------
        np.ndarray
            Validated numpy array

        Raises
        ------
        TypeError
            If the input cannot be converted to a numpy array
        ValueError
            If the input is a zero vector
        """
        try:
            v = np.asarray(vector, dtype=float)
            if v.ndim == 0:
                raise ValueError("Input must be a vector, not a scalar")

            # Check for zero vector
            if np.allclose(v, 0):
                raise ValueError(
                    "Zero vectors are not allowed in TriangleCosineSimilarity"
                )

            return v
        except Exception as e:
            logger.error(f"Vector validation error: {str(e)}")
            raise

    def similarity(self, x: ComparableType, y: ComparableType) -> float:
        """
        Calculate the triangle cosine similarity between two vectors.

        Uses the dot product over the product of norms, with a tighter bound
        derived from the spherical law of cosines.

        Parameters
        ----------
        x : ComparableType
            First vector
        y : ComparableType
            Second vector

        Returns
        -------
        float
            Similarity score between x and y, in the range [0, 1]

        Raises
        ------
        ValueError
            If inputs are zero vectors or have incompatible dimensions
        TypeError
            If inputs cannot be converted to numpy arrays
        """
        try:
            # Validate and convert inputs
            x_array = self._validate_vector(x)
            y_array = self._validate_vector(y)

            # Check for compatible dimensions
            if x_array.shape != y_array.shape:
                raise ValueError(
                    f"Incompatible dimensions: {x_array.shape} vs {y_array.shape}"
                )

            # Calculate norms
            x_norm = np.linalg.norm(x_array)
            y_norm = np.linalg.norm(y_array)

            # Calculate dot product
            dot_product = np.dot(x_array, y_array)

            # Standard cosine similarity calculation
            cosine = dot_product / (x_norm * y_norm)

            # Clamp to handle floating point errors
            cosine = max(min(cosine, 1.0), -1.0)

            # Apply triangle-based transformation for tighter bounds
            # This transforms the range [-1, 1] to [0, 1] with a non-linear mapping
            # derived from the spherical law of cosines
            angle = math.acos(cosine)
            similarity = 1.0 - (angle / math.pi)

            return similarity

        except Exception as e:
            logger.error(f"Error calculating triangle cosine similarity: {str(e)}")
            raise

    def similarities(
        self, x: ComparableType, ys: Sequence[ComparableType]
    ) -> List[float]:
        """
        Calculate triangle cosine similarities between one vector and multiple others.

        Parameters
        ----------
        x : ComparableType
            Reference vector
        ys : Sequence[ComparableType]
            Sequence of vectors to compare against the reference

        Returns
        -------
        List[float]
            List of similarity scores between x and each element in ys

        Raises
        ------
        ValueError
            If any vectors are zero or have incompatible dimensions
        TypeError
            If any inputs cannot be converted to numpy arrays
        """
        try:
            # Validate reference vector once
            x_array = self._validate_vector(x)
            x_norm = np.linalg.norm(x_array)

            results = []
            for y in ys:
                try:
                    y_array = self._validate_vector(y)

                    # Check for compatible dimensions
                    if x_array.shape != y_array.shape:
                        raise ValueError(
                            f"Incompatible dimensions: {x_array.shape} vs {y_array.shape}"
                        )

                    y_norm = np.linalg.norm(y_array)
                    dot_product = np.dot(x_array, y_array)

                    # Standard cosine similarity calculation
                    cosine = dot_product / (x_norm * y_norm)

                    # Clamp to handle floating point errors
                    cosine = max(min(cosine, 1.0), -1.0)

                    # Apply triangle-based transformation
                    angle = math.acos(cosine)
                    similarity = 1.0 - (angle / math.pi)

                    results.append(similarity)
                except Exception as e:
                    logger.warning(
                        f"Error calculating similarity for one vector: {str(e)}"
                    )
                    # Append None or a default value, or re-raise based on requirements
                    results.append(float("nan"))

            return results

        except Exception as e:
            logger.error(
                f"Error calculating multiple triangle cosine similarities: {str(e)}"
            )
            raise

    def dissimilarity(self, x: ComparableType, y: ComparableType) -> float:
        """
        Calculate the triangle cosine dissimilarity between two vectors.

        Parameters
        ----------
        x : ComparableType
            First vector
        y : ComparableType
            Second vector

        Returns
        -------
        float
            Dissimilarity score between x and y, in the range [0, 1]

        Raises
        ------
        ValueError
            If inputs are zero vectors or have incompatible dimensions
        TypeError
            If inputs cannot be converted to numpy arrays
        """
        try:
            # Simply use 1 - similarity since our measure is bounded [0, 1]
            return 1.0 - self.similarity(x, y)
        except Exception as e:
            logger.error(f"Error calculating triangle cosine dissimilarity: {str(e)}")
            raise

    def check_bounded(self) -> bool:
        """
        Check if the similarity measure is bounded.

        The triangle cosine similarity is bounded in the range [0, 1].

        Returns
        -------
        bool
            True, as triangle cosine similarity is bounded
        """
        return True

    def check_reflexivity(self, x: ComparableType) -> bool:
        """
        Check if the similarity measure is reflexive: s(x,x) = 1.

        Parameters
        ----------
        x : ComparableType
            Vector to check reflexivity with

        Returns
        -------
        bool
            True if s(x,x) = 1, False otherwise

        Raises
        ------
        ValueError
            If input is a zero vector
        TypeError
            If input cannot be converted to a numpy array
        """
        try:
            x_array = self._validate_vector(x)
            similarity_value = self.similarity(x_array, x_array)
            return abs(similarity_value - 1.0) < 1e-10
        except Exception as e:
            logger.error(f"Error checking reflexivity: {str(e)}")
            raise

    def check_symmetry(self, x: ComparableType, y: ComparableType) -> bool:
        """
        Check if the similarity measure is symmetric: s(x,y) = s(y,x).

        Parameters
        ----------
        x : ComparableType
            First vector to compare
        y : ComparableType
            Second vector to compare

        Returns
        -------
        bool
            True if s(x,y) = s(y,x), False otherwise

        Raises
        ------
        ValueError
            If inputs are zero vectors or have incompatible dimensions
        TypeError
            If inputs cannot be converted to numpy arrays
        """
        try:
            # Validate inputs
            x_array = self._validate_vector(x)
            y_array = self._validate_vector(y)

            similarity_xy = self.similarity(x_array, y_array)
            similarity_yx = self.similarity(y_array, x_array)

            return abs(similarity_xy - similarity_yx) < 1e-10
        except Exception as e:
            logger.error(f"Error checking symmetry: {str(e)}")
            raise
