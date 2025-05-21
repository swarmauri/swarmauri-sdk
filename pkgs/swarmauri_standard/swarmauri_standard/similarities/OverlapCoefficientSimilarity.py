import logging
from collections.abc import Collection
from typing import Any, List, Literal, Sequence, Set, TypeVar

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.similarities.SimilarityBase import SimilarityBase
from swarmauri_core.similarities.ISimilarity import ComparableType

# Set up logger
logger = logging.getLogger(__name__)

T = TypeVar("T")


@ComponentBase.register_type(SimilarityBase, "OverlapCoefficientSimilarity")
class OverlapCoefficientSimilarity(SimilarityBase):
    """
    Overlap Coefficient Similarity implementation.

    The Overlap Coefficient measures the overlap between two sets.
    It is defined as the size of the intersection divided by the size of the smaller set.
    This makes it sensitive to complete inclusion, where one set is a subset of the other.

    Attributes
    ----------
    type : Literal["OverlapCoefficientSimilarity"]
        The type identifier for this similarity measure
    """

    type: Literal["OverlapCoefficientSimilarity"] = "OverlapCoefficientSimilarity"

    def _convert_to_set(self, x: Any) -> Set:
        """
        Convert input to a set if it's not already a set.

        Parameters
        ----------
        x : Any
            Input to convert to a set

        Returns
        -------
        Set
            The input converted to a set

        Raises
        ------
        TypeError
            If the input cannot be converted to a set
        """
        if isinstance(x, set):
            return x
        elif isinstance(x, Collection):
            return set(x)
        else:
            try:
                return set(x)
            except (TypeError, ValueError) as e:
                logger.error(f"Cannot convert input to set: {str(e)}")
                raise TypeError(f"Input must be convertible to a set: {str(e)}")

    def similarity(self, x: ComparableType, y: ComparableType) -> float:
        """
        Calculate the Overlap Coefficient similarity between two sets.

        The Overlap Coefficient is defined as |X ∩ Y| / min(|X|, |Y|).

        Parameters
        ----------
        x : ComparableType
            First set or collection
        y : ComparableType
            Second set or collection

        Returns
        -------
        float
            Overlap Coefficient similarity between x and y

        Raises
        ------
        ValueError
            If either set is empty
        TypeError
            If inputs cannot be converted to sets
        """
        try:
            set_x = self._convert_to_set(x)
            set_y = self._convert_to_set(y)

            # Check if sets are non-empty
            if not set_x or not set_y:
                logger.error("Sets must be non-empty for Overlap Coefficient")
                raise ValueError("Sets must be non-empty for Overlap Coefficient")

            # Calculate intersection
            intersection_size = len(set_x.intersection(set_y))

            # Calculate minimum size
            min_size = min(len(set_x), len(set_y))

            # Calculate overlap coefficient
            return intersection_size / min_size
        except Exception as e:
            logger.error(f"Error calculating Overlap Coefficient similarity: {str(e)}")
            raise

    def similarities(
        self, x: ComparableType, ys: Sequence[ComparableType]
    ) -> List[float]:
        """
        Calculate Overlap Coefficient similarities between one set and multiple other sets.

        Parameters
        ----------
        x : ComparableType
            Reference set or collection
        ys : Sequence[ComparableType]
            Sequence of sets or collections to compare against the reference

        Returns
        -------
        List[float]
            List of Overlap Coefficient similarity scores between x and each element in ys

        Raises
        ------
        ValueError
            If any set is empty
        TypeError
            If any input cannot be converted to a set
        """
        try:
            # Convert x to set once for efficiency
            set_x = self._convert_to_set(x)

            if not set_x:
                logger.error("Reference set must be non-empty for Overlap Coefficient")
                raise ValueError(
                    "Reference set must be non-empty for Overlap Coefficient"
                )

            len_x = len(set_x)
            results = []

            for y in ys:
                set_y = self._convert_to_set(y)

                if not set_y:
                    logger.error(
                        "Comparison set must be non-empty for Overlap Coefficient"
                    )
                    raise ValueError(
                        "Comparison set must be non-empty for Overlap Coefficient"
                    )

                # Calculate intersection
                intersection_size = len(set_x.intersection(set_y))

                # Calculate minimum size
                min_size = min(len_x, len(set_y))

                # Calculate overlap coefficient
                results.append(intersection_size / min_size)

            return results
        except Exception as e:
            logger.error(
                f"Error calculating multiple Overlap Coefficient similarities: {str(e)}"
            )
            raise

    def dissimilarity(self, x: ComparableType, y: ComparableType) -> float:
        """
        Calculate the Overlap Coefficient dissimilarity between two sets.

        Defined as 1 - similarity(x, y).

        Parameters
        ----------
        x : ComparableType
            First set or collection
        y : ComparableType
            Second set or collection

        Returns
        -------
        float
            Overlap Coefficient dissimilarity between x and y

        Raises
        ------
        ValueError
            If either set is empty
        TypeError
            If inputs cannot be converted to sets
        """
        return 1.0 - self.similarity(x, y)

    def check_bounded(self) -> bool:
        """
        Check if the Overlap Coefficient similarity measure is bounded.

        The Overlap Coefficient is bounded in the range [0, 1].

        Returns
        -------
        bool
            True, as the Overlap Coefficient is bounded
        """
        return True

    def check_reflexivity(self, x: ComparableType) -> bool:
        """
        Check if the Overlap Coefficient similarity measure is reflexive: s(x,x) = 1.

        Parameters
        ----------
        x : ComparableType
            Object to check reflexivity with

        Returns
        -------
        bool
            True, as the Overlap Coefficient is reflexive

        Raises
        ------
        ValueError
            If the set is empty
        TypeError
            If the input cannot be converted to a set
        """
        try:
            set_x = self._convert_to_set(x)

            if not set_x:
                logger.error("Set must be non-empty for Overlap Coefficient")
                raise ValueError("Set must be non-empty for Overlap Coefficient")

            # For any non-empty set, the overlap with itself is the set itself,
            # and the minimum size is the size of the set, so the result is 1.0
            return True
        except Exception as e:
            logger.error(f"Error checking reflexivity: {str(e)}")
            raise

    def check_symmetry(self, x: ComparableType, y: ComparableType) -> bool:
        """
        Check if the Overlap Coefficient similarity measure is symmetric: s(x,y) = s(y,x).

        Parameters
        ----------
        x : ComparableType
            First set or collection
        y : ComparableType
            Second set or collection

        Returns
        -------
        bool
            True, as the Overlap Coefficient is symmetric

        Raises
        ------
        ValueError
            If either set is empty
        TypeError
            If inputs cannot be converted to sets
        """
        # The Overlap Coefficient is symmetric by definition:
        # |X ∩ Y| / min(|X|, |Y|) = |Y ∩ X| / min(|Y|, |X|)
        return True

    def check_identity_of_discernibles(
        self, x: ComparableType, y: ComparableType
    ) -> bool:
        """
        Check if the Overlap Coefficient satisfies the identity of discernibles: s(x,y) = 1 ⟺ x = y.

        Note: The Overlap Coefficient does not strictly satisfy this property.
        It returns 1 when one set is a subset of the other, not only when they are identical.

        Parameters
        ----------
        x : ComparableType
            First set or collection
        y : ComparableType
            Second set or collection

        Returns
        -------
        bool
            False if x ≠ y but s(x,y) = 1, True otherwise

        Raises
        ------
        ValueError
            If either set is empty
        TypeError
            If inputs cannot be converted to sets
        """
        try:
            set_x = self._convert_to_set(x)
            set_y = self._convert_to_set(y)

            if not set_x or not set_y:
                logger.error("Sets must be non-empty for Overlap Coefficient")
                raise ValueError("Sets must be non-empty for Overlap Coefficient")

            similarity_value = self.similarity(set_x, set_y)

            # If similarity is 1, check if sets are identical
            if abs(similarity_value - 1.0) < 1e-10:
                # The Overlap Coefficient can be 1 even if the sets are not identical
                # It will be 1 if one set is a subset of the other
                return set_x == set_y

            # If similarity is not 1, identity of discernibles is satisfied
            return True
        except Exception as e:
            logger.error(f"Error checking identity of discernibles: {str(e)}")
            raise
