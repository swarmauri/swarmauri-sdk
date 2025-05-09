from typing import TypeVar, Union, Iterable, Optional
import logging
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.seminorms import SeminormBase

logger = logging.getLogger(__name__)

T = TypeVar('T', list, tuple, Iterable, str)
S = TypeVar('S', int, slice, Iterable[int])

@ComponentBase.register_type(SeminormBase, "PartialSumSeminorm")
class PartialSumSeminorm(SeminormBase):
    """
    A seminorm that computes the sum over a specified subset of the input vector.

    This class implements a seminorm that evaluates the sum of elements in the input
    vector over a specified range or collection of indices. The indices can be specified
    as a slice, a list, or a tuple of integers.

    Attributes:
        indices: Union[Iterable[int], slice]
            The indices or slice specifying which elements to sum.
    """
    resource: str = ResourceTypes.SEMINORM.value
    """
    The resource type identifier for seminorm components.
    """
    
    def __init__(self, indices: Optional[Union[Iterable[int], slice]] = None):
        """
        Initializes the PartialSumSeminorm with the specified indices.

        Args:
            indices: Optional[Union[Iterable[int], slice]]
                The indices or slice specifying which elements to sum. If None,
                defaults to summing all elements (equivalent to slice(None)).
                
        Raises:
            ValueError: If indices is not a valid iterable or slice
        """
        super().__init__()
        if indices is None:
            indices = slice(None)
        if isinstance(indices, slice):
            self.indices = indices
        elif isinstance(indices, Iterable):
            try:
                self.indices = tuple(sorted(int(i) for i in indices))
            except TypeError:
                raise ValueError("Indices must be an iterable of integers or a slice")
        else:
            raise ValueError("Indices must be an iterable or slice")
        
        logger.debug(f"Initialized PartialSumSeminorm with indices: {self.indices}")
    
    def compute(self, input: T) -> float:
        """
        Computes the seminorm value by summing the specified elements of the input.

        Args:
            input: T
                The input vector to compute the seminorm for.
                
        Returns:
            float: The computed seminorm value
            
        Raises:
            ValueError: If input is not an iterable
        """
        try:
            input_list = list(input)
        except TypeError:
            logger.error("Input is not an iterable type")
            raise ValueError("Input must be an iterable type")
            
        if isinstance(self.indices, slice):
            selected_elements = input_list[self.indices]
        else:
            selected_elements = [input_list[i] for i in self.indices]
            
        try:
            return sum(float(e) for e in selected_elements)
        except ValueError as e:
            logger.error(f"Error summing elements: {str(e)}")
            raise
    
    def check_triangle_inequality(self, a: T, b: T) -> bool:
        """
        Checks if the triangle inequality holds for this seminorm.

        For partial sum seminorm, the triangle inequality holds because:
        sum_a_b = sum_a + sum_b, where sum_a is the sum of selected elements
        of a and sum_b is the sum of selected elements of b.

        Args:
            a: T
                The first input vector
            b: T
                The second input vector
                
        Returns:
            bool: True if the triangle inequality holds, False otherwise
        """
        return True
    
    def check_scalar_homogeneity(self, a: T, scalar: float) -> bool:
        """
        Checks if the seminorm is homogeneous of degree 1.

        For partial sum seminorm, this holds because:
        sum(scalar * a) = scalar * sum(a)

        Args:
            a: T
                The input vector to check
            scalar: float
                The scalar to test homogeneity with
                
        Returns:
            bool: True if scalar homogeneity holds, False otherwise
        """
        return True

# Example usage
if __name__ == "__main__":
    # Example 1: Sum the first two elements
    pss = PartialSumSeminorm(indices=[0, 1])
    result = pss.compute([1, 2, 3, 4])
    print(f"Partial sum: {result}")
    
    # Example 2: Sum all elements using slice
    pssSlice = PartialSumSeminorm(slice(None))
    resultSlice = pssSlice.compute([5, 6, 7])
    print(f"Total sum: {resultSlice}")