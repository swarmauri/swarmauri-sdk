from typing import Tuple, Union, List, Optional
import logging
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.tensors.ITensor import ITensor

logger = logging.getLogger(__name__)

@ComponentBase.register_model()
class TensorBase(ITensor, ComponentBase):
    """
    Base implementation of the ITensor interface. This class provides a foundation
    for implementing tensor operations, including basic structure and logging
    functionality. All methods raise NotImplementedError and are intended to be
    overridden in derived classes.

    Attributes:
        shape (Tuple[int, ...]): The shape of the tensor
        dtype (type): The data type of the elements in the tensor
        resource (Optional[str]): Resource identifier for the tensor
    """
    resource: Optional[str] = Field(default=ResourceTypes.TENSOR.value)

    def __init__(self):
        """
        Initializes the TensorBase instance.
        """
        super().__init__()
        logger.debug("Initialized TensorBase")

    def shape(self) -> Tuple[int, ...]:
        """
        Returns the shape of the tensor as a tuple of integers.
        
        Returns:
            Tuple[int, ...]: Shape of the tensor
        
        Raises:
            NotImplementedError: This method is not implemented in the base class
        """
        logger.debug("Getting tensor shape")
        raise NotImplementedError("Method not implemented in base class")

    def reshape(self, new_shape: Tuple[int, ...]) -> ITensor:
        """
        Reshapes the tensor to a new shape.
        
        Args:
            new_shape: New shape as a tuple of integers
            
        Returns:
            Reshaped tensor
        
        Raises:
            NotImplementedError: This method is not implemented in the base class
        """
        logger.debug(f"Reshaping tensor to {new_shape}")
        raise NotImplementedError("Method not implemented in base class")

    def dtype(self) -> type:
        """
        Returns the data type of the elements in the tensor.
        
        Returns:
            type: Data type of the tensor elements
        
        Raises:
            NotImplementedError: This method is not implemented in the base class
        """
        logger.debug("Getting tensor dtype")
        raise NotImplementedError("Method not implemented in base class")

    def __getitem__(self, index: Union[Tuple[int, ...], Tuple[slice, ...], int, slice]) -> Union[float, IVector, ITensor]:
        """
        Gets elements using tensor indices or slices.
        
        Args:
            index: Tuple of indices or slices for multi-dimensional access
            
        Returns:
            Union[float, IVector, ITensor]: Element, vector, or subtensor based on index
        
        Raises:
            NotImplementedError: This method is not implemented in the base class
        """
        logger.debug(f"Getting item with index {index}")
        raise NotImplementedError("Method not implemented in base class")

    def __setitem__(self, index: Union[Tuple[int, ...], Tuple[slice, ...], int, slice], value: Union[float, IVector, ITensor]):
        """
        Sets elements using tensor indices or slices.
        
        Args:
            index: Tuple of indices or slices for multi-dimensional access
            value: Value or values to set at the specified index
        
        Raises:
            NotImplementedError: This method is not implemented in the base class
        """
        logger.debug(f"Setting item at index {index} with value {value}")
        raise NotImplementedError("Method not implemented in base class")

    def tolist(self) -> Union[List[float], List[List[float]], ...]:
        """
        Converts the tensor to a nested list structure.
        
        Returns:
            Union[List[float], List[List[float]], ...]: Tensor as a nested list
        
        Raises:
            NotImplementedError: This method is not implemented in the base class
        """
        logger.debug("Converting tensor to list")
        raise NotImplementedError("Method not implemented in base class")

    def __add__(self, other: Union[float, int, ITensor]) -> ITensor:
        """
        Element-wise addition with another tensor or scalar.
        
        Args:
            other: Another tensor or scalar to add
            
        Returns:
            ITensor: Resulting tensor after addition
        
        Raises:
            NotImplementedError: This method is not implemented in the base class
        """
        logger.debug(f"Performing tensor addition with {other}")
        raise NotImplementedError("Method not implemented in base class")

    def __sub__(self, other: Union[float, int, ITensor]) -> ITensor:
        """
        Element-wise subtraction with another tensor or scalar.
        
        Args:
            other: Another tensor or scalar to subtract
            
        Returns:
            ITensor: Resulting tensor after subtraction
        
        Raises:
            NotImplementedError: This method is not implemented in the base class
        """
        logger.debug(f"Performing tensor subtraction with {other}")
        raise NotImplementedError("Method not implemented in base class")

    def __mul__(self, other: Union[float, int, ITensor]) -> ITensor:
        """
        Element-wise multiplication with another tensor or scalar.
        
        Args:
            other: Another tensor or scalar to multiply
            
        Returns:
            ITensor: Resulting tensor after multiplication
        
        Raises:
            NotImplementedError: This method is not implemented in the base class
        """
        logger.debug(f"Performing tensor multiplication with {other}")
        raise NotImplementedError("Method not implemented in base class")

    def __truediv__(self, other: Union[float, int, ITensor]) -> ITensor:
        """
        Element-wise division with another tensor or scalar.
        
        Args:
            other: Another tensor or scalar to divide by
            
        Returns:
            ITensor: Resulting tensor after division
        
        Raises:
            NotImplementedError: This method is not implemented in the base class
        """
        logger.debug(f"Performing tensor division by {other}")
        raise NotImplementedError("Method not implemented in base class")

    def transpose(self) -> ITensor:
        """
        Transposes the tensor.
        
        Returns:
            ITensor: Transposed tensor
        
        Raises:
            NotImplementedError: This method is not implemented in the base class
        """
        logger.debug("Transposing tensor")
        raise NotImplementedError("Method not implemented in base class")

    def broadcast(self, new_shape: Tuple[int, ...]) -> ITensor:
        """
        Broadcasts the tensor to a new shape.
        
        Args:
            new_shape: New shape as a tuple of integers
            
        Returns:
            ITensor: Broadcasted tensor
        
        Raises:
            NotImplementedError: This method is not implemented in the base class
        """
        logger.debug(f"Broadcasting tensor to {new_shape}")
        raise NotImplementedError("Method not implemented in base class")

    def __str__(self) -> str:
        """
        Returns a string representation of the tensor.
        
        Returns:
            str: String representation of the tensor
        """
        logger.debug("Getting string representation of tensor")
        return f"TensorBase(shape={self.shape()}, dtype={self.dtype()})"

    def __repr__(self) -> str:
        """
        Returns the official string representation of the tensor.
        
        Returns:
            str: Official string representation
        """
        logger.debug("Getting official string representation of tensor")
        return self.__str__()