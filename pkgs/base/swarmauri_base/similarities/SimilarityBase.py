from typing import Union, Sequence, Optional
from abc import ABC
from swarmauri_core.similarities.ISimilarity import ISimilarity
from swarmauri_base.ComponentBase import ComponentBase
import logging

logger = logging.getLogger(__name__)


@ComponentBase.register_model()
class SimilarityBase(ISimilarity, ComponentBase):
    """
    Base implementation for similarity measures. This class provides a concrete
    foundation for directional or feature-based similarity calculations.
    It implements bounds, reflexivity, and optional symmetry for similarity
    scoring while leaving specific implementation details to subclasses.
    
    The class inherits from ComponentBase and implements the ISimilarity
    interface. It provides basic structures and raises appropriate exceptions
    for methods that require implementation in derived classes.
    """
    resource: Optional[str] = "SIMILARITY"

    def similarity(self, x: Union[IVector, IMatrix, Sequence, str, Callable], 
                    y: Union[IVector, IMatrix, Sequence, str, Callable]) -> float:
        """
        Calculates the similarity between two elements.
        
        Args:
            x: First element to compare
            y: Second element to compare
            
        Returns:
            float: Similarity score between x and y
            
        Raises:
            NotImplementedError: Method not implemented in base class
        """
        logger.debug(f"Calculating similarity between {x} and {y}")
        raise NotImplementedError("similarity method must be implemented in a subclass")

    def similarities(self, xs: Union[IVector, IMatrix, Sequence, str, Callable], 
                     ys: Union[IVector, IMatrix, Sequence, str, Callable]) -> Union[float, Sequence[float]]:
        """
        Calculates similarities for multiple pairs of elements.
        
        Args:
            xs: First set of elements to compare
            ys: Second set of elements to compare
            
        Returns:
            Union[float, Sequence[float]]: Similarity scores for the pairs
            
        Raises:
            NotImplementedError: Method not implemented in base class
        """
        logger.debug(f"Calculating similarities between {xs} and {ys}")
        raise NotImplementedError("similarities method must be implemented in a subclass")

    def dissimilarity(self, x: Union[IVector, IMatrix, Sequence, str, Callable], 
                      y: Union[IVector, IMatrix, Sequence, str, Callable]) -> float:
        """
        Calculates the dissimilarity between two elements.
        
        Args:
            x: First element to compare
            y: Second element to compare
            
        Returns:
            float: Dissimilarity score between x and y
            
        Raises:
            NotImplementedError: Method not implemented in base class
        """
        logger.debug(f"Calculating dissimilarity between {x} and {y}")
        raise NotImplementedError("dissimilarity method must be implemented in a subclass")

    def dissimilarities(self, xs: Union[IVector, IMatrix, Sequence, str, Callable], 
                       ys: Union[IVector, IMatrix, Sequence, str, Callable]) -> Union[float, Sequence[float]]:
        """
        Calculates dissimilarities for multiple pairs of elements.
        
        Args:
            xs: First set of elements to compare
            ys: Second set of elements to compare
            
        Returns:
            Union[float, Sequence[float]]: Dissimilarity scores for the pairs
            
        Raises:
            NotImplementedError: Method not implemented in base class
        """
        logger.debug(f"Calculating dissimilarities between {xs} and {ys}")
        raise NotImplementedError("dissimilarities method must be implemented in a subclass")

    def check_boundedness(self) -> bool:
        """
        Checks if the similarity measure is bounded.
        
        Returns:
            bool: True if the measure is bounded, False otherwise
            
        Raises:
            NotImplementedError: Method not implemented in base class
        """
        logger.debug("Checking boundedness")
        raise NotImplementedError("check_boundedness method must be implemented in a subclass")

    def check_reflexivity(self) -> bool:
        """
        Checks if the similarity measure satisfies reflexivity.
        A measure is reflexive if s(x, x) = 1 for all x.
        
        Returns:
            bool: True if the measure is reflexive, False otherwise
            
        Raises:
            NotImplementedError: Method not implemented in base class
        """
        logger.debug("Checking reflexivity")
        raise NotImplementedError("check_reflexivity method must be implemented in a subclass")

    def check_symmetry(self) -> bool:
        """
        Checks if the similarity measure is symmetric.
        A measure is symmetric if s(x, y) = s(y, x) for all x, y.
        
        Returns:
            bool: True if the measure is symmetric, False otherwise
            
        Raises:
            NotImplementedError: Method not implemented in base class
        """
        logger.debug("Checking symmetry")
        raise NotImplementedError("check_symmetry method must be implemented in a subclass")

    def check_identity(self) -> bool:
        """
        Checks if the similarity measure satisfies identity of discernibles.
        A measure satisfies identity if s(x, y) = 1 if and only if x = y.
        
        Returns:
            bool: True if the measure satisfies identity, False otherwise
            
        Raises:
            NotImplementedError: Method not implemented in base class
        """
        logger.debug("Checking identity of discernibles")
        raise NotImplementedError("check_identity method must be implemented in a subclass")