import logging
import numpy as np
from typing import Union, List, Optional, Tuple, Literal
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.similarities.SimilarityBase import SimilarityBase

logger = logging.getLogger(__name__)

@ComponentBase.register_type(SimilarityBase, "BhattacharyyaCoefficientSimilarity")
class BhattacharyyaCoefficientSimilarity(SimilarityBase):
    """
    Measures the overlap of probability distributions using the Bhattacharyya coefficient.

    The Bhattacharyya coefficient is a measure of similarity between two probability
    distributions. It is particularly useful for comparing histograms or probability
    density functions. The coefficient ranges between 0 and 1, where 1 indicates
    identical distributions.

    Attributes:
        resource: Type of resource this component represents, defaults to SIMILARITY.
    """
    resource: Literal[str] = ResourceTypes.SIMILARITY.value

    def __init__(self):
        """
        Initializes the BhattacharyyaCoefficientSimilarity instance.
        """
        super().__init__()
        self._name = "BhattacharyyaCoefficientSimilarity"

    def similarity(
        self, 
        x: Union[Union[List[float], np.ndarray], Tuple[float, ...], str, callable], 
        y: Union[Union[List[float], np.ndarray], Tuple[float, ...], str, callable]
    ) -> float:
        """
        Calculates the similarity between two probability distributions using the
        Bhattacharyya coefficient.

        Args:
            x: The first probability distribution.
            y: The second probability distribution.

        Returns:
            float: The Bhattacharyya coefficient similarity score between x and y.

        Raises:
            ValueError: If the input distributions do not have the same length.
        """
        x = self._validate_distribution(x)
        y = self._validate_distribution(y)

        if len(x) != len(y):
            raise ValueError("Distributions must have the same length")

        # Calculate the Bhattacharyya coefficient
        sqrt_sum = np.sqrt(np.sum(np.multiply(x, y)))
        bc = sqrt_sum

        logger.debug(f"Bhattacharyya similarity calculated: {bc}")
        return bc

    def dissimilarity(
        self, 
        x: Union[Union[List[float], np.ndarray], Tuple[float, ...], str, callable], 
        y: Union[Union[List[float], np.ndarray], Tuple[float, ...], str, callable]
    ) -> float:
        """
        Calculates the dissimilarity between two probability distributions using the
        Bhattacharyya coefficient.

        Args:
            x: The first probability distribution.
            y: The second probability distribution.

        Returns:
            float: The Bhattacharyya coefficient dissimilarity score between x and y.
        """
        similarity = self.similarity(x, y)
        return 1.0 - similarity

    def similarities(
        self, 
        x: Union[Union[List[float], np.ndarray], Tuple[float, ...], str, callable], 
        ys: Union[
            List[Union[Union[List[float], np.ndarray], Tuple[float, ...], str, callable]], 
            Union[Union[List[float], np.ndarray], Tuple[float, ...], str, callable]
        ]
    ) -> Union[float, List[float]]:
        """
        Calculates similarity scores between a reference distribution and multiple
        distributions.

        Args:
            x: The reference distribution.
            ys: Either a single distribution or a list of distributions to compare.

        Returns:
            Union[float, List[float]]: Similarity scores between x and each element in ys.
        """
        if isinstance(ys, list):
            return [self.similarity(x, y) for y in ys]
        else:
            return self.similarity(x, ys)

    def dissimilarities(
        self, 
        x: Union[Union[List[float], np.ndarray], Tuple[float, ...], str, callable], 
        ys: Union[
            List[Union[Union[List[float], np.ndarray], Tuple[float, ...], str, callable]], 
            Union[Union[List[float], np.ndarray], Tuple[float, ...], str, callable]
        ]
    ) -> Union[float, List[float]]:
        """
        Calculates dissimilarity scores between a reference distribution and multiple
        distributions.

        Args:
            x: The reference distribution.
            ys: Either a single distribution or a list of distributions to compare.

        Returns:
            Union[float, List[float]]: Dissimilarity scores between x and each element in ys.
        """
        if isinstance(ys, list):
            return [self.dissimilarity(x, y) for y in ys]
        else:
            return self.dissimilarity(x, ys)

    def check_boundedness(
        self, 
        x: Union[Union[List[float], np.ndarray], Tuple[float, ...], str, callable], 
        y: Union[Union[List[float], np.ndarray], Tuple[float, ...], str, callable]
    ) -> bool:
        """
        Checks if the similarity measure is bounded.

        The Bhattacharyya coefficient is bounded between 0 and 1.

        Args:
            x: The first distribution (unused in this check).
            y: The second distribution (unused in this check).

        Returns:
            bool: True if the measure is bounded, False otherwise.
        """
        return True

    def check_reflexivity(
        self, 
        x: Union[Union[List[float], np.ndarray], Tuple[float, ...], str, callable]
    ) -> bool:
        """
        Checks if the similarity measure is reflexive.

        For any distribution x, similarity(x, x) should be 1.

        Args:
            x: The distribution to check reflexivity for.

        Returns:
            bool: True if the measure is reflexive, False otherwise.
        """
        return True

    def check_symmetry(
        self, 
        x: Union[Union[List[float], np.ndarray], Tuple[float, ...], str, callable], 
        y: Union[Union[List[float], np.ndarray], Tuple[float, ...], str, callable]
    ) -> bool:
        """
        Checks if the similarity measure is symmetric.

        The Bhattacharyya coefficient is symmetric, meaning similarity(x, y) = similarity(y, x).

        Args:
            x: The first distribution (unused in this check).
            y: The second distribution (unused in this check).

        Returns:
            bool: True if the measure is symmetric, False otherwise.
        """
        return True

    def check_identity(
        self, 
        x: Union[Union[List[float], np.ndarray], Tuple[float, ...], str, callable], 
        y: Union[Union[List[float], np.ndarray], Tuple[float, ...], str, callable]
    ) -> bool:
        """
        Checks if the similarity measure satisfies identity.

        For identical distributions x and y, similarity(x, y) should be 1.

        Args:
            x: The first distribution.
            y: The second distribution.

        Returns:
            bool: True if the measure satisfies identity, False otherwise.
        """
        return self.similarity(x, y) == 1.0

    def _validate_distribution(self, distribution: Union[List[float], np.ndarray, Tuple[float, ...], str, callable]) -> np.ndarray:
        """
        Validates and normalizes a probability distribution.

        Args:
            distribution: The distribution to validate and normalize.

        Returns:
            np.ndarray: The validated and normalized distribution as a numpy array.

        Raises:
            ValueError: If the distribution is invalid or cannot be normalized.
        """
        if isinstance(distribution, str) or callable(distribution):
            raise ValueError("Distribution must be provided as a list, array, or tuple of floats")

        if not isinstance(distribution, (list, np.ndarray, tuple)):
            raise ValueError("Invalid distribution type")

        dist_array = np.asarray(distribution)
        if np.any(np.isnan(dist_array)) or np.any(np.isinf(dist_array)) or np.any(dist_array < 0):
            raise ValueError("Distribution contains invalid values (NaN, Inf, or negative values)")

        sum_dist = np.sum(dist_array)
        if sum_dist == 0:
            raise ValueError("Distribution sum is zero and cannot be normalized")

        normalized = dist_array / sum_dist
        return normalized