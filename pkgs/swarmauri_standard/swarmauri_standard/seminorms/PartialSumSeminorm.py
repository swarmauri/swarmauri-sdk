import logging
import numpy as np
from typing import Any, TypeVar, Generic, Optional, Literal, List, Union
from pydantic import Field, validator

from swarmauri_base.seminorms.SeminormBase import SeminormBase
from swarmauri_core.ComponentBase import ComponentBase

# Set up logging
logger = logging.getLogger(__name__)

# Type variable for generic typing
T = TypeVar('T')

@ComponentBase.register_model()
class PartialSumSeminorm(SeminormBase):
    """
    Seminorm computed via summing only part of the vector.
    
    This seminorm evaluates a norm on a partial segment of the input,
    ignoring the rest. It is useful for cases where only certain 
    components of a vector are relevant for the norm calculation.
    
    Attributes
    ----------
    type : Literal["PartialSumSeminorm"]
        The type identifier for this seminorm.
    start_index : int
        The starting index of the segment to consider (inclusive).
    end_index : Optional[int]
        The ending index of the segment to consider (exclusive).
        If None, the end of the vector is used.
    """
    
    type: Literal["PartialSumSeminorm"] = "PartialSumSeminorm"
    start_index: int = Field(0, description="Starting index (inclusive) of the segment to consider")
    end_index: Optional[int] = Field(None, description="Ending index (exclusive) of the segment to consider")
    
    @validator('start_index')
    def validate_start_index(cls, v):
        """Validate that start_index is non-negative."""
        if v < 0:
            raise ValueError("start_index must be non-negative")
        return v
    
    @validator('end_index')
    def validate_end_index(cls, v, values):
        """Validate that end_index is greater than start_index if provided."""
        if v is not None:
            if 'start_index' in values and v <= values['start_index']:
                raise ValueError("end_index must be greater than start_index")
        return v
    
    def evaluate(self, x: Union[List[float], np.ndarray]) -> float:
        """
        Evaluate the seminorm by summing absolute values of a segment of the input vector.
        
        Parameters
        ----------
        x : Union[List[float], np.ndarray]
            The input vector to evaluate the seminorm on.
            
        Returns
        -------
        float
            The seminorm value, which is the sum of absolute values of the specified segment.
            
        Raises
        ------
        ValueError
            If the input is not a list or numpy array, or if indices are out of bounds.
        """
        logger.debug("Evaluating PartialSumSeminorm on input of type %s", type(x).__name__)
        
        # Convert to numpy array if it's a list
        if isinstance(x, list):
            x = np.array(x)
        elif not isinstance(x, np.ndarray):
            raise ValueError(f"Input must be a list or numpy array, got {type(x).__name__}")
        
        # Determine end index if not provided
        end = self.end_index if self.end_index is not None else len(x)
        
        # Validate indices
        if self.start_index >= len(x):
            raise ValueError(f"start_index {self.start_index} is out of bounds for input of length {len(x)}")
        if end > len(x):
            raise ValueError(f"end_index {end} is out of bounds for input of length {len(x)}")
        
        # Extract the segment and compute the sum of absolute values
        segment = x[self.start_index:end]
        result = np.sum(np.abs(segment))
        
        logger.debug("PartialSumSeminorm result: %f", result)
        return float(result)
    
    def scale(self, x: Union[List[float], np.ndarray], alpha: float) -> float:
        """
        Evaluate the seminorm of a scaled input.
        
        This method satisfies scalar homogeneity: p(αx) = |α|p(x)
        
        Parameters
        ----------
        x : Union[List[float], np.ndarray]
            The input vector to evaluate the seminorm on.
        alpha : float
            The scaling factor.
            
        Returns
        -------
        float
            The seminorm value of the scaled input.
        """
        logger.debug("Scaling input by factor %f", alpha)
        return abs(alpha) * self.evaluate(x)
    
    def triangle_inequality(self, x: Union[List[float], np.ndarray], y: Union[List[float], np.ndarray]) -> bool:
        """
        Verify that the triangle inequality holds for the given inputs.
        
        Checks if p(x + y) <= p(x) + p(y).
        
        Parameters
        ----------
        x : Union[List[float], np.ndarray]
            First input vector.
        y : Union[List[float], np.ndarray]
            Second input vector.
            
        Returns
        -------
        bool
            True if the triangle inequality holds, False otherwise.
            
        Raises
        ------
        ValueError
            If inputs have different lengths or are not compatible types.
        """
        logger.debug("Checking triangle inequality for PartialSumSeminorm")
        
        # Convert to numpy arrays if they're lists
        if isinstance(x, list):
            x = np.array(x)
        if isinstance(y, list):
            y = np.array(y)
        
        # Check if inputs have the same length
        if len(x) != len(y):
            raise ValueError(f"Inputs must have the same length, got {len(x)} and {len(y)}")
        
        # Calculate the sum vector
        sum_vector = x + y
        
        # Evaluate the seminorm on all vectors
        p_x = self.evaluate(x)
        p_y = self.evaluate(y)
        p_sum = self.evaluate(sum_vector)
        
        # Check the triangle inequality
        result = p_sum <= p_x + p_y + 1e-10  # Add small tolerance for floating-point errors
        
        logger.debug("Triangle inequality check result: %s", result)
        return result
    
    def is_zero(self, x: Union[List[float], np.ndarray], tolerance: float = 1e-10) -> bool:
        """
        Check if the seminorm evaluates to zero (within a tolerance).
        
        Parameters
        ----------
        x : Union[List[float], np.ndarray]
            The input vector to check.
        tolerance : float, optional
            The numerical tolerance for considering a value as zero.
            
        Returns
        -------
        bool
            True if the seminorm of x is zero (within tolerance), False otherwise.
        """
        logger.debug("Checking if seminorm is zero with tolerance %f", tolerance)
        return self.evaluate(x) < tolerance
    
    def is_definite(self) -> bool:
        """
        Check if this seminorm is actually a norm (i.e., it has the definiteness property).
        
        A partial sum seminorm is not definite unless it considers the entire vector.
        
        Returns
        -------
        bool
            True if the seminorm is definite (and thus a norm), False otherwise.
        """
        logger.debug("Checking if PartialSumSeminorm is definite")
        # This seminorm is only definite if it considers the entire vector
        # Since we can't know the length of vectors it will be applied to,
        # we conservatively return False
        return False