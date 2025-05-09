from typing import Union, Sequence, Tuple, Any
import logging
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.similarities.SimilarityBase import SimilarityBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "BhattacharyyaCoefficientSimilarity")
class BhattacharyyaCoefficientSimilarity(SimilarityBase):
    """
    Concrete implementation of the Bhattacharyya Coefficient Similarity measure.

    The Bhattacharyya coefficient is a measure of similarity between two probability
    distributions. It is particularly useful for comparing histograms or probability
    density functions.

    Inherits From:
        SimilarityBase: Base class for similarity measures

    Attributes:
        resource: Optional[str] = ResourceTypes.SIMILARITY.value
            Specifies the resource type for this component
    """
    resource: Optional[str] = ResourceTypes.SIMILARITY.value

    def similarity(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> float:
        """
        Computes the Bhattacharyya coefficient similarity between two distributions.

        The Bhattacharyya coefficient measures the similarity between two probability
        distributions. The coefficient ranges between 0 (complete dissimilarity)
        and 1 (complete similarity).

        Args:
            a: Union[Any, None]
                The first probability distribution
            b: Union[Any, None]
                The second probability distribution

        Returns:
            float:
                The Bhattacharyya coefficient similarity score

        Raises:
            ValueError:
                If the input distributions are invalid or not normalized
        """
        logger.info("Computing Bhattacharyya coefficient similarity")
        
        if a is None or b is None:
            return 0.0
            
        if not self._is_valid_distribution(a) or not self._is_valid_distribution(b):
            raise ValueError("Invalid or non-normalized distribution provided")
            
        bc = self._bhattacharyya_coefficient(a, b)
        logger.debug(f"Bhattacharyya coefficient: {bc}")
        return bc

    def similarities(
            self, 
            a: Union[Any, None], 
            b_list: Sequence[Union[Any, None]]
    ) -> Tuple[float, ...]:
        """
        Computes Bhattacharyya coefficient similarities for multiple distributions.

        Args:
            a: Union[Any, None]
                The reference distribution
            b_list: Sequence[Union[Any, None]]
                List of distributions to compare against

        Returns:
            Tuple[float, ...]:
                Tuple of Bhattacharyya coefficient similarity scores
        """
        logger.info("Computing multiple Bhattacharyya coefficient similarities")
        return tuple(self.similarity(a, b) for b in b_list)

    def dissimilarity(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> float:
        """
        Computes the Bhattacharyya coefficient dissimilarity between two distributions.

        The dissimilarity is calculated as 1 minus the similarity score.

        Args:
            a: Union[Any, None]
                The first probability distribution
            b: Union[Any, None]
                The second probability distribution

        Returns:
            float:
                The Bhattacharyya coefficient dissimilarity score
        """
        logger.info("Computing Bhattacharyya coefficient dissimilarity")
        return 1.0 - self.similarity(a, b)

    def dissimilarities(
            self, 
            a: Union[Any, None], 
            b_list: Sequence[Union[Any, None]]
    ) -> Tuple[float, ...]:
        """
        Computes Bhattacharyya coefficient dissimilarities for multiple distributions.

        Args:
            a: Union[Any, None]
                The reference distribution
            b_list: Sequence[Union[Any, None]]
                List of distributions to compare against

        Returns:
            Tuple[float, ...]:
                Tuple of Bhattacharyya coefficient dissimilarity scores
        """
        logger.info("Computing multiple Bhattacharyya coefficient dissimilarities")
        return tuple(self.dissimilarity(a, b) for b in b_list)

    def check_boundedness(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> bool:
        """
        Checks if the Bhattacharyya coefficient is a bounded measure.

        The Bhattacharyya coefficient is bounded between 0 and 1.

        Args:
            a: Union[Any, None]
                The first element to compare (unused in this implementation)
            b: Union[Any, None]
                The second element to compare (unused in this implementation)

        Returns:
            bool:
                True if the measure is bounded, False otherwise
        """
        logger.info("Checking if Bhattacharyya coefficient is bounded")
        return True

    def check_reflexivity(
            self, 
            a: Union[Any, None]
    ) -> bool:
        """
        Checks if the Bhattacharyya coefficient is reflexive.

        The Bhattacharyya coefficient is reflexive since s(x, x) = 1.

        Args:
            a: Union[Any, None]
                The element to check reflexivity for (unused in this implementation)

        Returns:
            bool:
                True if the measure is reflexive, False otherwise
        """
        logger.info("Checking reflexivity of Bhattacharyya coefficient")
        return True

    def check_symmetry(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> bool:
        """
        Checks if the Bhattacharyya coefficient is symmetric.

        The Bhattacharyya coefficient is symmetric since s(x, y) = s(y, x).

        Args:
            a: Union[Any, None]
                The first element to compare (unused in this implementation)
            b: Union[Any, None]
                The second element to compare (unused in this implementation)

        Returns:
            bool:
                True if the measure is symmetric, False otherwise
        """
        logger.info("Checking symmetry of Bhattacharyya coefficient")
        return True

    def check_identity(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> bool:
        """
        Checks if the Bhattacharyya coefficient satisfies identity.

        The Bhattacharyya coefficient satisfies identity since s(x, y) = 1 if and only if x = y.

        Args:
            a: Union[Any, None]
                The first element to compare (unused in this implementation)
            b: Union[Any, None]
                The second element to compare (unused in this implementation)

        Returns:
            bool:
                True if the measure satisfies identity, False otherwise
        """
        logger.info("Checking identity of Bhattacharyya coefficient")
        return True

    @staticmethod
    def _bhattacharyya_coefficient(
            p: Any, 
            q: Any
    ) -> float:
        """
        Computes the Bhattacharyya coefficient between two probability distributions.

        Args:
            p: Any
                First probability distribution
            q: Any
                Second probability distribution

        Returns:
            float:
                The Bhattacharyya coefficient value

        Raises:
            ValueError:
                If the distributions are not valid or not of the same length
        """
        if len(p) != len(q):
            raise ValueError("Distributions must be of the same length")
            
        bc = 0.0
        for p_i, q_i in zip(p, q):
            bc += (p_i * q_i) ** 0.5
        return bc

    @staticmethod
    def _is_valid_distribution(distribution: Any) -> bool:
        """
        Checks if a distribution is valid (non-negative and sums to 1).

        Args:
            distribution: Any
                The distribution to validate

        Returns:
            bool:
                True if the distribution is valid, False otherwise
        """
        if not all(x >= 0 for x in distribution):
            return False
        return abs(sum(distribution) - 1.0) < 1e-6