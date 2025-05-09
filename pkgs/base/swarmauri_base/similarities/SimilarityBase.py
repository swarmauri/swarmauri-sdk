from typing import Any, Sequence, Tuple, TypeVar, Union
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.similarities.ISimilarity import ISimilarity
import logging

# Configure logging
logger = logging.getLogger(__name__)

InputType = TypeVar('InputType', str, bytes, Any)
OutputType = TypeVar('OutputType', float)

@ComponentBase.register_model()
class SimilarityBase(ISimilarity, ComponentBase):
    """
    Concrete base class for implementing similarity measures.

    This class provides a foundation for various similarity measures by implementing
    the base functionality while leaving specific calculations to subclasses.
    It handles bounds checking, reflexivity, and symmetry properties.

    All specific similarity calculation methods should be implemented in derived classes.
    """
    
    resource: str = ResourceTypes.SIMILARITY.value

    def __init__(self):
        """
        Initialize the SimilarityBase instance.
        """
        super().__init__()
        logger.debug("Initialized SimilarityBase instance")

    def similarity(self, x: InputType, y: InputType) -> float:
        """
        Calculate the similarity between two elements.

        Args:
            x: InputType
                The first element to compare
            y: InputType
                The second element to compare

        Returns:
            float:
                A float representing the similarity between x and y.
                If bounded, should be between 0 and 1.

        Raises:
            NotImplementedError: Always raised as this method must be implemented by subclasses
        """
        logger.error("similarity method not implemented by subclass")
        raise NotImplementedError("similarity must be implemented by subclass")

    def similarities(self, pairs: Sequence[Tuple[InputType, InputType]]) -> Sequence[float]:
        """
        Calculate similarities for multiple pairs of elements.

        Args:
            pairs: Sequence[Tuple[InputType, InputType]]
                A sequence of element pairs to compare

        Returns:
            Sequence[float]:
                A sequence of similarity scores corresponding to each pair.

        Raises:
            NotImplementedError: Always raised as this method must be implemented by subclasses
        """
        logger.error("similarities method not implemented by subclass")
        raise NotImplementedError("similarities must be implemented by subclass")

    def dissimilarity(self, x: InputType, y: InputType) -> float:
        """
        Calculate the dissimilarity between two elements.

        Args:
            x: InputType
                The first element to compare
            y: InputType
                The second element to compare

        Returns:
            float:
                A float representing the dissimilarity between x and y.
                If bounded, should be between 0 and 1.

        Raises:
            NotImplementedError: Always raised as this method must be implemented by subclasses
        """
        logger.error("dissimilarity method not implemented by subclass")
        raise NotImplementedError("dissimilarity must be implemented by subclass")

    def dissimilarities(self, pairs: Sequence[Tuple[InputType, InputType]]) -> Sequence[float]:
        """
        Calculate dissimilarities for multiple pairs of elements.

        Args:
            pairs: Sequence[Tuple[InputType, InputType]]
                A sequence of element pairs to compare

        Returns:
            Sequence[float]:
                A sequence of dissimilarity scores corresponding to each pair.

        Raises:
            NotImplementedError: Always raised as this method must be implemented by subclasses
        """
        logger.error("dissimilarities method not implemented by subclass")
        raise NotImplementedError("dissimilarities must be implemented by subclass")