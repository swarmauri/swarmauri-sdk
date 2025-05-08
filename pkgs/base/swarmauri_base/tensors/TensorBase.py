from typing import Optional, Tuple, Union, List, Any, TypeVar
import logging
from pydantic import Field
import numpy as np

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.tensors.ITensor import ITensor

# Set up logging
logger = logging.getLogger(__name__)

@ComponentBase.register_model()
class TensorBase(ITensor, ComponentBase):
    """
    Base implementation of the ITensor interface for tensor operations.
    
    This class provides a concrete implementation of the ITensor interface,
    serving as a foundation for tensor manipulations including reshaping,
    contraction, and broadcasting operations.
    
    Attributes
    ----------
    resource : Optional[str]
        The resource type of this tensor component.
    """
    resource: Optional[str] = Field(default=ResourceTypes.TENSOR.value)
    
    def shape(self) -> Tuple[int, ...]:
        """
        Get the shape of the tensor.
        
        Returns
        -------
        Tuple[int, ...]
            The dimensions of the tensor.
        
        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses.
        """
        raise NotImplementedError("shape() method must be implemented by subclasses")
    
    def ndim(self) -> int:
        """
        Get the number of dimensions of the tensor.
        
        Returns
        -------
        int
            The number of dimensions.
        
        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses.
        """
        raise NotImplementedError("ndim() method must be implemented by subclasses")
    
    def dtype(self) -> Any:
        """
        Get the data type of the tensor elements.
        
        Returns
        -------
        Any
            The data type of the tensor.
        
        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses.
        """
        raise NotImplementedError("dtype() method must be implemented by subclasses")
    
    def device(self) -> str:
        """
        Get the device where the tensor is stored.
        
        Returns
        -------
        str
            The device information (e.g., "cpu", "cuda:0").
        
        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses.
        """
        raise NotImplementedError("device() method must be implemented by subclasses")
    
    def reshape(self, shape: Tuple[int, ...]) -> 'TensorBase':
        """
        Reshape the tensor to the specified dimensions.
        
        Parameters
        ----------
        shape : Tuple[int, ...]
            The new shape for the tensor.
            
        Returns
        -------
        TensorBase
            A new tensor with the specified shape.
            
        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses.
        """
        raise NotImplementedError("reshape() method must be implemented by subclasses")
    
    def transpose(self, dims: Optional[Tuple[int, ...]] = None) -> 'TensorBase':
        """
        Transpose the tensor dimensions.
        
        Parameters
        ----------
        dims : Optional[Tuple[int, ...]], default=None
            The desired ordering of dimensions.
            If None, reverse the dimensions.
            
        Returns
        -------
        TensorBase
            A new tensor with transposed dimensions.
        
        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses.
        """
        raise NotImplementedError("transpose() method must be implemented by subclasses")
    
    def contract(self, other: 'TensorBase', dims_self: Tuple[int, ...], dims_other: Tuple[int, ...]) -> 'TensorBase':
        """
        Contract this tensor with another tensor along specified dimensions.
        
        Parameters
        ----------
        other : TensorBase
            The tensor to contract with.
        dims_self : Tuple[int, ...]
            The dimensions of this tensor to contract.
        dims_other : Tuple[int, ...]
            The dimensions of the other tensor to contract.
            
        Returns
        -------
        TensorBase
            The result of the contraction.
            
        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses.
        """
        raise NotImplementedError("contract() method must be implemented by subclasses")
    
    def to_numpy(self) -> Any:
        """
        Convert the tensor to a numpy array.
        
        Returns
        -------
        Any
            The tensor as a numpy array.
        
        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses.
        """
        raise NotImplementedError("to_numpy() method must be implemented by subclasses")
    
    def clone(self) -> 'TensorBase':
        """
        Create a deep copy of the tensor.
        
        Returns
        -------
        TensorBase
            A new tensor with the same data.
        
        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses.
        """
        raise NotImplementedError("clone() method must be implemented by subclasses")
    
    def __add__(self, other: Union['TensorBase', float, int]) -> 'TensorBase':
        """
        Add another tensor or scalar to this tensor.
        
        Parameters
        ----------
        other : Union[TensorBase, float, int]
            The tensor or scalar to add.
            
        Returns
        -------
        TensorBase
            The result of the addition.
        
        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses.
        """
        raise NotImplementedError("__add__() method must be implemented by subclasses")
    
    def __mul__(self, other: Union['TensorBase', float, int]) -> 'TensorBase':
        """
        Multiply this tensor by another tensor or scalar.
        
        Parameters
        ----------
        other : Union[TensorBase, float, int]
            The tensor or scalar to multiply by.
            
        Returns
        -------
        TensorBase
            The result of the multiplication.
        
        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses.
        """
        raise NotImplementedError("__mul__() method must be implemented by subclasses")
    
    def __getitem__(self, key: Any) -> Union['TensorBase', float, int]:
        """
        Get a slice or element of the tensor.
        
        Parameters
        ----------
        key : Any
            The indexing key.
            
        Returns
        -------
        Union[TensorBase, float, int]
            The selected portion of the tensor.
        
        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses.
        """
        raise NotImplementedError("__getitem__() method must be implemented by subclasses")
    
    def __setitem__(self, key: Any, value: Union['TensorBase', float, int]) -> None:
        """
        Set a slice or element of the tensor.
        
        Parameters
        ----------
        key : Any
            The indexing key.
        value : Union[TensorBase, float, int]
            The value to set.
        
        Raises
        ------
        NotImplementedError
            This method must be implemented by subclasses.
        """
        raise NotImplementedError("__setitem__() method must be implemented by subclasses")