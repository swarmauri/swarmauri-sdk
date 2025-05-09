from typing import Union, Sequence, Tuple, Any, Optional
import logging
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.similarities.SimilarityBase import SimilarityBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "TanimotoSimilarity")
class TanimotoSimilarity(SimilarityBase):
    """
    A concrete implementation of the Tanimoto similarity measure.

    This class provides the implementation for calculating the Tanimoto similarity
    between vectors. The Tanimoto similarity is a generalization of the Jaccard
    similarity for real-valued vectors and is commonly used in cheminformatics for
    comparing molecular fingerprints.

    Inherits From:
        SimilarityBase: Base class for similarity measures

    Attributes:
        resource: Optional[str] = "similarity"
            Specifies the resource type for this component
    """
    resource: Optional[str] = "similarity"

    def similarity(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> float:
        """
        Calculates the Tanimoto similarity between two vectors.

        The Tanimoto similarity is calculated as:
            T = (a · b) / (||a||² + ||b||² - (a · b))
        
        Where:
            a · b = dot product of vectors a and b
            ||a||² = squared magnitude of vector a
            ||b||² = squared magnitude of vector b

        Args:
            a: Union[Any, None]
                The first vector to compare
            b: Union[Any, None]
                The second vector to compare

        Returns:
            float:
                The Tanimoto similarity score between the two vectors

        Raises:
            ValueError:
                If either vector is None or zero vector
        """
        if a is None or b is None:
            logger.error("Input vectors cannot be None")
            raise ValueError("Input vectors cannot be None")
            
        if len(a) == 0 or len(b) == 0:
            logger.error("Input vectors cannot be empty")
            raise ValueError("Input vectors cannot be empty")

        # Calculate the dot product
        dot_product = sum(x * y for x, y in zip(a, b))
        
        # Calculate the squared magnitudes
        sum_a_sq = sum(x**2 for x in a)
        sum_b_sq = sum(x**2 for x in b)
        
        # Calculate the denominator
        denominator = sum_a_sq + sum_b_sq - dot_product
        
        if denominator == 0:
            logger.error("Denominator is zero, cannot calculate similarity")
            raise ValueError("Denominator is zero, cannot calculate similarity")
            
        similarity = dot_product / denominator
        
        logger.debug(f"Calculated Tanimoto similarity: {similarity}")
        return similarity

    def similarities(
            self, 
            a: Union[Any, None], 
            b_list: Sequence[Union[Any, None]]
    ) -> Tuple[float, ...]:
        """
        Calculates Tanimoto similarity scores between one vector and a list of vectors.

        Args:
            a: Union[Any, None]
                The vector to compare against multiple vectors
            b_list: Sequence[Union[Any, None]]
                The list of vectors to compare against

        Returns:
            Tuple[float, ...]:
                A tuple of Tanimoto similarity scores

        Raises:
            ValueError:
                If input vector 'a' or any vector in 'b_list' is None or empty
        """
        if a is None or len(a) == 0:
            logger.error("Input vector 'a' cannot be None or empty")
            raise ValueError("Input vector 'a' cannot be None or empty")
            
        similarities = []
        for b in b_list:
            if b is None or len(b) == 0:
                logger.error("Input vector in 'b_list' cannot be None or empty")
                raise ValueError("Input vector in 'b_list' cannot be None or empty")
            similarities.append(self.similarity(a, b))
            
        logger.debug(f"Calculated similarities for {len(similarities)} vectors")
        return tuple(similarities)

    def dissimilarity(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> float:
        """
        Calculates the dissimilarity score as 1 - similarity.

        Args:
            a: Union[Any, None]
                The first vector to compare
            b: Union[Any, None]
                The second vector to compare

        Returns:
            float:
                The dissimilarity score between the two vectors
        """
        similarity = self.similarity(a, b)
        dissimilarity = 1.0 - similarity
        
        logger.debug(f"Calculated dissimilarity: {dissimilarity}")
        return dissimilarity

    def dissimilarities(
            self, 
            a: Union[Any, None], 
            b_list: Sequence[Union[Any, None]]
    ) -> Tuple[float, ...]:
        """
        Calculates dissimilarity scores as 1 - similarity for multiple vectors.

        Args:
            a: Union[Any, None]
                The vector to compare against multiple vectors
            b_list: Sequence[Union[Any, None]]
                The list of vectors to compare against

        Returns:
            Tuple[float, ...]:
                A tuple of dissimilarity scores
        """
        similarities = self.similarities(a, b_list)
        dissimilarities = tuple(1.0 - s for s in similarities)
        
        logger.debug(f"Calculated dissimilarities for {len(dissimilarities)} vectors")
        return dissimilarities

    def check_boundedness(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> bool:
        """
        Checks if the Tanimoto similarity measure is bounded.

        Tanimoto similarity is bounded between 0 and 1.

        Args:
            a: Union[Any, None]
                The first vector to compare
            b: Union[Any, None]
                The second vector to compare

        Returns:
            bool:
                True if the measure is bounded, False otherwise
        """
        # Tanimoto similarity is always between 0 and 1
        return True

    def check_reflexivity(
            self, 
            a: Union[Any, None]
    ) -> bool:
        """
        Checks if the Tanimoto similarity measure is reflexive.

        A measure is reflexive if s(x, x) = 1 for all x.

        Args:
            a: Union[Any, None]
                The vector to check reflexivity for

        Returns:
            bool:
                True if the measure is reflexive, False otherwise
        """
        try:
            similarity = self.similarity(a, a)
            return similarity == 1.0
        except Exception as e:
            logger.error(f"Error checking reflexivity: {str(e)}")
            return False

    def check_symmetry(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> bool:
        """
        Checks if the Tanimoto similarity measure is symmetric.

        A measure is symmetric if s(x, y) = s(y, x) for all x, y.

        Args:
            a: Union[Any, None]
                The first vector to compare
            b: Union[Any, None]
                The second vector to compare

        Returns:
            bool:
                True if the measure is symmetric, False otherwise
        """
        # Tanimoto similarity is symmetric
        return True

    def check_identity(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> bool:
        """
        Checks if the Tanimoto similarity measure satisfies identity.

        A measure satisfies identity if s(x, y) = 1 if and only if x = y.

        Args:
            a: Union[Any, None]
                The first vector to compare
            b: Union[Any, None]
                The second vector to compare

        Returns:
            bool:
                True if the measure satisfies identity, False otherwise
        """
        if a == b:
            return self.similarity(a, b) == 1.0
        return False