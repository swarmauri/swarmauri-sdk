from abc import ABC, abstractmethod
import logging
from typing import Any, TypeVar, Generic

# Set up logging
logger = logging.getLogger(__name__)

# Type variable for generic typing
T = TypeVar('T')

class ISeminorm(Generic[T], ABC):
    """
    Interface for seminorm structures.
    
    A seminorm is a function that satisfies the properties of a norm except for definiteness.
    In particular, a seminorm p satisfies:
    1. p(x) >= 0 for all x (non-negativity)
    2. p(αx) = |α|p(x) for all x and scalar α (scalar homogeneity)
    3. p(x + y) <= p(x) + p(y) for all x, y (triangle inequality)
    
    Unlike a norm, a seminorm may have p(x) = 0 for some non-zero x.
    """
    
    @abstractmethod
    def evaluate(self, x: T) -> float:
        """
        Evaluate the seminorm for a given input.
        
        Parameters
        ----------
        x : T
            The input to evaluate the seminorm on.
            
        Returns
        -------
        float
            The seminorm value, which must be non-negative.
        """
        pass
    
    @abstractmethod
    def scale(self, x: T, alpha: float) -> float:
        """
        Evaluate the seminorm of a scaled input.
        
        This method should satisfy scalar homogeneity: p(αx) = |α|p(x)
        
        Parameters
        ----------
        x : T
            The input to evaluate the seminorm on.
        alpha : float
            The scaling factor.
            
        Returns
        -------
        float
            The seminorm value of the scaled input.
        """
        pass
    
    @abstractmethod
    def triangle_inequality(self, x: T, y: T) -> bool:
        """
        Verify that the triangle inequality holds for the given inputs.
        
        This method should check if p(x + y) <= p(x) + p(y).
        
        Parameters
        ----------
        x : T
            First input.
        y : T
            Second input.
            
        Returns
        -------
        bool
            True if the triangle inequality holds, False otherwise.
        """
        pass
    
    @abstractmethod
    def is_zero(self, x: T, tolerance: float = 1e-10) -> bool:
        """
        Check if the seminorm evaluates to zero (within a tolerance).
        
        Parameters
        ----------
        x : T
            The input to check.
        tolerance : float, optional
            The numerical tolerance for considering a value as zero.
            
        Returns
        -------
        bool
            True if the seminorm of x is zero (within tolerance), False otherwise.
        """
        pass
    
    @abstractmethod
    def is_definite(self) -> bool:
        """
        Check if this seminorm is actually a norm (i.e., it has the definiteness property).
        
        A seminorm is definite if p(x) = 0 implies x = 0.
        
        Returns
        -------
        bool
            True if the seminorm is definite (and thus a norm), False otherwise.
        """
        pass