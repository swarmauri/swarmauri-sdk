from abc import ABC, abstractmethod
from typing import Optional, Tuple, Union, List, Any, TypeVar, Generic
import logging

# Set up logging
logger = logging.getLogger(__name__)

T = TypeVar('T', bound='ITensor')

class ITensor(ABC):
    """
    Core interface for tensorial algebra components.
    
    This abstract base class defines the essential operations and properties
    that all tensor implementations must support. It provides a standard
    interface for tensor manipulation regardless of the underlying implementation.
    """
    
    @abstractmethod
    def shape(self) -> Tuple[int, ...]:
        """
        Get the shape of the tensor.
        
        Returns
        -------
        Tuple[int, ...]
            The dimensions of the tensor.
        """
        pass
    
    @abstractmethod
    def ndim(self) -> int:
        """
        Get the number of dimensions of the tensor.
        
        Returns
        -------
        int
            The number of dimensions.
        """
        pass
    
    @abstractmethod
    def dtype(self) -> Any:
        """
        Get the data type of the tensor elements.
        
        Returns
        -------
        Any
            The data type of the tensor.
        """
        pass
    
    @abstractmethod
    def device(self) -> str:
        """
        Get the device where the tensor is stored.
        
        Returns
        -------
        str
            The device information (e.g., "cpu", "cuda:0").
        """
        pass
    
    @abstractmethod
    def reshape(self: T, shape: Tuple[int, ...]) -> T:
        """
        Reshape the tensor to the specified dimensions.
        
        Parameters
        ----------
        shape : Tuple[int, ...]
            The new shape for the tensor.
            
        Returns
        -------
        T
            A new tensor with the specified shape.
            
        Raises
        ------
        ValueError
            If the new shape is not compatible with the tensor's size.
        """
        pass
    
    @abstractmethod
    def transpose(self: T, dims: Optional[Tuple[int, ...]] = None) -> T:
        """
        Transpose the tensor dimensions.
        
        Parameters
        ----------
        dims : Optional[Tuple[int, ...]], default=None
            The desired ordering of dimensions.
            If None, reverse the dimensions.
            
        Returns
        -------
        T
            A new tensor with transposed dimensions.
        """
        pass
    
    @abstractmethod
    def contract(self: T, other: T, dims_self: Tuple[int, ...], dims_other: Tuple[int, ...]) -> T:
        """
        Contract this tensor with another tensor along specified dimensions.
        
        Parameters
        ----------
        other : T
            The tensor to contract with.
        dims_self : Tuple[int, ...]
            The dimensions of this tensor to contract.
        dims_other : Tuple[int, ...]
            The dimensions of the other tensor to contract.
            
        Returns
        -------
        T
            The result of the contraction.
            
        Raises
        ------
        ValueError
            If the dimensions to contract don't match in size.
        """
        pass
    
    @abstractmethod
    def to_numpy(self) -> Any:
        """
        Convert the tensor to a numpy array.
        
        Returns
        -------
        Any
            The tensor as a numpy array.
        """
        pass
    
    @abstractmethod
    def clone(self: T) -> T:
        """
        Create a deep copy of the tensor.
        
        Returns
        -------
        T
            A new tensor with the same data.
        """
        pass
    
    @abstractmethod
    def __add__(self: T, other: Union[T, float, int]) -> T:
        """
        Add another tensor or scalar to this tensor.
        
        Parameters
        ----------
        other : Union[T, float, int]
            The tensor or scalar to add.
            
        Returns
        -------
        T
            The result of the addition.
        """
        pass
    
    @abstractmethod
    def __mul__(self: T, other: Union[T, float, int]) -> T:
        """
        Multiply this tensor by another tensor or scalar.
        
        Parameters
        ----------
        other : Union[T, float, int]
            The tensor or scalar to multiply by.
            
        Returns
        -------
        T
            The result of the multiplication.
        """
        pass
    
    @abstractmethod
    def __getitem__(self: T, key: Any) -> Union[T, float, int]:
        """
        Get a slice or element of the tensor.
        
        Parameters
        ----------
        key : Any
            The indexing key.
            
        Returns
        -------
        Union[T, float, int]
            The selected portion of the tensor.
        """
        pass
    
    @abstractmethod
    def __setitem__(self: T, key: Any, value: Union[T, float, int]) -> None:
        """
        Set a slice or element of the tensor.
        
        Parameters
        ----------
        key : Any
            The indexing key.
        value : Union[T, float, int]
            The value to set.
        """
        pass