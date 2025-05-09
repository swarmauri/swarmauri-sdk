from typing import Union, Sequence, Optional, Literal
import logging
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.similarities.SimilarityBase import SimilarityBase

logger = logging.getLogger(__name__)


@ComponentBase.register_model()
class CosineSimilarity(SimilarityBase):
    """
    Concrete implementation of the SimilarityBase class for Cosine Similarity measure.

    This class calculates the cosine similarity between vectors using the dot product
    and magnitudes of the vectors. The cosine similarity is a measure of similarity
    between two non-zero vectors of an inner product space that measures the cosine
    of the angle between them.

    The class provides implementations for similarity, dissimilarity, and related
    properties like boundedness, reflexivity, symmetry, and identity.
    """

    type: Literal["CosineSimilarity"] = "CosineSimilarity"
    resource: Optional[str] = "COSINE_SIMILARITY"

    def similarity(
        self, x: Union[Sequence[float], str], y: Union[Sequence[float], str]
    ) -> float:
        """
        Computes the cosine similarity between two vectors.

        The cosine similarity is defined as the dot product of the vectors divided
        by the product of their magnitudes. This implementation assumes non-zero
        vectors as per the constraints.

        Args:
            x: First vector
            y: Second vector

        Returns:
            float: Cosine similarity between x and y

        Raises:
            ValueError: If either vector is zero
        """
        logger.debug(f"Calculating cosine similarity between {x} and {y}")

        # Convert string representations to vectors if necessary
        if isinstance(x, str):
            x = eval(x)
        if isinstance(y, str):
            y = eval(y)

        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(x, y))

        # Calculate magnitudes
        mag_x = sum(a**2 for a in x) ** 0.5
        mag_y = sum(b**2 for b in y) ** 0.5

        # Check for zero vectors
        if mag_x == 0 or mag_y == 0:
            raise ValueError("Non-zero vectors only")

        # Compute cosine similarity
        sim = dot_product / (mag_x * mag_y)

        return sim

    def similarities(
        self,
        xs: Union[Sequence[Union[Sequence[float], str]], Sequence[float], str],
        ys: Union[Sequence[Union[Sequence[float], str]], Sequence[float], str],
    ) -> Union[float, Sequence[float]]:
        """
        Computes cosine similarities for multiple pairs of vectors.

        Args:
            xs: Sequence of first vectors to compare
            ys: Sequence of second vectors to compare

        Returns:
            Union[float, Sequence[float]]: Sequence of cosine similarities
        """
        logger.debug(f"Calculating cosine similarities between {xs} and {ys}")

        if isinstance(xs, Sequence) and isinstance(ys, Sequence):
            return [self.similarity(x, y) for x, y in zip(xs, ys)]
        else:
            return self.similarity(xs, ys)

    def dissimilarity(
        self, x: Union[Sequence[float], str], y: Union[Sequence[float], str]
    ) -> float:
        """
        Computes the dissimilarity as 1 minus the cosine similarity.

        Args:
            x: First vector
            y: Second vector

        Returns:
            float: Dissimilarity score
        """
        logger.debug(f"Calculating cosine dissimilarity between {x} and {y}")
        return 1.0 - self.similarity(x, y)

    def dissimilarities(
        self,
        xs: Union[Sequence[Union[Sequence[float], str]], Sequence[float], str],
        ys: Union[Sequence[Union[Sequence[float], str]], Sequence[float], str],
    ) -> Union[float, Sequence[float]]:
        """
        Computes cosine dissimilarities for multiple pairs of vectors.

        Args:
            xs: Sequence of first vectors to compare
            ys: Sequence of second vectors to compare

        Returns:
            Union[float, Sequence[float]]: Sequence of cosine dissimilarities
        """
        logger.debug(f"Calculating cosine dissimilarities between {xs} and {ys}")

        if isinstance(xs, Sequence) and isinstance(ys, Sequence):
            return [1.0 - s for s in self.similarities(xs, ys)]
        else:
            return 1.0 - self.similarity(xs, ys)

    def check_boundedness(self) -> bool:
        """
        Checks if the cosine similarity measure is bounded.

        Cosine similarity is bounded between -1 and 1, thus this method
        returns True to indicate boundedness.

        Returns:
            bool: True if the measure is bounded, False otherwise
        """
        logger.debug("Checking boundedness of cosine similarity")
        return True

    def check_reflexivity(self) -> bool:
        """
        Checks if the cosine similarity measure satisfies reflexivity.

        A measure is reflexive if s(x, x) = 1 for all x. Cosine similarity
        satisfies this property, thus returning True.

        Returns:
            bool: True if the measure is reflexive, False otherwise
        """
        logger.debug("Checking reflexivity of cosine similarity")
        return True

    def check_symmetry(self) -> bool:
        """
        Checks if the cosine similarity measure is symmetric.

        Cosine similarity is symmetric since s(x, y) = s(y, x), thus
        this method returns True.

        Returns:
            bool: True if the measure is symmetric, False otherwise
        """
        logger.debug("Checking symmetry of cosine similarity")
        return True

    def check_identity(self) -> bool:
        """
        Checks if the cosine similarity measure satisfies identity of discernibles.

        A measure satisfies identity if s(x, y) = 1 if and only if x = y.
        Cosine similarity does not satisfy this property because different vectors
        can have a similarity of 1, thus this method returns False.

        Returns:
            bool: False as cosine similarity does not satisfy identity
        """
        logger.debug("Checking identity of discernibles for cosine similarity")
        return False
