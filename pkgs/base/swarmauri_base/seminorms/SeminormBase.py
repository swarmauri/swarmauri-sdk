import logging
from abc import ABC, abstractmethod
from typing import TypeVar, Union, Callable, Sequence
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.seminorms.ISeminorm import ISeminorm

logger = logging.getLogger(__name__)

T = TypeVar('T', IVector, IMatrix, Sequence, str, Callable)

@ComponentBase.register_model()
class SeminormBase(ISeminorm, ComponentBase):
    """
    Base class providing reusable logic for defining seminorms in partial vector spaces.
    
    This class implements the ISeminorm interface and provides basic functionality
    that can be extended by specific seminorm implementations. It includes logging
    and basic structure that must be extended with concrete implementations.
    """
    
    resource: str = ResourceTypes.SEMINORM.value
    """
    The resource type identifier for seminorm components.
    """
    
    @abstractmethod
    def compute(self, input: T) -> float:
        """
        Computes the seminorm value for the given input.
        
        Args:
            input: T
                The input to compute the seminorm for. Can be a vector, matrix,
                sequence, string, or callable.
                
        Returns:
            float: The computed seminorm value
            
        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        logger.warning("compute method called on base class - not implemented")
        raise NotImplementedError("compute method must be implemented by subclass")
    
    @abstractmethod
    def check_triangle_inequality(self, a: T, b: T) -> bool:
        """
        Checks if the triangle inequality holds for the given inputs.
        
        Args:
            a: T
                The first input
            b: T
                The second input
                
        Returns:
            bool: True if the triangle inequality holds, False otherwise
            
        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        logger.warning("check_triangle_inequality method called on base class - not implemented")
        raise NotImplementedError("check_triangle_inequality method must be implemented by subclass")
    
    @abstractmethod
    def check_scalar_homogeneity(self, a: T, scalar: float) -> bool:
        """
        Checks if the scalar homogeneity property holds for the given input and scalar.
        
        Args:
            a: T
                The input to check
            scalar: float
                The scalar to test homogeneity with
                
        Returns:
            bool: True if scalar homogeneity holds, False otherwise
            
        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        logger.warning("check_scalar_homogeneity method called on base class - not implemented")
        raise NotImplementedError("check_scalar_homogeneity method must be implemented by subclass")