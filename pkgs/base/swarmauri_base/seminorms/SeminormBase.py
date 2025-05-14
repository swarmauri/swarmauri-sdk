from abc import ABC
import logging
from typing import TypeVar, Union, Callable, Sequence, Literal
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.seminorms.ISeminorm import ISeminorm, InputType

# Configure logging
logger = logging.getLogger(__name__)

T = TypeVar('T', bound=Union[int, float, complex])


class SeminormBase(ISeminorm, ABC):
    """
    Base class providing tools for evaluating seminorms in partial vector spaces.
    
    This class provides reusable logic for defining seminorms and implements
    the ISeminorm interface. Concrete implementations should override the
    abstract methods to provide specific seminorm behavior.
    
    A seminorm is a function that assigns a non-negative length or size to vectors
    in a vector space, satisfying the properties of non-negativity, triangle inequality,
    and scalar homogeneity.
    """
    
    def compute(self, x: InputType) -> float:
        """
        Compute the seminorm of the input.
        
        Parameters
        ----------
        x : InputType
            The input to compute the seminorm for. Can be a vector, matrix,
            sequence, string, or callable.
            
        Returns
        -------
        float
            The seminorm value (non-negative real number)
            
        Raises
        ------
        TypeError
            If the input type is not supported
        ValueError
            If the computation cannot be performed on the given input
        NotImplementedError
            This method must be implemented by subclasses
        """
        logger.debug(f"Computing seminorm for input of type {type(x)}")
        raise NotImplementedError("compute method must be implemented by subclasses")
    
    def check_triangle_inequality(self, x: InputType, y: InputType) -> bool:
        """
        Check if the triangle inequality property holds for the given inputs.
        
        The triangle inequality states that:
        ||x + y|| ≤ ||x|| + ||y||
        
        Parameters
        ----------
        x : InputType
            First input to check
        y : InputType
            Second input to check
            
        Returns
        -------
        bool
            True if the triangle inequality holds, False otherwise
            
        Raises
        ------
        TypeError
            If the input types are not supported or compatible
        ValueError
            If the check cannot be performed on the given inputs
        NotImplementedError
            This method must be implemented by subclasses
        """
        logger.debug(f"Checking triangle inequality for inputs of types {type(x)} and {type(y)}")
        raise NotImplementedError("check_triangle_inequality method must be implemented by subclasses")
    
    def check_scalar_homogeneity(self, x: InputType, alpha: T) -> bool:
        """
        Check if the scalar homogeneity property holds for the given input and scalar.
        
        The scalar homogeneity states that:
        ||αx|| = |α|·||x||
        
        Parameters
        ----------
        x : InputType
            The input to check
        alpha : T
            The scalar to multiply by
            
        Returns
        -------
        bool
            True if scalar homogeneity holds, False otherwise
            
        Raises
        ------
        TypeError
            If the input type is not supported
        ValueError
            If the check cannot be performed on the given input
        NotImplementedError
            This method must be implemented by subclasses
        """
        logger.debug(f"Checking scalar homogeneity for input of type {type(x)} with scalar {alpha}")
        raise NotImplementedError("check_scalar_homogeneity method must be implemented by subclasses")