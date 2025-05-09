from abc import ABC, abstractmethod
from typing import Union
import logging

# Define logger
logger = logging.getLogger(__name__)

# Type alias for vector types
IVector = "IVector"

# Type alias for matrix types
Matrix = "Matrix"

from swarmauri_core.inner_products.IInnerProduct import IInnerProduct

class IUseInnerProduct(ABC):
    """
    Abstract interface marking components that use inner product geometry.
    This interface defines methods that rely on an inner product structure for geometric operations.
    Implementations should provide concrete geometric functionality using the inner product.
    """

    def __init__(self, inner_product: IInnerProduct):
        """
        Initializes the IUseInnerProduct implementation with a specific inner product.

        Args:
            inner_product: An instance of IInnerProduct to be used for geometric operations
        """
        self.inner_product = inner_product

    def check_angle(self, a: Union[IVector, Matrix], b: Union[IVector, Matrix]) -> float:
        """
        Computes and checks the angle between two vectors using the inner product.

        Args:
            a: First vector
            b: Second vector

        Returns:
            float: The angle between the two vectors in radians
        """
        logger.info("Computing angle between vectors")
        inner = self.inner_product.compute(a, b)
        magnitude_a = self.inner_product.compute(a, a) ** 0.5
        magnitude_b = self.inner_product.compute(b, b) ** 0.5
        
        if magnitude_a == 0 or magnitude_b == 0:
            logger.warning("Cannot compute angle with zero magnitude vector")
            return 0.0
            
        cosine_similarity = inner / (magnitude_a * magnitude_b)
        angle = self.inner_product.compute(cosine_similarity, 1).real  # Assuming compute handles inverse cosine
        
        logger.info(f"Angle between vectors: {angle}")
        return angle

    def check_verify_orthogonality(self, a: Union[IVector, Matrix], b: Union[IVector, Matrix]) -> bool:
        """
        Verifies if two vectors are orthogonal using the inner product.

        Args:
            a: First vector
            b: Second vector

        Returns:
            bool: True if vectors are orthogonal, False otherwise
        """
        logger.info("Checking orthogonality")
        inner = self.inner_product.compute(a, b)
        
        if inner == 0:
            logger.info("Vectors are orthogonal")
            return True
        else:
            logger.info("Vectors are not orthogonal")
            return False

    def check_xy_project(self, a: Union[IVector, Matrix], b: Union[IVector, Matrix]) -> Union[IVector, Matrix]:
        """
        Projects vector a onto vector b using the inner product.

        Args:
            a: Vector to project
            b: Vector onto which to project

        Returns:
            Union[IVector, Matrix]: Projection of a onto b
        """
        logger.info("Projecting vector a onto vector b")
        inner = self.inner_product.compute(a, b)
        norm_b = self.inner_product.compute(b, b)
        
        if norm_b == 0:
            logger.warning("Cannot project onto zero vector")
            return a
            
        projection = (inner / norm_b) * b
        logger.info("Projection computed successfully")
        return projection

    def check_verify_parallelogram_law(self, a: Union[IVector, Matrix], b: Union[IVector, Matrix]) -> bool:
        """
        Verifies the parallelogram law using the inner product.

        Args:
            a: First vector
            b: Second vector

        Returns:
            bool: True if parallelogram law holds, False otherwise
        """
        logger.info("Checking parallelogram law")
        norm_a_plus_b = self.inner_product.compute(a + b, a + b)
        norm_a_minus_b = self.inner_product.compute(a - b, a - b)
        sum_of_squares = self.inner_product.compute(a, a) + self.inner_product.compute(b, b)
        
        if norm_a_plus_b + norm_a_minus_b == 2 * sum_of_squares:
            logger.info("Parallelogram law holds")
            return True
        else:
            logger.info("Parallelogram law does not hold")
            return False