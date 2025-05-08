from typing import Any, Optional, TypeVar, Generic
import logging
from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.similarities.ISimilarity import ISimilarity

# Set up logging
logger = logging.getLogger(__name__)

T = TypeVar('T')

@ComponentBase.register_model()
class SimilarityBase(ISimilarity[T], ComponentBase):
    """
    Base class for implementing similarity measures.
    
    Provides a foundation for directional or feature-based similarity
    with implementation of bounds, reflexivity and optional symmetry
    for similarity scoring.
    
    Attributes
    ----------
    resource : str
        Resource type identifier
    is_bounded : bool
        Indicates if the similarity measure is bounded within a specific range
    lower_bound : float
        The lower bound of the similarity measure if bounded
    upper_bound : float
        The upper bound of the similarity measure if bounded
    """
    
    resource: Optional[str] = Field(default=ResourceTypes.SIMILARITY.value)
    
    def __init__(self, is_bounded: bool = True, lower_bound: float = 0.0, 
                 upper_bound: float = 1.0, **kwargs):
        """
        Initialize the similarity base class.
        
        Parameters
        ----------
        is_bounded : bool, optional
            Whether the similarity measure is bounded, by default True
        lower_bound : float, optional
            Lower bound of similarity if bounded, by default 0.0
        upper_bound : float, optional
            Upper bound of similarity if bounded, by default 1.0
        **kwargs : dict
            Additional keyword arguments to pass to parent classes
        """
        ISimilarity.__init__(self, is_bounded=is_bounded, 
                             lower_bound=lower_bound, 
                             upper_bound=upper_bound)
        ComponentBase.__init__(self, **kwargs)
        logger.debug(f"Initialized {self.__class__.__name__}")
    
    def calculate(self, a: T, b: T) -> float:
        """
        Calculate similarity between two objects.
        
        Parameters
        ----------
        a : T
            First object to compare
        b : T
            Second object to compare
            
        Returns
        -------
        float
            Similarity score between objects
            
        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses
        """
        logger.error(f"{self.__class__.__name__}.calculate() not implemented")
        raise NotImplementedError(
            f"Method 'calculate' must be implemented by {self.__class__.__name__} subclasses"
        )
    
    def is_reflexive(self) -> bool:
        """
        Check if the similarity measure is reflexive.
        
        A similarity measure is reflexive if sim(x, x) = max_similarity for all x.
        
        Returns
        -------
        bool
            True if the similarity measure is reflexive, False otherwise
            
        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses
        """
        logger.error(f"{self.__class__.__name__}.is_reflexive() not implemented")
        raise NotImplementedError(
            f"Method 'is_reflexive' must be implemented by {self.__class__.__name__} subclasses"
        )
    
    def is_symmetric(self) -> bool:
        """
        Check if the similarity measure is symmetric.
        
        A similarity measure is symmetric if sim(a, b) = sim(b, a) for all a, b.
        
        Returns
        -------
        bool
            True if the similarity measure is symmetric, False otherwise
            
        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses
        """
        logger.error(f"{self.__class__.__name__}.is_symmetric() not implemented")
        raise NotImplementedError(
            f"Method 'is_symmetric' must be implemented by {self.__class__.__name__} subclasses"
        )
    
    def __str__(self) -> str:
        """
        Get string representation of the similarity measure.
        
        Returns
        -------
        str
            String representation including bounds information
        """
        bounds_str = f"[{self.lower_bound}, {self.upper_bound}]" if self.is_bounded else "unbounded"
        return f"{self.__class__.__name__} (bounds: {bounds_str})"