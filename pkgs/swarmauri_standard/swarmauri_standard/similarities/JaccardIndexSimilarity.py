import logging
from typing import List, Literal, Sequence, Set

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.similarities.SimilarityBase import SimilarityBase

# Set up logger
logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "JaccardIndexSimilarity")
class JaccardIndexSimilarity(SimilarityBase):
    """
    Jaccard Index similarity measure for sets.

    The Jaccard Index is defined as the size of the intersection divided by the size of the union
    of the sample sets. It ranges from 0 (no similarity) to 1 (identical sets).

    This similarity measure is symmetric and bounded in the range [0,1].

    Attributes
    ----------
    type : Literal["JaccardIndexSimilarity"]
        Type identifier for this similarity measure
    """

    type: Literal["JaccardIndexSimilarity"] = "JaccardIndexSimilarity"

    def similarity(self, x: Set, y: Set) -> float:
        """
        Calculate the Jaccard Index similarity between two sets.

        Parameters
        ----------
        x : Set
            First set to compare
        y : Set
            Second set to compare

        Returns
        -------
        float
            Jaccard Index similarity score between x and y

        Raises
        ------
        TypeError
            If inputs are not sets
        ValueError
            If either set is empty and the other is not
        """
        # Validate input types
        if not isinstance(x, set) or not isinstance(y, set):
            logger.error("JaccardIndexSimilarity requires set inputs")
            raise TypeError("Inputs must be sets")

        # Handle edge cases
        if len(x) == 0 and len(y) == 0:
            logger.debug("Both sets are empty, returning similarity of 1.0")
            return 1.0

        if len(x) == 0 or len(y) == 0:
            logger.debug("One set is empty, returning similarity of 0.0")
            return 0.0

        # Calculate intersection and union
        intersection_size = len(x.intersection(y))
        union_size = len(x.union(y))

        # Calculate Jaccard Index
        jaccard_index = intersection_size / union_size
        logger.debug(f"Calculated Jaccard Index: {jaccard_index}")

        return jaccard_index

    def similarities(self, x: Set, ys: Sequence[Set]) -> List[float]:
        """
        Calculate Jaccard Index similarities between one set and multiple other sets.

        Parameters
        ----------
        x : Set
            Reference set
        ys : Sequence[Set]
            Sequence of sets to compare against the reference

        Returns
        -------
        List[float]
            List of Jaccard Index similarity scores between x and each element in ys

        Raises
        ------
        TypeError
            If any input is not a set
        """
        # Validate input types
        if not isinstance(x, set):
            logger.error("Reference input must be a set")
            raise TypeError("Reference input must be a set")

        results = []

        for i, y in enumerate(ys):
            if not isinstance(y, set):
                logger.error(f"Input at index {i} is not a set")
                raise TypeError("All inputs in sequence must be sets")

            results.append(self.similarity(x, y))

        return results

    def dissimilarity(self, x: Set, y: Set) -> float:
        """
        Calculate the Jaccard dissimilarity between two sets.

        Jaccard dissimilarity is defined as 1 - Jaccard similarity.

        Parameters
        ----------
        x : Set
            First set to compare
        y : Set
            Second set to compare

        Returns
        -------
        float
            Jaccard dissimilarity score between x and y

        Raises
        ------
        TypeError
            If inputs are not sets
        """
        # Since Jaccard Index is bounded between 0 and 1,
        # we can define dissimilarity as 1 - similarity
        return 1.0 - self.similarity(x, y)

    def check_bounded(self) -> bool:
        """
        Check if the similarity measure is bounded.

        The Jaccard Index is always bounded in the range [0,1].

        Returns
        -------
        bool
            True, as the Jaccard Index is bounded
        """
        return True

    def check_symmetry(self, x: Set, y: Set) -> bool:
        """
        Check if the similarity measure is symmetric.

        The Jaccard Index is symmetric by definition: J(A,B) = J(B,A).

        Parameters
        ----------
        x : Set
            First set to compare
        y : Set
            Second set to compare

        Returns
        -------
        bool
            True, as the Jaccard Index is symmetric

        Raises
        ------
        TypeError
            If inputs are not sets
        """
        # Validate input types
        if not isinstance(x, set) or not isinstance(y, set):
            logger.error("Inputs must be sets")
            raise TypeError("Inputs must be sets")

        # The Jaccard Index is symmetric by definition, but we can verify
        similarity_xy = self.similarity(x, y)
        similarity_yx = self.similarity(y, x)

        return abs(similarity_xy - similarity_yx) < 1e-10
