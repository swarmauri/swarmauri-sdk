from abc import ABC, abstractmethod
from typing import (
    Tuple,
    List,
    TypeVar,
    Union,
    Iterator,
    Sequence,
    Protocol,
)

T = TypeVar("T", bound=Union[int, float, complex])
Shape = Tuple[int, ...]
Index = Union[int, slice, Tuple[Union[int, slice], ...]]


class SupportsArray(Protocol):
    """Protocol for objects that support array-like behavior."""

    @abstractmethod
    def __array__(self) -> "IMatrix": ...


# Define a type for IVector to avoid circular imports
IVector = TypeVar("IVector")


class IMatrix(ABC):
    """
    Interface abstraction for matrix operations.

    This interface defines the standard operations and properties that all matrix
    implementations must support, providing a common API for linear operators and
    2D structures.
    """

    @abstractmethod
    def __getitem__(self, key: Index) -> Union["IMatrix", IVector, T]:
        """
        Get an element, row, column, or submatrix using indexing/slicing.

        Parameters
        ----------
        key : Index
            The index or slice to access

        Returns
        -------
        Union[IMatrix, IVector, T]
            The requested element, vector, or submatrix

        Raises
        ------
        IndexError
            If the index is out of bounds
        """
        pass

    @abstractmethod
    def __setitem__(
        self, key: Index, value: Union["IMatrix", IVector, T, Sequence[Sequence[T]]]
    ) -> None:
        """
        Set an element, row, column, or submatrix using indexing/slicing.

        Parameters
        ----------
        key : Index
            The index or slice to modify
        value : Union[IMatrix, IVector, T, Sequence[Sequence[T]]]
            The value to set

        Raises
        ------
        IndexError
            If the index is out of bounds
        ValueError
            If the value has incompatible dimensions
        """
        pass

    @property
    @abstractmethod
    def shape(self) -> Tuple[int, int]:
        """
        Get the shape of the matrix.

        Returns
        -------
        Tuple[int, int]
            The dimensions of the matrix as (rows, columns)
        """
        pass

    @abstractmethod
    def reshape(self, shape: Tuple[int, int]) -> "IMatrix":
        """
        Reshape the matrix to the specified dimensions.

        Parameters
        ----------
        shape : Tuple[int, int]
            The new dimensions as (rows, columns)

        Returns
        -------
        IMatrix
            A reshaped matrix

        Raises
        ------
        ValueError
            If the new shape is incompatible with the total number of elements
        """
        pass

    @property
    @abstractmethod
    def dtype(self) -> type:
        """
        Get the data type of the matrix elements.

        Returns
        -------
        type
            The data type of the elements
        """
        pass

    @abstractmethod
    def tolist(self) -> List[List[T]]:
        """
        Convert the matrix to a nested list.

        Returns
        -------
        List[List[T]]
            A list of lists representing the matrix
        """
        pass

    @abstractmethod
    def row(self, index: int) -> IVector:
        """
        Get a specific row of the matrix.

        Parameters
        ----------
        index : int
            The row index

        Returns
        -------
        IVector
            The specified row as a vector

        Raises
        ------
        IndexError
            If the index is out of bounds
        """
        pass

    @abstractmethod
    def column(self, index: int) -> IVector:
        """
        Get a specific column of the matrix.

        Parameters
        ----------
        index : int
            The column index

        Returns
        -------
        IVector
            The specified column as a vector

        Raises
        ------
        IndexError
            If the index is out of bounds
        """
        pass

    @abstractmethod
    def __add__(self, other: Union["IMatrix", T]) -> "IMatrix":
        """
        Add another matrix or scalar to this matrix.

        Parameters
        ----------
        other : Union[IMatrix, T]
            The matrix or scalar to add

        Returns
        -------
        IMatrix
            The resulting matrix

        Raises
        ------
        ValueError
            If the matrices have incompatible dimensions
        """
        pass

    @abstractmethod
    def __sub__(self, other: Union["IMatrix", T]) -> "IMatrix":
        """
        Subtract another matrix or scalar from this matrix.

        Parameters
        ----------
        other : Union[IMatrix, T]
            The matrix or scalar to subtract

        Returns
        -------
        IMatrix
            The resulting matrix

        Raises
        ------
        ValueError
            If the matrices have incompatible dimensions
        """
        pass

    @abstractmethod
    def __mul__(self, other: Union["IMatrix", T]) -> "IMatrix":
        """
        Element-wise multiply this matrix by another matrix or scalar.

        Parameters
        ----------
        other : Union[IMatrix, T]
            The matrix or scalar to multiply by

        Returns
        -------
        IMatrix
            The resulting matrix

        Raises
        ------
        ValueError
            If the matrices have incompatible dimensions
        """
        pass

    @abstractmethod
    def __matmul__(self, other: "IMatrix") -> "IMatrix":
        """
        Perform matrix multiplication with another matrix.

        Parameters
        ----------
        other : IMatrix
            The matrix to multiply with

        Returns
        -------
        IMatrix
            The resulting matrix

        Raises
        ------
        ValueError
            If the matrices have incompatible dimensions for multiplication
        """
        pass

    @abstractmethod
    def __truediv__(self, other: Union["IMatrix", T]) -> "IMatrix":
        """
        Element-wise divide this matrix by another matrix or scalar.

        Parameters
        ----------
        other : Union[IMatrix, T]
            The matrix or scalar to divide by

        Returns
        -------
        IMatrix
            The resulting matrix

        Raises
        ------
        ValueError
            If the matrices have incompatible dimensions
        ZeroDivisionError
            If dividing by zero
        """
        pass

    @abstractmethod
    def __neg__(self) -> "IMatrix":
        """
        Negate all elements in the matrix.

        Returns
        -------
        IMatrix
            The negated matrix
        """
        pass

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        """
        Check if this matrix is equal to another matrix.

        Parameters
        ----------
        other : object
            The object to compare with

        Returns
        -------
        bool
            True if the matrices are equal, False otherwise
        """
        pass

    @abstractmethod
    def __iter__(self) -> Iterator[IVector]:
        """
        Iterate over the rows of the matrix.

        Returns
        -------
        Iterator[IVector]
            An iterator yielding rows as vectors
        """
        pass

    @abstractmethod
    def transpose(self) -> "IMatrix":
        """
        Transpose the matrix.

        Returns
        -------
        IMatrix
            The transposed matrix
        """
        pass

    @abstractmethod
    def __array__(self) -> "IMatrix":
        """
        Support for numpy's array protocol.

        Returns
        -------
        IMatrix
            The matrix itself or a compatible representation
        """
        pass
