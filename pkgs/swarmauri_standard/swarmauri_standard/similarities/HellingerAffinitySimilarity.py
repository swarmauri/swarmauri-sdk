import logging
import numpy as np
from typing import Union, Sequence, Tuple, Any, Optional
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.similarities.SimilarityBase import SimilarityBase

logger = logging.getLogger(__name__)


@ComponentBase.register_model()
class HellingerAffinitySimilarity(SimilarityBase):
    """
    Computes the Hellinger affinity similarity between two discrete probability distributions.

    The Hellinger affinity is a measure of similarity between two probability distributions.
    It is based on the square root of the sum of the product of the square roots of the
    corresponding probabilities. This measure is particularly useful for comparing
    distributions and is always non-negative.

    Inherits From:
        SimilarityBase: Base class for implementing similarity measures

    Attributes:
        resource: Optional[str] = Field(default=ResourceTypes.SIMILARITY.value)
            Specifies the resource type for this component
    """
    resource: Optional[str] = ResourceTypes.SIMILARITY.value

    def __init__(self) -> None:
        """
        Initializes the HellingerAffinitySimilarity class.
        """
        super().__init__()
        logger.debug("Initialized HellingerAffinitySimilarity")

    def similarity(
            self,
            a: Union[Any, None],
            b: Union[Any, None]
    ) -> float:
        """
        Computes the Hellinger affinity similarity between two probability distributions.

        Args:
            a: Union[Any, None]
                The first probability distribution
            b: Union[Any, None]
                The second probability distribution

        Returns:
            float:
                The similarity score between the two distributions

        Raises:
            ValueError:
                If the input distributions are invalid (not probability distributions)
        """
        if a is None and b is None:
            return 1.0
        if a is None or b is None:
            return 0.0

        if not self._is_valid_probability_distribution(a):
            raise ValueError("Invalid probability distribution a")
        if not self._is_valid_probability_distribution(b):
            raise ValueError("Invalid probability distribution b")

        sqrt_a = np.sqrt(a)
        sqrt_b = np.sqrt(b)
        similarity_score = np.sqrt(np.sum(sqrt_a * sqrt_b))
        return similarity_score

    def similarities(
            self,
            a: Union[Any, None],
            b_list: Sequence[Union[Any, None]]
    ) -> Tuple[float, ...]:
        """
        Computes the Hellinger affinity similarity scores between one distribution
        and a list of distributions.

        Args:
            a: Union[Any, None]
                The distribution to compare against multiple distributions
            b_list: Sequence[Union[Any, None]]
                The list of distributions to compare against

        Returns:
            Tuple[float, ...]:
                A tuple of similarity scores

        Raises:
            ValueError:
                If any input distribution is invalid
        """
        if a is None:
            return tuple(0.0 for _ in b_list)

        if not self._is_valid_probability_distribution(a):
            raise ValueError("Invalid probability distribution a")

        scores = []
        for b in b_list:
            if b is None:
                scores.append(0.0)
                continue
            if not self._is_valid_probability_distribution(b):
                raise ValueError("Invalid probability distribution in b_list")
            scores.append(self.similarity(a, b))
        return tuple(scores)

    def dissimilarity(
            self,
            a: Union[Any, None],
            b: Union[Any, None]
    ) -> float:
        """
        Computes the dissimilarity score based on the Hellinger affinity similarity.

        Args:
            a: Union[Any, None]
                The first distribution
            b: Union[Any, None]
                The second distribution

        Returns:
            float:
                The dissimilarity score between the two distributions
        """
        return 1.0 - self.similarity(a, b)

    def dissimilarities(
            self,
            a: Union[Any, None],
            b_list: Sequence[Union[Any, None]]
    ) -> Tuple[float, ...]:
        """
        Computes the dissimilarity scores between one distribution and a list of distributions.

        Args:
            a: Union[Any, None]
                The distribution to compare against multiple distributions
            b_list: Sequence[Union[Any, None]]
                The list of distributions to compare against

        Returns:
            Tuple[float, ...]:
                A tuple of dissimilarity scores
        """
        return tuple(1.0 - score for score in self.similarities(a, b_list))

    def check_boundedness(
            self,
            a: Union[Any, None],
            b: Union[Any, None]
    ) -> bool:
        """
        Checks if the similarity measure is bounded.

        The Hellinger affinity is always bounded between 0 and 1.

        Args:
            a: Union[Any, None]
                The first distribution
            b: Union[Any, None]
                The second distribution

        Returns:
            bool:
                True if the similarity measure is bounded, False otherwise
        """
        return True

    def check_reflexivity(
            self,
            a: Union[Any, None]
    ) -> bool:
        """
        Checks if the similarity measure is reflexive.

        For the Hellinger affinity, s(x, x) = 1, so it is reflexive.

        Args:
            a: Union[Any, None]
                The distribution to check reflexivity for

        Returns:
            bool:
                True if the similarity measure is reflexive, False otherwise
        """
        return True

    def check_symmetry(
            self,
            a: Union[Any, None],
            b: Union[Any, None]
    ) -> bool:
        """
        Checks if the similarity measure is symmetric.

        The Hellinger affinity is symmetric, i.e., s(x, y) = s(y, x).

        Args:
            a: Union[Any, None]
                The first distribution
            b: Union[Any, None]
                The second distribution

        Returns:
            bool:
                True if the similarity measure is symmetric, False otherwise
        """
        return True

    def check_identity(
            self,
            a: Union[Any, None],
            b: Union[Any, None]
    ) -> bool:
        """
        Checks if the similarity measure satisfies identity.

        The Hellinger affinity does not necessarily satisfy identity since
        s(x, y) can be 1 even if x ≠ y.

        Args:
            a: Union[Any, None]
                The first distribution
            b: Union[Any, None]
                The second distribution

        Returns:
            bool:
                True if the similarity measure satisfies identity, False otherwise
        """
        return False

    def _is_valid_probability_distribution(self, distribution: Any) -> bool:
        """
        Checks if the given distribution is a valid probability distribution.

        A valid probability distribution must have non-negative values and
        sum to 1.

        Args:
            distribution: Any
                The distribution to validate

        Returns:
            bool:
                True if the distribution is valid, False otherwise
        """
        if not isinstance(distribution, np.ndarray) or distribution.ndim != 1:
            return False

        if np.any(distribution < 0):
            return False

        return np.isclose(np.sum(distribution), 1.0, atol=1e-8)