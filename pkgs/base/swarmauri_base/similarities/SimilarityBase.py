from typing import Union, List, Optional
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.similarities.ISimilarity import ISimilarity
import logging

logger = logging.getLogger(__name__)

@ComponentBase.register_model()
class SimilarityBase(ISimilarity, ComponentBase):
    """
    Base implementation of the ISimilarity interface providing foundational functionality.
    
    This class provides a concrete implementation of the ISimilarity interface, serving as a base
    class for various similarity measures. It implements the required methods with base logic while
    leaving specific calculations to derived classes.
    
    Attributes:
        resource: Type of resource this component represents, defaults to SIMILARITY.
    """
    resource: Optional[str] = Field(default=ResourceTypes.SIMILARITY.value)

    def similarity(
        self, 
        x: Union[IVector, IMatrix, Tuple, str, Callable], 
        y: Union[IVector, IMatrix, Tuple, str, Callable]
    ) -> float:
        """
        Base method for calculating similarity between two elements.
        
        Args:
            x: First element to compare.
            y: Second element to compare.
            
        Returns:
            float: Similarity score between x and y.
            
        Raises:
            NotImplementedError: This method must be implemented in a derived class.
        """
        raise NotImplementedError(
            "Similarity calculation must be implemented in a derived class."
        )

    def similarities(
        self, 
        x: Union[IVector, IMatrix, Tuple, str, Callable], 
        ys: Union[
            List[Union[IVector, IMatrix, Tuple, str, Callable]], 
            Union[IVector, IMatrix, Tuple, str, Callable]
        ]
    ) -> Union[float, List[float]]:
        """
        Base method for calculating similarities between an element and multiple elements.
        
        Args:
            x: Reference element to compare against.
            ys: List of elements or single element to compare with x.
            
        Returns:
            Union[float, List[float]]: Similarity scores between x and each element in ys.
            
        Raises:
            NotImplementedError: This method must be implemented in a derived class.
        """
        raise NotImplementedError(
            "Similarities calculation must be implemented in a derived class."
        )

    def dissimilarity(
        self, 
        x: Union[IVector, IMatrix, Tuple, str, Callable], 
        y: Union[IVector, IMatrix, Tuple, str, Callable]
    ) -> float:
        """
        Base method for calculating dissimilarity between two elements.
        
        Args:
            x: First element to compare.
            y: Second element to compare.
            
        Returns:
            float: Dissimilarity score between x and y.
            
        Raises:
            NotImplementedError: This method must be implemented in a derived class.
        """
        raise NotImplementedError(
            "Dissimilarity calculation must be implemented in a derived class."
        )

    def dissimilarities(
        self, 
        x: Union[IVector, IMatrix, Tuple, str, Callable], 
        ys: Union[
            List[Union[IVector, IMatrix, Tuple, str, Callable]], 
            Union[IVector, IMatrix, Tuple, str, Callable]
        ]
    ) -> Union[float, List[float]]:
        """
        Base method for calculating dissimilarities between an element and multiple elements.
        
        Args:
            x: Reference element to compare against.
            ys: List of elements or single element to compare with x.
            
        Returns:
            Union[float, List[float]]: Dissimilarity scores between x and each element in ys.
            
        Raises:
            NotImplementedError: This method must be implemented in a derived class.
        """
        raise NotImplementedError(
            "Dissimilarities calculation must be implemented in a derived class."
        )

    def check_boundedness(
        self, 
        x: Union[IVector, IMatrix, Tuple, str, Callable], 
        y: Union[IVector, IMatrix, Tuple, str, Callable]
    ) -> bool:
        """
        Base method for checking if the similarity measure is bounded.
        
        Args:
            x: First element to compare.
            y: Second element to compare.
            
        Returns:
            bool: True if the measure is bounded, False otherwise.
            
        Raises:
            NotImplementedError: This method must be implemented in a derived class.
        """
        raise NotImplementedError(
            "Boundedness check must be implemented in a derived class."
        )

    def check_reflexivity(
        self, 
        x: Union[IVector, IMatrix, Tuple, str, Callable]
    ) -> bool:
        """
        Base method for checking if the similarity measure is reflexive.
        
        Args:
            x: Element to check reflexivity for.
            
        Returns:
            bool: True if the measure is reflexive, False otherwise.
            
        Raises:
            NotImplementedError: This method must be implemented in a derived class.
        """
        raise NotImplementedError(
            "Reflexivity check must be implemented in a derived class."
        )

    def check_symmetry(
        self, 
        x: Union[IVector, IMatrix, Tuple, str, Callable], 
        y: Union[IVector, IMatrix, Tuple, str, Callable]
    ) -> bool:
        """
        Base method for checking if the similarity measure is symmetric.
        
        Args:
            x: First element to compare.
            y: Second element to compare.
            
        Returns:
            bool: True if the measure is symmetric, False otherwise.
            
        Raises:
            NotImplementedError: This method must be implemented in a derived class.
        """
        raise NotImplementedError(
            "Symmetry check must be implemented in a derived class."
        )

    def check_identity(
        self, 
        x: Union[IVector, IMatrix, Tuple, str, Callable], 
        y: Union[IVector, IMatrix, Tuple, str, Callable]
    ) -> bool:
        """
        Base method for checking if the similarity measure satisfies identity.
        
        Args:
            x: First element to compare.
            y: Second element to compare.
            
        Returns:
            bool: True if the measure satisfies identity, False otherwise.
            
        Raises:
            NotImplementedError: This method must be implemented in a derived class.
        """
        raise NotImplementedError(
            "Identity check must be implemented in a derived class."
        )