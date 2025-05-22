import logging
from typing import List, Literal, Sequence

import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.similarities.SimilarityBase import SimilarityBase
from swarmauri_core.similarities.ISimilarity import ComparableType

# Set up logger
logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "BrayCurtisSimilarity")
class BrayCurtisSimilarity(SimilarityBase):
    """
    Bray-Curtis similarity measure.

    This similarity measure is commonly used in ecology to quantify the compositional
    dissimilarity between two samples. It is based on the ratio of the sum of the absolute
    differences to the sum of the abundances.

    The Bray-Curtis similarity is calculated as 1 - (sum of absolute differences / sum of all values).

    Attributes
    ----------
    type : Literal["BrayCurtisSimilarity"]
        Type identifier for the similarity measure
    """

    type: Literal["BrayCurtisSimilarity"] = "BrayCurtisSimilarity"

    def _validate_input(self, x: ComparableType, y: ComparableType) -> tuple:
        """
        Validate that inputs are non-negative arrays or lists of the same length.

        Parameters
        ----------
        x : ComparableType
            First vector to compare
        y : ComparableType
            Second vector to compare

        Returns
        -------
        tuple
            Tuple of numpy arrays representing the validated inputs

        Raises
        ------
        ValueError
            If inputs contain negative values or have different lengths
        TypeError
            If inputs cannot be converted to numeric arrays
        """
        try:
            # Convert inputs to numpy arrays
            x_array = np.asarray(x, dtype=float)
            y_array = np.asarray(y, dtype=float)

            # Check if arrays have the same shape
            if x_array.shape != y_array.shape:
                raise ValueError(
                    f"Input vectors must have the same shape: {x_array.shape} != {y_array.shape}"
                )

            # Check for negative values
            if np.any(x_array < 0) or np.any(y_array < 0):
                raise ValueError(
                    "Bray-Curtis similarity requires non-negative input values"
                )

            return x_array, y_array

        except (TypeError, ValueError) as e:
            logger.error(f"Input validation error: {str(e)}")
            raise

    def similarity(self, x: ComparableType, y: ComparableType) -> float:
        """
        Calculate the Bray-Curtis similarity between two vectors.

        Parameters
        ----------
        x : ComparableType
            First vector to compare
        y : ComparableType
            Second vector to compare

        Returns
        -------
        float
            Bray-Curtis similarity between x and y

        Raises
        ------
        ValueError
            If inputs contain negative values or have different lengths
        TypeError
            If inputs cannot be converted to numeric arrays
        """
        try:
            x_array, y_array = self._validate_input(x, y)

            # Calculate sum of absolute differences
            sum_abs_diff = np.sum(np.abs(x_array - y_array))

            # Calculate sum of all values
            sum_all = np.sum(x_array) + np.sum(y_array)

            # If both vectors are all zeros, they are identical
            if sum_all == 0:
                return 1.0

            # Calculate Bray-Curtis similarity: 1 - (sum of abs differences / sum of all values)
            similarity_value = 1.0 - (sum_abs_diff / sum_all)

            return float(similarity_value)

        except Exception as e:
            logger.error(f"Error calculating Bray-Curtis similarity: {str(e)}")
            raise

    def similarities(
        self, x: ComparableType, ys: Sequence[ComparableType]
    ) -> List[float]:
        """
        Calculate Bray-Curtis similarities between one vector and multiple other vectors.

        Parameters
        ----------
        x : ComparableType
            Reference vector
        ys : Sequence[ComparableType]
            Sequence of vectors to compare against the reference

        Returns
        -------
        List[float]
            List of Bray-Curtis similarity scores between x and each element in ys

        Raises
        ------
        ValueError
            If any inputs contain negative values or have different lengths
        TypeError
            If any inputs cannot be converted to numeric arrays
        """
        try:
            # Convert x to numpy array once for efficiency
            x_array = np.asarray(x, dtype=float)

            # Check for negative values in x
            if np.any(x_array < 0):
                raise ValueError(
                    "Bray-Curtis similarity requires non-negative input values"
                )

            # Calculate sum of x once for efficiency
            sum_x = np.sum(x_array)

            result = []
            for y in ys:
                y_array = np.asarray(y, dtype=float)

                # Check if arrays have the same shape
                if x_array.shape != y_array.shape:
                    raise ValueError(
                        f"Input vectors must have the same shape: {x_array.shape} != {y_array.shape}"
                    )

                # Check for negative values in y
                if np.any(y_array < 0):
                    raise ValueError(
                        "Bray-Curtis similarity requires non-negative input values"
                    )

                sum_y = np.sum(y_array)
                sum_abs_diff = np.sum(np.abs(x_array - y_array))
                sum_all = sum_x + sum_y

                # If both vectors are all zeros, they are identical
                if sum_all == 0:
                    result.append(1.0)
                else:
                    similarity_value = 1.0 - (sum_abs_diff / sum_all)
                    result.append(float(similarity_value))

            return result

        except Exception as e:
            logger.error(
                f"Error calculating multiple Bray-Curtis similarities: {str(e)}"
            )
            raise

    def dissimilarity(self, x: ComparableType, y: ComparableType) -> float:
        """
        Calculate the Bray-Curtis dissimilarity between two vectors.

        Parameters
        ----------
        x : ComparableType
            First vector to compare
        y : ComparableType
            Second vector to compare

        Returns
        -------
        float
            Bray-Curtis dissimilarity between x and y

        Raises
        ------
        ValueError
            If inputs contain negative values or have different lengths
        TypeError
            If inputs cannot be converted to numeric arrays
        """
        try:
            x_array, y_array = self._validate_input(x, y)

            # Calculate sum of absolute differences
            sum_abs_diff = np.sum(np.abs(x_array - y_array))

            # Calculate sum of all values
            sum_all = np.sum(x_array) + np.sum(y_array)

            # If both vectors are all zeros, they are identical
            if sum_all == 0:
                return 0.0

            # Calculate Bray-Curtis dissimilarity directly: sum of abs differences / sum of all values
            dissimilarity_value = sum_abs_diff / sum_all

            return float(dissimilarity_value)

        except Exception as e:
            logger.error(f"Error calculating Bray-Curtis dissimilarity: {str(e)}")
            raise

    def check_bounded(self) -> bool:
        """
        Check if the Bray-Curtis similarity measure is bounded.

        The Bray-Curtis similarity is bounded in the range [0, 1].

        Returns
        -------
        bool
            True, as the Bray-Curtis similarity is bounded
        """
        return True

    def check_symmetry(self, x: ComparableType, y: ComparableType) -> bool:
        """
        Check if the Bray-Curtis similarity measure is symmetric.

        The Bray-Curtis similarity is symmetric: s(x,y) = s(y,x).

        Parameters
        ----------
        x : ComparableType
            First vector to compare
        y : ComparableType
            Second vector to compare

        Returns
        -------
        bool
            True, as the Bray-Curtis similarity is symmetric

        Raises
        ------
        ValueError
            If inputs contain negative values or have different lengths
        TypeError
            If inputs cannot be converted to numeric arrays
        """
        try:
            # Bray-Curtis similarity is symmetric by definition
            # We'll verify this empirically
            similarity_xy = self.similarity(x, y)
            similarity_yx = self.similarity(y, x)

            # Use approximate equality to handle floating-point precision issues
            return abs(similarity_xy - similarity_yx) < 1e-10

        except Exception as e:
            logger.error(f"Error checking symmetry: {str(e)}")
            raise
