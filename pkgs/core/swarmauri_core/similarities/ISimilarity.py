from abc import ABC, abstractmethod
from typing import Union, Sequence, Callable
import logging

from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix

logger = logging.getLogger(__name__)


class ISimilarity(ABC):
    """
    Interface for similarity measures. This abstract base class defines the core
    methods for calculating similarities and dissimilarities between various
    types of data, including vectors, matrices, sequences, strings, and callables.
    
    The interface provides methods for both single pair comparisons and batch
    comparisons. Additionally, it includes checks for important properties of
    similarity measures like boundedness, reflexivity, symmetry, and identity.
    
    Methods:
        similarity: Calculates the similarity between two elements
        similarities: Calculates similarities for multiple pairs
        dissimilarity: Calculates the dissimilarity between two elements
        dissimilarities: Calculates dissimilarities for multiple pairs
        check_boundedness: Verifies if the similarity measure is bounded
        check_reflexivity: Checks if the measure satisfies reflexivity
        check_symmetry: Verifies if the measure is symmetric
        check_identity: Checks if the measure satisfies identity of discernibles
    """

    @abstractmethod
    def similarity(self, x: Union[IVector, IMatrix, Sequence, str, Callable], 
                    y: Union[IVector, IMatrix, Sequence, str, Callable]) -> float:
        """
        Calculates the similarity between two elements.
        
        Args:
            x: First element to compare
            y: Second element to compare
            
        Returns:
            float: Similarity score between x and y
        """
        logger.debug(f"Calculating similarity between {x} and {y}")
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def similarities(self, xs: Union[IVector, IMatrix, Sequence, str, Callable], 
                     ys: Union[IVector, IMatrix, Sequence, str, Callable]) -> Union[float, Sequence[float]]:
        """
        Calculates similarities for multiple pairs of elements.
        
        Args:
            xs: First set of elements to compare
            ys: Second set of elements to compare
            
        Returns:
            Union[float, Sequence[float]]: Similarity scores for the pairs
        """
        logger.debug(f"Calculating similarities between {xs} and {ys}")
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def dissimilarity(self, x: Union[IVector, IMatrix, Sequence, str, Callable], 
                      y: Union[IVector, IMatrix, Sequence, str, Callable]) -> float:
        """
        Calculates the dissimilarity between two elements.
        
        Args:
            x: First element to compare
            y: Second element to compare
            
        Returns:
            float: Dissimilarity score between x and y
        """
        logger.debug(f"Calculating dissimilarity between {x} and {y}")
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def dissimilarities(self, xs: Union[IVector, IMatrix, Sequence, str, Callable], 
                       ys: Union[IVector, IMatrix, Sequence, str, Callable]) -> Union[float, Sequence[float]]:
        """
        Calculates dissimilarities for multiple pairs of elements.
        
        Args:
            xs: First set of elements to compare
            ys: Second set of elements to compare
            
        Returns:
            Union[float, Sequence[float]]: Dissimilarity scores for the pairs
        """
        logger.debug(f"Calculating dissimilarities between {xs} and {ys}")
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def check_boundedness(self) -> bool:
        """
        Checks if the similarity measure is bounded.
        
        Returns:
            bool: True if the measure is bounded, False otherwise
        """
        logger.debug("Checking boundedness")
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def check_reflexivity(self) -> bool:
        """
        Checks if the similarity measure satisfies reflexivity.
        A measure is reflexive if s(x, x) = 1 for all x.
        
        Returns:
            bool: True if the measure is reflexive, False otherwise
        """
        logger.debug("Checking reflexivity")
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def check_symmetry(self) -> bool:
        """
        Checks if the similarity measure is symmetric.
        A measure is symmetric if s(x, y) = s(y, x) for all x, y.
        
        Returns:
            bool: True if the measure is symmetric, False otherwise
        """
        logger.debug("Checking symmetry")
        raise NotImplementedError("Method not implemented")

    @abstractmethod
    def check_identity(self) -> bool:
        """
        Checks if the similarity measure satisfies identity of discernibles.
        A measure satisfies identity if s(x, y) = 1 if and only if x = y.
        
        Returns:
            bool: True if the measure satisfies identity, False otherwise
        """
        logger.debug("Checking identity of discernibles")
        raise NotImplementedError("Method not implemented")