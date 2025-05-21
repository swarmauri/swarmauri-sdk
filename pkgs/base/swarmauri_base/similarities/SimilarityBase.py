import logging
from typing import List, Optional, Sequence

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.similarities.ISimilarity import ComparableType, ISimilarity

# Set up logger
logger = logging.getLogger(__name__)


@ComponentBase.register_model()
class SimilarityBase(ISimilarity, ComponentBase):
    """
    Base class for directional or feature-based similarity measures.

    This abstract base class implements the foundation for similarity measures,
    providing common functionality for bounds, reflexivity, and optional symmetry.
    It serves as a starting point for implementing concrete similarity metrics.

    Attributes
    ----------
    resource : str
        Resource type identifier
    """

    resource: Optional[str] = ResourceTypes.SIMILARITY.value

    def similarity(self, x: ComparableType, y: ComparableType) -> float:
        """
        Calculate the similarity between two objects.

        Parameters
        ----------
        x : ComparableType
            First object to compare
        y : ComparableType
            Second object to compare

        Returns
        -------
        float
            Similarity score between x and y

        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses
        ValueError
            If the objects are incomparable or have incompatible dimensions
        TypeError
            If the input types are not supported
        """
        raise NotImplementedError(
            "The similarity method must be implemented by subclasses"
        )

    def similarities(
        self, x: ComparableType, ys: Sequence[ComparableType]
    ) -> List[float]:
        """
        Calculate similarities between one object and multiple other objects.

        Parameters
        ----------
        x : ComparableType
            Reference object
        ys : Sequence[ComparableType]
            Sequence of objects to compare against the reference

        Returns
        -------
        List[float]
            List of similarity scores between x and each element in ys

        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses
        ValueError
            If any objects are incomparable or have incompatible dimensions
        TypeError
            If any input types are not supported
        """
        # Default implementation can be overridden for efficiency
        try:
            return [self.similarity(x, y) for y in ys]
        except Exception as e:
            logger.error(f"Error calculating similarities: {str(e)}")
            raise

    def dissimilarity(self, x: ComparableType, y: ComparableType) -> float:
        """
        Calculate the dissimilarity between two objects.

        Parameters
        ----------
        x : ComparableType
            First object to compare
        y : ComparableType
            Second object to compare

        Returns
        -------
        float
            Dissimilarity score between x and y

        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses
        ValueError
            If the objects are incomparable or have incompatible dimensions
        TypeError
            If the input types are not supported
        """
        # Default implementation based on similarity
        # Subclasses may override for direct dissimilarity calculation
        if self.check_bounded():
            try:
                return 1.0 - self.similarity(x, y)
            except Exception as e:
                logger.error(f"Error calculating dissimilarity: {str(e)}")
                raise
        else:
            raise NotImplementedError(
                "Dissimilarity for unbounded similarity measures must be implemented by subclasses"
            )

    def dissimilarities(
        self, x: ComparableType, ys: Sequence[ComparableType]
    ) -> List[float]:
        """
        Calculate dissimilarities between one object and multiple other objects.

        Parameters
        ----------
        x : ComparableType
            Reference object
        ys : Sequence[ComparableType]
            Sequence of objects to compare against the reference

        Returns
        -------
        List[float]
            List of dissimilarity scores between x and each element in ys

        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses
        ValueError
            If any objects are incomparable or have incompatible dimensions
        TypeError
            If any input types are not supported
        """
        # Default implementation can be overridden for efficiency
        try:
            return [self.dissimilarity(x, y) for y in ys]
        except Exception as e:
            logger.error(f"Error calculating dissimilarities: {str(e)}")
            raise

    def check_bounded(self) -> bool:
        """
        Check if the similarity measure is bounded.

        A bounded similarity measure has values within a fixed range,
        typically [0,1] for similarities.

        Returns
        -------
        bool
            True if the similarity measure is bounded, False otherwise
        """
        raise NotImplementedError(
            "The check_bounded method must be implemented by subclasses"
        )

    def check_reflexivity(self, x: ComparableType) -> bool:
        """
        Check if the similarity measure is reflexive: s(x,x) = 1.

        Parameters
        ----------
        x : ComparableType
            Object to check reflexivity with

        Returns
        -------
        bool
            True if s(x,x) = 1, False otherwise

        Raises
        ------
        TypeError
            If the input type is not supported
        """
        try:
            # A similarity measure is reflexive if s(x,x) = 1
            similarity_value = self.similarity(x, x)
            # Use approximate equality to handle floating-point precision issues
            return abs(similarity_value - 1.0) < 1e-10
        except Exception as e:
            logger.error(f"Error checking reflexivity: {str(e)}")
            raise

    def check_symmetry(self, x: ComparableType, y: ComparableType) -> bool:
        """
        Check if the similarity measure is symmetric: s(x,y) = s(y,x).

        Parameters
        ----------
        x : ComparableType
            First object to compare
        y : ComparableType
            Second object to compare

        Returns
        -------
        bool
            True if s(x,y) = s(y,x), False otherwise

        Raises
        ------
        ValueError
            If the objects are incomparable or have incompatible dimensions
        TypeError
            If the input types are not supported
        """
        try:
            # A similarity measure is symmetric if s(x,y) = s(y,x)
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
        Check if the similarity measure satisfies the identity of discernibles: s(x,y) = 1 ⟺ x = y.

        Parameters
        ----------
        x : ComparableType
            First object to compare
        y : ComparableType
            Second object to compare

        Returns
        -------
        bool
            True if the identity of discernibles property holds, False otherwise

        Raises
        ------
        ValueError
            If the objects are incomparable or have incompatible dimensions
        TypeError
            If the input types are not supported
        """
        try:
            similarity_value = self.similarity(x, y)
            # If x and y are identical (by value, not necessarily by reference)
            if str(x) == str(y):  # Simple string comparison as a basic equality check
                # Then the similarity should be 1
                return abs(similarity_value - 1.0) < 1e-10
            else:
                # If x and y are different, the similarity should be less than 1
                return similarity_value < 1.0 - 1e-10
        except Exception as e:
            logger.error(f"Error checking identity of discernibles: {str(e)}")
            raise
