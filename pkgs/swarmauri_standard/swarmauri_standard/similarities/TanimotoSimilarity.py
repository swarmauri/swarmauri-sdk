import logging
from typing import List, Literal, Sequence

import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.similarities.SimilarityBase import SimilarityBase
from swarmauri_core.similarities.ISimilarity import ComparableType

# Set up logger
logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "TanimotoSimilarity")
class TanimotoSimilarity(SimilarityBase):
    """
    Tanimoto Similarity implementation, a generalization of Jaccard for real vectors.

    The Tanimoto coefficient is widely used in cheminformatics for measuring
    the similarity between molecular fingerprints. It is defined as the ratio of
    the intersection to the union when applied to binary vectors, and extends to
    real-valued vectors.

    For real-valued vectors, the formula is:
        T(A,B) = (A·B) / (|A|^2 + |B|^2 - A·B)

    where A·B is the dot product, and |A|^2 is the sum of squares of elements.

    Attributes
    ----------
    type : Literal["TanimotoSimilarity"]
        Type identifier for this similarity measure
    """

    type: Literal["TanimotoSimilarity"] = "TanimotoSimilarity"

    def _validate_input(self, x: ComparableType, y: ComparableType) -> tuple:
        """
        Validate and convert inputs to numpy arrays.

        Parameters
        ----------
        x : ComparableType
            First vector to compare
        y : ComparableType
            Second vector to compare

        Returns
        -------
        tuple
            Tuple of validated numpy arrays

        Raises
        ------
        TypeError
            If inputs cannot be converted to numeric arrays
        ValueError
            If inputs have different dimensions or are zero vectors
        """
        try:
            # Convert to numpy arrays
            x_array = np.array(x, dtype=float)
            y_array = np.array(y, dtype=float)

            # Check dimensions
            if x_array.shape != y_array.shape:
                raise ValueError(
                    f"Input vectors must have the same dimensions: {x_array.shape} != {y_array.shape}"
                )

            # Check for zero vectors
            if np.all(x_array == 0) or np.all(y_array == 0):
                raise ValueError("Tanimoto similarity is not defined for zero vectors")

            return x_array, y_array
        except Exception as e:
            logger.error(f"Input validation error: {str(e)}")
            raise

    def similarity(self, x: ComparableType, y: ComparableType) -> float:
        """
        Calculate the Tanimoto similarity between two vectors.

        Parameters
        ----------
        x : ComparableType
            First vector to compare
        y : ComparableType
            Second vector to compare

        Returns
        -------
        float
            Tanimoto similarity score between x and y, in range [0,1]

        Raises
        ------
        ValueError
            If vectors have different dimensions or are zero vectors
        TypeError
            If inputs cannot be converted to numeric arrays
        """
        try:
            x_array, y_array = self._validate_input(x, y)

            # Check if vectors are proportional (one is a scalar multiple of the other)
            # Find ratio for first non-zero element pair
            ratio = None
            for i in range(len(x_array)):
                if y_array[i] != 0 and x_array[i] != 0:
                    ratio = x_array[i] / y_array[i]
                    break

            if ratio is not None:
                # Check if all elements maintain this ratio (allowing for floating point error)
                is_proportional = True
                for i in range(len(x_array)):
                    if x_array[i] == 0 and y_array[i] == 0:
                        continue  # Both elements are zero, ratio is preserved
                    elif x_array[i] == 0 or y_array[i] == 0:
                        is_proportional = False  # One element is zero, the other isn't
                        break
                    elif abs(x_array[i] / y_array[i] - ratio) > 1e-10:
                        is_proportional = False  # Ratio differs
                        break

                if is_proportional:
                    return 1.0  # Proportional vectors have similarity 1.0

            # Calculate dot product
            dot_product = np.dot(x_array, y_array)

            # Calculate sum of squares
            sum_squares_x = np.sum(x_array**2)
            sum_squares_y = np.sum(y_array**2)

            # Calculate Tanimoto coefficient
            denominator = sum_squares_x + sum_squares_y - dot_product

            # Avoid division by zero (though we already checked for zero vectors)
            if denominator == 0:
                return 0.0

            tanimoto = dot_product / denominator

            logger.debug(f"Tanimoto similarity: {tanimoto}")
            return float(tanimoto)
        except Exception as e:
            logger.error(f"Error calculating Tanimoto similarity: {str(e)}")
            raise

    def similarities(
        self, x: ComparableType, ys: Sequence[ComparableType]
    ) -> List[float]:
        """
        Calculate Tanimoto similarities between one vector and multiple other vectors.

        This implementation is optimized for multiple comparisons.

        Parameters
        ----------
        x : ComparableType
            Reference vector
        ys : Sequence[ComparableType]
            Sequence of vectors to compare against the reference

        Returns
        -------
        List[float]
            List of Tanimoto similarity scores between x and each element in ys

        Raises
        ------
        ValueError
            If any vectors have different dimensions or are zero vectors
        TypeError
            If any inputs cannot be converted to numeric arrays
        """
        try:
            # Convert reference vector to numpy array
            x_array = np.array(x, dtype=float)

            # Check for zero vector
            if np.all(x_array == 0):
                raise ValueError("Tanimoto similarity is not defined for zero vectors")

            # Precompute sum of squares for reference vector
            sum_squares_x = np.sum(x_array**2)

            results = []
            for y in ys:
                try:
                    y_array = np.array(y, dtype=float)

                    # Check dimensions
                    if x_array.shape != y_array.shape:
                        raise ValueError(
                            f"Input vectors must have the same dimensions: {x_array.shape} != {y_array.shape}"
                        )

                    # Check for zero vector
                    if np.all(y_array == 0):
                        raise ValueError(
                            "Tanimoto similarity is not defined for zero vectors"
                        )

                    # Calculate dot product
                    dot_product = np.dot(x_array, y_array)

                    # Calculate sum of squares for y
                    sum_squares_y = np.sum(y_array**2)

                    # Calculate Tanimoto coefficient
                    denominator = sum_squares_x + sum_squares_y - dot_product

                    # Avoid division by zero
                    if denominator == 0:
                        results.append(0.0)
                    else:
                        results.append(float(dot_product / denominator))

                except Exception as e:
                    logger.warning(f"Error calculating individual similarity: {str(e)}")
                    results.append(
                        float("nan")
                    )  # Use NaN to indicate calculation error

            return results
        except Exception as e:
            logger.error(f"Error calculating multiple Tanimoto similarities: {str(e)}")
            raise

    def dissimilarity(self, x: ComparableType, y: ComparableType) -> float:
        """
        Calculate the Tanimoto dissimilarity between two vectors.

        Parameters
        ----------
        x : ComparableType
            First vector to compare
        y : ComparableType
            Second vector to compare

        Returns
        -------
        float
            Tanimoto dissimilarity score between x and y, in range [0,1]

        Raises
        ------
        ValueError
            If vectors have different dimensions or are zero vectors
        TypeError
            If inputs cannot be converted to numeric arrays
        """
        try:
            # Tanimoto dissimilarity is 1 - similarity
            return 1.0 - self.similarity(x, y)
        except Exception as e:
            logger.error(f"Error calculating Tanimoto dissimilarity: {str(e)}")
            raise

    def check_bounded(self) -> bool:
        """
        Check if the Tanimoto similarity measure is bounded.

        Tanimoto similarity is bounded in the range [0,1].

        Returns
        -------
        bool
            True, as Tanimoto similarity is bounded in [0,1]
        """
        return True

    def check_reflexivity(self, x: ComparableType) -> bool:
        """
        Check if the Tanimoto similarity measure is reflexive: s(x,x) = 1.

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
        TypeError
            If the input cannot be converted to a numeric array
        ValueError
            If the input is a zero vector
        """
        try:
            # Convert to numpy array
            x_array = np.array(x, dtype=float)

            # Check for zero vector
            if np.all(x_array == 0):
                raise ValueError("Tanimoto similarity is not defined for zero vectors")

            # For non-zero vectors, Tanimoto similarity is reflexive
            # s(x,x) = (x·x) / (|x|^2 + |x|^2 - x·x) = |x|^2 / |x|^2 = 1

            # Calculate explicitly to verify
            dot_product = np.sum(x_array**2)  # x·x = sum of squares
            denominator = (
                dot_product + dot_product - dot_product
            )  # 2|x|^2 - |x|^2 = |x|^2

            similarity_value = dot_product / denominator

            # Use approximate equality to handle floating-point precision issues
            return abs(similarity_value - 1.0) < 1e-10
        except Exception as e:
            logger.error(f"Error checking reflexivity: {str(e)}")
            raise

    def check_symmetry(self, x: ComparableType, y: ComparableType) -> bool:
        """
        Check if the Tanimoto similarity measure is symmetric: s(x,y) = s(y,x).

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
            If vectors have different dimensions or are zero vectors
        TypeError
            If inputs cannot be converted to numeric arrays
        """
        try:
            # Tanimoto similarity is symmetric by definition
            # s(x,y) = (x·y) / (|x|^2 + |y|^2 - x·y) = (y·x) / (|y|^2 + |x|^2 - y·x) = s(y,x)

            # Calculate explicitly to verify
            similarity_xy = self.similarity(x, y)
            similarity_yx = self.similarity(y, x)

            # Use approximate equality to handle floating-point precision issues
            return abs(similarity_xy - similarity_yx) < 1e-10
        except Exception as e:
            logger.error(f"Error checking symmetry: {str(e)}")
            raise

    def check_identity_of_discernibles(
        self, x: ComparableType, y: ComparableType
    ) -> bool:
        """
        Check if the Tanimoto similarity measure satisfies the identity of discernibles:
        s(x,y) = 1 ⟺ x = y (proportional vectors).

        For Tanimoto similarity, s(x,y) = 1 if and only if x and y are proportional vectors.

        Parameters
        ----------
        x : ComparableType
            First vector to compare
        y : ComparableType
            Second vector to compare

        Returns
        -------
        bool
            True if the identity of discernibles property holds, False otherwise

        Raises
        ------
        ValueError
            If vectors have different dimensions or are zero vectors
        TypeError
            If inputs cannot be converted to numeric arrays
        """
        try:
            x_array, y_array = self._validate_input(x, y)

            # Calculate similarity
            similarity_value = self.similarity(x_array, y_array)

            # For Tanimoto, s(x,y) = 1 if and only if x and y are proportional vectors
            # Check if vectors are proportional (x = c*y for some constant c)
            if abs(similarity_value - 1.0) < 1e-10:
                # If similarity is 1, vectors should be proportional
                # Find ratio for first non-zero element
                ratio = None
                for i in range(len(x_array)):
                    if y_array[i] != 0 and x_array[i] != 0:
                        ratio = x_array[i] / y_array[i]
                        break

                if ratio is None:
                    # This shouldn't happen since we checked for zero vectors
                    return False

                # Check if all elements maintain this ratio (allowing for floating point error)
                for i in range(len(x_array)):
                    if x_array[i] == 0 and y_array[i] == 0:
                        continue  # Both elements are zero, ratio is preserved
                    elif x_array[i] == 0 or y_array[i] == 0:
                        return False  # One element is zero, the other isn't
                    elif abs(x_array[i] / y_array[i] - ratio) > 1e-10:
                        return False  # Ratio differs

                return True  # All elements maintain the same ratio
            else:
                # If similarity is not 1, vectors should not be proportional
                # Check if vectors are not proportional
                # We already know similarity < 1, so they're not proportional
                return True
        except Exception as e:
            logger.error(f"Error checking identity of discernibles: {str(e)}")
            raise
