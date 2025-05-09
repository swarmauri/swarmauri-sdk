from abc import ABC, abstractmethod
from typing import Union
import logging

# Define logger
logger = logging.getLogger(__name__)

# Import the interface class
from swarmauri_core.inner_products.IInnerProduct import IInnerProduct

class InnerProductBase(ABC, IInnerProduct):
    """
    A base implementation of the IInnerProduct interface.
    
    This class provides a foundation for implementing inner product calculations.
    It includes abstract methods that must be implemented by subclasses.
    """
    
    @abstractmethod
    def compute(self, a: Union[object, object], b: Union[object, object]) -> Union[float, complex]:
        """
        Computes the inner product between two elements.
        
        Args:
            a: The first element for the inner product
            b: The second element for the inner product
            
        Returns:
            Union[float, complex]: The result of the inner product computation
            
        Raises:
            NotImplementedError: If the method is not implemented in the subclass
        """
        logger.error("Compute method not implemented in subclass")
        raise NotImplementedError("Subclass must implement the compute method")
    
    def check_conjugate_symmetry(self, a: Union[object, object], b: Union[object, object]) -> bool:
        """
        Checks if the inner product implementation satisfies conjugate symmetry.
        
        Args:
            a: The first element to check
            b: The second element to check
            
        Returns:
            bool: True if conjugate symmetry holds, False otherwise
            
        Raises:
            NotImplementedError: If the method is not implemented in the subclass
        """
        logger.error("check_conjugate_symmetry method not implemented in subclass")
        raise NotImplementedError("Subclass must implement the check_conjugate_symmetry method")
    
    def check_linearity_first_argument(self, a: Union[object, object], b: Union[object, object], c: Union[object, object]) -> bool:
        """
        Checks if the inner product implementation is linear in the first argument.
        
        Args:
            a: The first element for linearity check
            b: The second element for linearity check
            c: The third element for linearity check
            
        Returns:
            bool: True if linearity in the first argument holds, False otherwise
            
        Raises:
            NotImplementedError: If the method is not implemented in the subclass
        """
        logger.error("check_linearity_first_argument method not implemented in subclass")
        raise NotImplementedError("Subclass must implement the check_linearity_first_argument method")
    
    def check_positivity(self, a: Union[object, object]) -> bool:
        """
        Checks if the inner product implementation satisfies positive definiteness.
        
        Args:
            a: The element to check for positivity
            
        Returns:
            bool: True if positivity holds, False otherwise
            
        Raises:
            NotImplementedError: If the method is not implemented in the subclass
        """
        logger.error("check_positivity method not implemented in subclass")
        raise NotImplementedError("Subclass must implement the check_positivity method")