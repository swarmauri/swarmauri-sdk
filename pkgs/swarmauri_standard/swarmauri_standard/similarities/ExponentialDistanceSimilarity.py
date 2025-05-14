from typing import Callable, Sequence, List, Optional, Literal, Union, Any
import logging
import math

from swarmauri_core.similarities.ISimilarity import ComparableType
from swarmauri_base.similarities.SimilarityBase import SimilarityBase
from swarmauri_base.ComponentBase import ComponentBase

# Set up logger
logger = logging.getLogger(__name__)


@ComponentBase.register_type(SimilarityBase, "ExponentialDistanceSimilarity")
class ExponentialDistanceSimilarity(SimilarityBase):
    """
    Similarity measure based on exponentially decaying distance.
    
    This class implements a similarity measure where the similarity between two objects
    decreases exponentially with the distance between them. The formula used is:
    similarity = exp(-alpha * distance(x, y))
    
    Attributes
    ----------
    type : Literal["ExponentialDistanceSimilarity"]
        The type identifier for this similarity measure
    alpha : float
        Decay rate parameter that controls how quickly similarity decreases with distance
    distance_func : Callable[[ComparableType, ComparableType], float]
        Function that calculates distance between two objects
    """
    
    type: Literal["ExponentialDistanceSimilarity"] = "ExponentialDistanceSimilarity"
    alpha: float
    distance_func: Callable[[ComparableType, ComparableType], float]
    
    def __init__(self, 
                 distance_func: Callable[[ComparableType, ComparableType], float],
                 alpha: float = 1.0):
        """
        Initialize the exponential distance similarity measure.
        
        Parameters
        ----------
        distance_func : Callable[[ComparableType, ComparableType], float]
            Function that calculates distance between two objects
        alpha : float, optional
            Decay rate parameter, by default 1.0. Higher values make similarity 
            decrease more rapidly with distance.
            
        Raises
        ------
        ValueError
            If alpha is not positive or distance_func is not callable
        """
        super().__init__()
        
        if not callable(distance_func):
            error_msg = "distance_func must be callable"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        if alpha <= 0:
            error_msg = "alpha must be positive"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        self.distance_func = distance_func
        self.alpha = alpha
        logger.debug(f"Initialized ExponentialDistanceSimilarity with alpha={alpha}")
    
    def similarity(self, x: ComparableType, y: ComparableType) -> float:
        """
        Calculate the similarity between two objects using exponential decay of distance.
        
        Parameters
        ----------
        x : ComparableType
            First object to compare
        y : ComparableType
            Second object to compare
            
        Returns
        -------
        float
            Similarity score between x and y in the range [0, 1]
            
        Raises
        ------
        ValueError
            If the objects are incomparable
        TypeError
            If the input types are not supported by the distance function
        """
        try:
            # Calculate distance between x and y
            distance = self.distance_func(x, y)
            
            # Check if distance is negative
            if distance < 0:
                error_msg = f"Distance function returned negative value: {distance}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            # Calculate similarity using exponential decay
            similarity_value = math.exp(-self.alpha * distance)
            
            logger.debug(f"Calculated similarity: {similarity_value} for distance: {distance}")
            return similarity_value
            
        except Exception as e:
            logger.error(f"Error in similarity calculation: {str(e)}")
            raise
    
    def similarities(self, x: ComparableType, ys: Sequence[ComparableType]) -> List[float]:
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
        ValueError
            If any objects are incomparable
        TypeError
            If any input types are not supported by the distance function
        """
        try:
            # Calculate distances for all objects in ys
            distances = [self.distance_func(x, y) for y in ys]
            
            # Check if any distance is negative
            if any(d < 0 for d in distances):
                error_msg = "Distance function returned negative value(s)"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            # Calculate similarities using exponential decay
            similarity_values = [math.exp(-self.alpha * d) for d in distances]
            
            logger.debug(f"Calculated {len(similarity_values)} similarity values")
            return similarity_values
            
        except Exception as e:
            logger.error(f"Error in similarities calculation: {str(e)}")
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
            Dissimilarity score between x and y in the range [0, 1]
            
        Raises
        ------
        ValueError
            If the objects are incomparable
        TypeError
            If the input types are not supported by the distance function
        """
        try:
            # For bounded similarity in [0,1], dissimilarity is 1-similarity
            return 1.0 - self.similarity(x, y)
        except Exception as e:
            logger.error(f"Error in dissimilarity calculation: {str(e)}")
            raise
    
    def check_bounded(self) -> bool:
        """
        Check if the similarity measure is bounded.
        
        The exponential similarity measure is bounded in the range [0,1].
        
        Returns
        -------
        bool
            True, as this similarity measure is bounded
        """
        # Exponential similarity is always bounded in [0,1]
        return True
    
    def to_dict(self) -> dict:
        """
        Convert the similarity measure to a dictionary representation.
        
        Returns
        -------
        dict
            Dictionary representation of the similarity measure
            
        Note
        ----
        The distance function cannot be directly serialized, so it's not included
        in the dictionary. When deserializing, the distance function must be provided.
        """
        base_dict = super().to_dict()
        base_dict.update({
            "alpha": self.alpha,
            # Note: distance_func cannot be serialized directly
            "distance_func_info": "Distance function cannot be serialized, must be provided when reconstructing"
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: dict, **kwargs) -> 'ExponentialDistanceSimilarity':
        """
        Create an instance from a dictionary representation.
        
        Parameters
        ----------
        data : dict
            Dictionary representation of the similarity measure
        **kwargs
            Additional keyword arguments, must include 'distance_func'
            
        Returns
        -------
        ExponentialDistanceSimilarity
            New instance of the similarity measure
            
        Raises
        ------
        ValueError
            If 'distance_func' is not provided in kwargs
        """
        if 'distance_func' not in kwargs:
            error_msg = "distance_func must be provided when reconstructing ExponentialDistanceSimilarity"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        distance_func = kwargs['distance_func']
        alpha = data.get('alpha', 1.0)
        
        return cls(distance_func=distance_func, alpha=alpha)