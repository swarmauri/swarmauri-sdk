from typing import Any, List, Sequence, Literal, Union, TypeVar, Optional
import logging
import numpy as np
from pydantic import Field, validator

from swarmauri_base.metrics.MetricBase import MetricBase
from swarmauri_core.ComponentBase import ComponentBase

# Configure logger
logger = logging.getLogger(__name__)

# Type variable for sequence types
T = TypeVar('T')

@ComponentBase.register_type(MetricBase, "HammingMetric")
class HammingMetric(MetricBase):
    """
    Implementation of the Hamming distance metric.
    
    The Hamming distance between two sequences of equal length is the number of positions
    at which the corresponding elements are different. It is particularly useful for
    measuring the distance between binary strings, categorical vectors, or any sequences
    where the notion of equality between elements is well-defined.
    
    Attributes
    ----------
    type : Literal["HammingMetric"]
        The type identifier for this metric
    normalize : bool
        If True, the distance is normalized by the sequence length to range [0, 1]
    """
    type: Literal["HammingMetric"] = "HammingMetric"
    normalize: bool = Field(default=False, description="Whether to normalize the distance to [0, 1]")
    
    def distance(self, x: Union[Sequence[T], np.ndarray], y: Union[Sequence[T], np.ndarray]) -> float:
        """
        Calculate the Hamming distance between two sequences.
        
        The Hamming distance counts the number of positions at which the corresponding
        elements in the two sequences are different.
        
        Parameters
        ----------
        x : Union[Sequence[T], np.ndarray]
            First sequence
        y : Union[Sequence[T], np.ndarray]
            Second sequence
            
        Returns
        -------
        float
            The Hamming distance between x and y. If normalize=True, the result is
            divided by the sequence length to get a value in the range [0, 1].
            
        Raises
        ------
        ValueError
            If the sequences have different lengths
        """
        # Convert inputs to numpy arrays for efficient processing
        x_array = np.asarray(x)
        y_array = np.asarray(y)
        
        # Check if sequences have equal length
        if len(x_array) != len(y_array):
            error_msg = f"Sequences must have equal length, got {len(x_array)} and {len(y_array)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Count positions where elements differ
        # The != operation creates a boolean array, and sum() counts the True values
        mismatches = np.sum(x_array != y_array)
        
        # Normalize if requested
        if self.normalize and len(x_array) > 0:
            return float(mismatches) / len(x_array)
        
        return float(mismatches)
    
    def are_identical(self, x: Union[Sequence[T], np.ndarray], y: Union[Sequence[T], np.ndarray]) -> bool:
        """
        Check if two sequences are identical according to the Hamming metric.
        
        Two sequences are identical if their Hamming distance is zero,
        meaning they have the same elements in the same positions.
        
        Parameters
        ----------
        x : Union[Sequence[T], np.ndarray]
            First sequence
        y : Union[Sequence[T], np.ndarray]
            Second sequence
            
        Returns
        -------
        bool
            True if the sequences are identical (distance is zero), False otherwise
            
        Raises
        ------
        ValueError
            If the sequences have different lengths
        """
        try:
            # Two sequences are identical if their Hamming distance is zero
            return self.distance(x, y) == 0
        except ValueError as e:
            # If sequences have different lengths, they cannot be identical
            logger.warning(f"Cannot determine if sequences are identical: {str(e)}")
            return False
    
    @validator('normalize')
    def validate_normalize(cls, v: bool) -> bool:
        """
        Validate the normalize parameter.
        
        Parameters
        ----------
        v : bool
            The normalize value to validate
            
        Returns
        -------
        bool
            The validated normalize value
        """
        if not isinstance(v, bool):
            logger.warning(f"normalize must be a boolean, got {type(v)}. Converting to bool.")
            return bool(v)
        return v
    
    def batch_distance(self, x: Union[Sequence[T], np.ndarray], 
                       points: List[Union[Sequence[T], np.ndarray]]) -> List[float]:
        """
        Calculate the Hamming distance between one sequence and multiple other sequences.
        
        This is an optimized version for computing distances to multiple points.
        
        Parameters
        ----------
        x : Union[Sequence[T], np.ndarray]
            Reference sequence
        points : List[Union[Sequence[T], np.ndarray]]
            List of sequences to compare against the reference
            
        Returns
        -------
        List[float]
            List of Hamming distances between x and each sequence in points
            
        Raises
        ------
        ValueError
            If any sequence has a different length from x
        """
        return [self.distance(x, y) for y in points]