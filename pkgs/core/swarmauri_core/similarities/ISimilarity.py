from abc import ABC, abstractmethod
from typing import Any, Optional, TypeVar, Generic
import logging

# Set up logging
logger = logging.getLogger(__name__)

T = TypeVar('T')

class ISimilarity(ABC, Generic[T]):
    """
    Abstract base class for similarity measures.
    
    Defines the interface for calculating similarity between objects.
    Similarity measures can be directional or bounded, supporting
    various comparison methods like cosine similarity.
    
    Attributes
    ----------
    is_bounded : bool
        Indicates if the similarity measure is bounded within a specific range.
    lower_bound : float
        The lower bound of the similarity measure if bounded.
    upper_bound : float
        The upper bound of the similarity measure if bounded.
    """
    
    def __init__(self, is_bounded: bool = True, lower_bound: float = 0.0, upper_bound: float = 1.0):
        """
        Initialize a similarity measure.
        
        Parameters
        ----------
        is_bounded : bool, optional
            Whether the similarity measure is bounded, by default True
        lower_bound : float, optional
            Lower bound of similarity if bounded, by default 0.0
        upper_bound : float, optional
            Upper bound of similarity if bounded, by default 1.0
        """
        self.is_bounded = is_bounded
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        
        # Validate bounds if similarity is bounded
        if is_bounded and lower_bound >= upper_bound:
            logger.error("Lower bound must be less than upper bound")
            raise ValueError("Lower bound must be less than upper bound")
        
        logger.debug(f"Initialized {self.__class__.__name__} with bounds: "
                    f"[{lower_bound}, {upper_bound}], is_bounded={is_bounded}")
    
    @abstractmethod
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
        """
        pass
    
    @abstractmethod
    def is_reflexive(self) -> bool:
        """
        Check if the similarity measure is reflexive.
        
        A similarity measure is reflexive if sim(x, x) = max_similarity for all x.
        
        Returns
        -------
        bool
            True if the similarity measure is reflexive, False otherwise
        """
        pass
    
    @abstractmethod
    def is_symmetric(self) -> bool:
        """
        Check if the similarity measure is symmetric.
        
        A similarity measure is symmetric if sim(a, b) = sim(b, a) for all a, b.
        
        Returns
        -------
        bool
            True if the similarity measure is symmetric, False otherwise
        """
        pass
    
    def normalize(self, value: float) -> float:
        """
        Normalize a similarity value to fit within the defined bounds.
        
        Parameters
        ----------
        value : float
            Raw similarity value to normalize
            
        Returns
        -------
        float
            Normalized similarity value within bounds
        """
        if not self.is_bounded:
            logger.debug(f"Value {value} not normalized (unbounded similarity)")
            return value
        
        # Clip the value to be within bounds
        normalized = max(min(value, self.upper_bound), self.lower_bound)
        
        if normalized != value:
            logger.debug(f"Normalized value from {value} to {normalized}")
            
        return normalized
    
    def __str__(self) -> str:
        """
        Get string representation of the similarity measure.
        
        Returns
        -------
        str
            String representation
        """
        bounds_str = f"[{self.lower_bound}, {self.upper_bound}]" if self.is_bounded else "unbounded"
        return f"{self.__class__.__name__} (bounds: {bounds_str})"