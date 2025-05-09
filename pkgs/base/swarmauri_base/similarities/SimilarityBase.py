from abc import ABC, abstractmethod
from typing import Union, Sequence, Tuple, Any, Optional
import logging
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.similarities.ISimilarity import ISimilarity

logger = logging.getLogger(__name__)


@ComponentBase.register_model()
class SimilarityBase(ISimilarity, ComponentBase):
    """
    Base class for implementing similarity measures.

    This class provides a foundation for directional or feature-based similarity
    implementation. It implements bounds, reflexivity and optional symmetry for
    similarity scoring. All methods raise NotImplementedError and must be
    implemented by concrete subclasses.

    Inherits From:
        ISimilarity: Interface for similarity measures
        ComponentBase: Base class for components

    Attributes:
        resource: Optional[str] = Field(default=ResourceTypes.SIMILARITY.value)
            Specifies the resource type for this component
    """
    resource: Optional[str] = ResourceTypes.SIMILARITY.value

    def similarity(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> float:
        """
        Calculates the similarity score between two elements.

        This method must be implemented by subclasses to provide the actual
        similarity calculation logic.

        Args:
            a: Union[Any, None]
                The first element to compare
            b: Union[Any, None]
                The second element to compare

        Returns:
            float:
                The similarity score between the two elements

        Raises:
            NotImplementedError:
                If the method is not implemented by the subclass
        """
        logger.error("similarity method not implemented")
        raise NotImplementedError("similarity method must be implemented")

    def similarities(
            self, 
            a: Union[Any, None], 
            b_list: Sequence[Union[Any, None]]
    ) -> Tuple[float, ...]:
        """
        Calculates similarity scores between one element and a list of elements.

        This method must be implemented by subclasses to provide the actual
        similarity calculation logic for multiple elements.

        Args:
            a: Union[Any, None]
                The element to compare against multiple elements
            b_list: Sequence[Union[Any, None]]
                The list of elements to compare against

        Returns:
            Tuple[float, ...]:
                A tuple of similarity scores

        Raises:
            NotImplementedError:
                If the method is not implemented by the subclass
        """
        logger.error("similarities method not implemented")
        raise NotImplementedError("similarities method must be implemented")

    def dissimilarity(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> float:
        """
        Calculates the dissimilarity score between two elements.

        This method must be implemented by subclasses to provide the actual
        dissimilarity calculation logic.

        Args:
            a: Union[Any, None]
                The first element to compare
            b: Union[Any, None]
                The second element to compare

        Returns:
            float:
                The dissimilarity score between the two elements

        Raises:
            NotImplementedError:
                If the method is not implemented by the subclass
        """
        logger.error("dissimilarity method not implemented")
        raise NotImplementedError("dissimilarity method must be implemented")

    def dissimilarities(
            self, 
            a: Union[Any, None], 
            b_list: Sequence[Union[Any, None]]
    ) -> Tuple[float, ...]:
        """
        Calculates dissimilarity scores between one element and a list of elements.

        This method must be implemented by subclasses to provide the actual
        dissimilarity calculation logic for multiple elements.

        Args:
            a: Union[Any, None]
                The element to compare against multiple elements
            b_list: Sequence[Union[Any, None]]
                The list of elements to compare against

        Returns:
            Tuple[float, ...]:
                A tuple of dissimilarity scores

        Raises:
            NotImplementedError:
                If the method is not implemented by the subclass
        """
        logger.error("dissimilarities method not implemented")
        raise NotImplementedError("dissimilarities method must be implemented")

    def check_boundedness(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> bool:
        """
        Checks if the similarity measure is bounded.

        This method must be implemented by subclasses to provide the actual
        boundedness check logic.

        Args:
            a: Union[Any, None]
                The first element to compare
            b: Union[Any, None]
                The second element to compare

        Returns:
            bool:
                True if the similarity measure is bounded, False otherwise

        Raises:
            NotImplementedError:
                If the method is not implemented by the subclass
        """
        logger.error("check_boundedness method not implemented")
        raise NotImplementedError("check_boundedness method must be implemented")

    def check_reflexivity(
            self, 
            a: Union[Any, None]
    ) -> bool:
        """
        Checks if the similarity measure is reflexive, i.e., s(x, x) = 1.

        This method must be implemented by subclasses to provide the actual
        reflexivity check logic.

        Args:
            a: Union[Any, None]
                The element to check reflexivity for

        Returns:
            bool:
                True if the similarity measure is reflexive, False otherwise

        Raises:
            NotImplementedError:
                If the method is not implemented by the subclass
        """
        logger.error("check_reflexivity method not implemented")
        raise NotImplementedError("check_reflexivity method must be implemented")

    def check_symmetry(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> bool:
        """
        Checks if the similarity measure is symmetric, i.e., s(x, y) = s(y, x).

        This method must be implemented by subclasses to provide the actual
        symmetry check logic.

        Args:
            a: Union[Any, None]
                The first element to compare
            b: Union[Any, None]
                The second element to compare

        Returns:
            bool:
                True if the similarity measure is symmetric, False otherwise

        Raises:
            NotImplementedError:
                If the method is not implemented by the subclass
        """
        logger.error("check_symmetry method not implemented")
        raise NotImplementedError("check_symmetry method must be implemented")

    def check_identity(
            self, 
            a: Union[Any, None], 
            b: Union[Any, None]
    ) -> bool:
        """
        Checks if the similarity measure satisfies identity, i.e., s(x, y) = 1
        if and only if x = y.

        This method must be implemented by subclasses to provide the actual
        identity check logic.

        Args:
            a: Union[Any, None]
                The first element to compare
            b: Union[Any, None]
                The second element to compare

        Returns:
            bool:
                True if the similarity measure satisfies identity, False otherwise

        Raises:
            NotImplementedError:
                If the method is not implemented by the subclass
        """
        logger.error("check_identity method not implemented")
        raise NotImplementedError("check_identity method must be implemented")