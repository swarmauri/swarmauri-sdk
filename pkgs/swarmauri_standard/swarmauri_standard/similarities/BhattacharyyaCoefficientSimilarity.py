import logging
from typing import List, Literal, Sequence

import numpy as np
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.similarities.SimilarityBase import SimilarityBase
from swarmauri_core.similarities.ISimilarity import ComparableType

# Set up logger
logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "BhattacharyyaCoefficientSimilarity")
class BhattacharyyaCoefficientSimilarity(SimilarityBase):
    """
    Bhattacharyya Coefficient Similarity metric for measuring overlap between probability distributions.

    This similarity measure calculates the Bhattacharyya coefficient, which quantifies the
    amount of overlap between two probability distributions. It's commonly used for comparing
    histograms or probability density functions.

    The coefficient is defined as the sum of the square root of the product of corresponding
    probabilities from both distributions: BC(p,q) = ∑ √(p_i * q_i)

    Attributes
    ----------
    type : Literal["BhattacharyyaCoefficientSimilarity"]
        Type identifier for this similarity measure
    """

    type: Literal["BhattacharyyaCoefficientSimilarity"] = (
        "BhattacharyyaCoefficientSimilarity"
    )

    def similarity(self, x: ComparableType, y: ComparableType) -> float:
        """
        Calculate the Bhattacharyya coefficient between two probability distributions.

        Parameters
        ----------
        x : ComparableType
            First probability distribution (list, array, or dict)
        y : ComparableType
            Second probability distribution (list, array, or dict)

        Returns
        -------
        float
            Bhattacharyya coefficient between x and y (range [0,1])

        Raises
        ------
        ValueError
            If the distributions have incompatible dimensions or are not normalized
        TypeError
            If the input types are not supported
        """
        try:
            # Convert inputs to numpy arrays if they are lists
            if isinstance(x, dict) and isinstance(y, dict):
                # For dictionary representations of distributions
                # Ensure both dictionaries have the same keys
                all_keys = set(x.keys()).union(set(y.keys()))
                p = np.array([x.get(k, 0.0) for k in all_keys])
                q = np.array([y.get(k, 0.0) for k in all_keys])
            else:
                # For list/array representations
                p = np.array(x, dtype=float)
                q = np.array(y, dtype=float)

            # Check if distributions have the same dimensions
            if p.shape != q.shape:
                raise ValueError(
                    f"Distributions must have the same dimensions: {p.shape} != {q.shape}"
                )

            # Check for negative probabilities
            if np.any(p < 0) or np.any(q < 0):
                raise ValueError("Probability values must be non-negative")

            # Check if distributions are normalized (sum to 1)
            if not np.isclose(np.sum(p), 1.0, rtol=1e-5):
                raise ValueError(
                    f"First distribution is not normalized: sum = {np.sum(p)}"
                )
            if not np.isclose(np.sum(q), 1.0, rtol=1e-5):
                raise ValueError(
                    f"Second distribution is not normalized: sum = {np.sum(q)}"
                )

            # Calculate Bhattacharyya coefficient
            # BC(p,q) = ∑ √(p_i * q_i)
            bc = np.sum(np.sqrt(p * q))

            return float(bc)

        except (TypeError, ValueError) as e:
            logger.error(f"Error calculating Bhattacharyya coefficient: {str(e)}")
            raise

    def similarities(
        self, x: ComparableType, ys: Sequence[ComparableType]
    ) -> List[float]:
        """
        Calculate Bhattacharyya coefficients between one distribution and multiple others.

        Parameters
        ----------
        x : ComparableType
            Reference probability distribution
        ys : Sequence[ComparableType]
            Sequence of probability distributions to compare against the reference

        Returns
        -------
        List[float]
            List of Bhattacharyya coefficients between x and each element in ys

        Raises
        ------
        ValueError
            If any distributions have incompatible dimensions or are not normalized
        TypeError
            If any input types are not supported
        """
        try:
            # Convert reference distribution to numpy array
            if isinstance(x, dict):
                # For dictionary representations, we'll handle this in the loop
                p_dict = x
                p_array = None
            else:
                p_dict = None
                p_array = np.array(x, dtype=float)

                # Check if reference distribution is normalized
                if not np.isclose(np.sum(p_array), 1.0, rtol=1e-5):
                    raise ValueError(
                        f"Reference distribution is not normalized: sum = {np.sum(p_array)}"
                    )

            results = []
            for i, y in enumerate(ys):
                try:
                    if p_dict is not None and isinstance(y, dict):
                        # Dictionary case - handle in similarity method
                        sim = self.similarity(p_dict, y)
                    elif p_array is not None:
                        # Array case - optimize by reusing the converted reference
                        q = np.array(y, dtype=float)

                        # Check if distribution is normalized
                        if not np.isclose(np.sum(q), 1.0, rtol=1e-5):
                            raise ValueError(
                                f"Distribution at index {i} is not normalized: sum = {np.sum(q)}"
                            )

                        # Check dimensions
                        if p_array.shape != q.shape:
                            raise ValueError(
                                f"Distribution at index {i} has incompatible dimensions: {p_array.shape} != {q.shape}"
                            )

                        # Calculate Bhattacharyya coefficient
                        sim = float(np.sum(np.sqrt(p_array * q)))
                    else:
                        # Fall back to standard method
                        sim = self.similarity(x, y)

                    results.append(sim)
                except Exception as e:
                    logger.error(f"Error calculating similarity for item {i}: {str(e)}")
                    raise

            return results

        except Exception as e:
            logger.error(f"Error calculating multiple similarities: {str(e)}")
            raise

    def dissimilarity(self, x: ComparableType, y: ComparableType) -> float:
        """
        Calculate the Bhattacharyya distance between two probability distributions.

        The Bhattacharyya distance is defined as: -ln(BC(p,q))
        For normalized probability distributions, this is equivalent to: 1 - BC(p,q)

        Parameters
        ----------
        x : ComparableType
            First probability distribution
        y : ComparableType
            Second probability distribution

        Returns
        -------
        float
            Bhattacharyya-based dissimilarity between x and y (range [0,1])

        Raises
        ------
        ValueError
            If the distributions have incompatible dimensions or are not normalized
        TypeError
            If the input types are not supported
        """
        try:
            # Get the Bhattacharyya coefficient
            bc = self.similarity(x, y)

            # Convert to a dissimilarity measure in [0,1]
            # For probability distributions, 1-BC is a valid dissimilarity measure
            return 1.0 - bc

        except Exception as e:
            logger.error(f"Error calculating Bhattacharyya dissimilarity: {str(e)}")
            raise

    def check_bounded(self) -> bool:
        """
        Check if the similarity measure is bounded.

        The Bhattacharyya coefficient is always bounded between 0 and 1.

        Returns
        -------
        bool
            True, as the Bhattacharyya coefficient is bounded
        """
        return True
