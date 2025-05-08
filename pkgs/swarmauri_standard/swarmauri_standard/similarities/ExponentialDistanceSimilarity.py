from typing import Any, Callable, Generic, Literal, Optional, TypeVar, Union
import logging
import math
from pydantic import Field

from swarmauri_base.similarities.SimilarityBase import SimilarityBase

# Set up logging
logger = logging.getLogger(__name__)

T = TypeVar('T')

@SimilarityBase.register_type()
class ExponentialDistanceSimilarity(SimilarityBase, Generic[T]):
    """
    Implements similarity that exponentially decays with distance.
    
    This similarity measure uses the formula: sim(a, b) = e^(-lambda * distance(a, b))
    where lambda is a decay factor that controls how quickly similarity decreases
    with distance. Supports arbitrary distance functions.
    
    Attributes
    ----------
    type : Literal["ExponentialDistanceSimilarity"]
        Type identifier for this similarity measure
    distance_function : Callable[[T, T], float]
        Function that calculates distance between two objects
    decay_factor : float
        Controls how quickly similarity decays with distance (lambda)
    """
    
    type: Literal["ExponentialDistanceSimilarity"] = "ExponentialDistanceSimilarity"
    distance_function: Callable[[T, T], float] = Field(
        ..., description="Function to calculate distance between two objects"
    )
    decay_factor: float = Field(
        default=1.0, 
        description="Decay factor (lambda) that controls decay rate",
        gt=0.0
    )
    
    def __init__(
        self, 
        distance_function: Callable[[T, T], float],
        decay_factor: float = 1.0,
        is_bounded: bool = True, 
        lower_bound: float = 0.0, 
        upper_bound: float = 1.0, 
        **kwargs
    ):
        """
        Initialize the exponential distance similarity measure.
        
        Parameters
        ----------
        distance_function : Callable[[T, T], float]
            Function that calculates distance between two objects
        decay_factor : float, optional
            Controls how quickly similarity decays with distance, by default 1.0
        is_bounded : bool, optional
            Whether the similarity measure is bounded, by default True
        lower_bound : float, optional
            Lower bound of similarity if bounded, by default 0.0
        upper_bound : float, optional
            Upper bound of similarity if bounded, by default 1.0
        **kwargs : dict
            Additional keyword arguments to pass to parent classes
        """
        super().__init__(
            is_bounded=is_bounded, 
            lower_bound=lower_bound, 
            upper_bound=upper_bound, 
            **kwargs
        )
        self.distance_function = distance_function
        self.decay_factor = decay_factor
        logger.debug(f"Initialized {self.__class__.__name__} with decay factor {decay_factor}")
    
    def calculate(self, a: T, b: T) -> float:
        """
        Calculate similarity between two objects based on exponential decay of distance.
        
        Parameters
        ----------
        a : T
            First object to compare
        b : T
            Second object to compare
            
        Returns
        -------
        float
            Similarity score between objects, with e^(-lambda * distance(a, b))
        """
        try:
            # Calculate distance between objects
            distance = self.distance_function(a, b)
            
            # Ensure distance is non-negative
            if distance < 0:
                logger.warning(f"Distance function returned negative value: {distance}. Using absolute value.")
                distance = abs(distance)
            
            # Calculate similarity using exponential decay
            similarity = math.exp(-self.decay_factor * distance)
            
            logger.debug(f"Calculated similarity {similarity} for distance {distance}")
            return similarity
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            raise
    
    def is_reflexive(self) -> bool:
        """
        Check if the similarity measure is reflexive.
        
        For exponential distance similarity, it is reflexive if the distance
        function returns 0 for identical objects, which results in a similarity of 1.
        
        Returns
        -------
        bool
            True, as this similarity measure is reflexive when distance(x, x) = 0
        """
        # Exponential similarity is reflexive if distance(x, x) = 0
        # which gives e^0 = 1, the maximum similarity
        return True
    
    def is_symmetric(self) -> bool:
        """
        Check if the similarity measure is symmetric.
        
        For exponential distance similarity, it is symmetric if the underlying
        distance function is symmetric.
        
        Returns
        -------
        bool
            True, assuming the distance function is symmetric
        """
        # Exponential similarity is symmetric if the distance function is symmetric
        # Most distance functions are symmetric, so we return True by default
        # Note: This might not be true for all distance functions
        return True
    
    def __str__(self) -> str:
        """
        Get string representation of the similarity measure.
        
        Returns
        -------
        str
            String representation including decay factor and bounds information
        """
        bounds_str = f"[{self.lower_bound}, {self.upper_bound}]" if self.is_bounded else "unbounded"
        return f"{self.__class__.__name__} (decay factor: {self.decay_factor}, bounds: {bounds_str})"