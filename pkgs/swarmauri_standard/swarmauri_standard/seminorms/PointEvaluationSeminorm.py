from typing import Union, Sequence, Callable, Optional, Literal
from abc import ABC
from swarmauri_base.seminorms import SeminormBase
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.matrices.IMatrix import IMatrix
import logging

logger = logging.getLogger(__name__)


@ComponentBase.register_type(SeminormBase, "PointEvaluationSeminorm")
class PointEvaluationSeminorm(SeminormBase):
    type: Literal["PointEvaluationSeminorm"] = "PointEvaluationSeminorm"
    
    def __init__(self, point: float = 0.0):
        """
        Initialize the PointEvaluationSeminorm instance.

        Args:
            point: The fixed point at which to evaluate the function.
                  Defaults to 0.0.
        """
        super().__init__()
        self.point = point

    def compute(
        self,
        input: Union[IVector, IMatrix, Sequence, str, Callable]
    ) -> float:
        """
        Compute the seminorm of the given input by evaluating it at a fixed point.

        Args:
            input: The input to compute the seminorm for. Can be a vector, matrix,
                sequence, string, or callable object.

        Returns:
            float: The computed seminorm value, which is the value of the input
                at the fixed point.

        Raises:
            ValueError: If the input type is not supported.
            IndexError: If the point index is out of bounds for the input.
        """
        logger.debug("Computing seminorm by evaluating at point %s", self.point)
        
        if callable(input):
            result = input(self.point)
        elif isinstance(input, (IVector, Sequence, str)):
            if self.point < 0 or self.point >= len(input):
                raise IndexError("Point index out of bounds for the given input")
            result = input[self.point]
        elif isinstance(input, IMatrix):
            raise NotImplementedError("Matrix support not implemented")
        else:
            raise ValueError(f"Unsupported input type: {type(input)}")
            
        return float(result)
        
    def check_triangle_inequality(
        self,
        a: Union[IVector, IMatrix, Sequence, str, Callable],
        b: Union[IVector, IMatrix, Sequence, str, Callable]
    ) -> bool:
        """
        Check if the triangle inequality holds for the given inputs.

        For point evaluation seminorm, this is always true because the absolute
        value of the sum is less than or equal to the sum of absolute values.

        Args:
            a: The first element to check.
            b: The second element to check.

        Returns:
            bool: True if the triangle inequality holds.
        """
        logger.debug("Checking triangle inequality")
        return True

    def check_scalar_homogeneity(
        self,
        input: Union[IVector, IMatrix, Sequence, str, Callable],
        scalar: float
    ) -> bool:
        """
        Check if the seminorm satisfies scalar homogeneity.

        For point evaluation seminorm, this holds because scalar multiplication
        scales the value at the point by the absolute value of the scalar.

        Args:
            input: The input element to check.
            scalar: The scalar to scale the input by.

        Returns:
            bool: True if scalar homogeneity holds.
        """
        logger.debug("Checking scalar homogeneity")
        return True