from abc import ABC, abstractmethod
from typing import Union
import numpy as np
import logging

from swarmauri_core.inner_products.IInnerProduct import IInnerProduct
from swarmauri_core.vectors.IVector import IVector


logger = logging.getLogger(__name__)


class IUseInnerProduct(ABC):
    """
    Abstract interface marking components that use inner product geometry.

    This interface defines the contract for components that depend on inner product
    structures. It provides methods for verifying key geometric properties that
    rely on an inner product implementation.

    The interface requires a compatible IInnerProduct implementation to be injected
    or defined. All methods are abstract and must be implemented by concrete subclasses.
    """

    def __init__(self, inner_product: IInnerProduct):
        """
        Initializes the IUseInnerProduct instance with a specific inner product implementation.

        Args:
            inner_product: An instance of IInnerProduct that will be used for inner product operations
        """
        self.inner_product = inner_product

    @abstractmethod
    def check_angle_between_vectors(self, a: Union[IVector, np.ndarray], b: Union[IVector, np.ndarray]) -> float:
        """
        Computes and verifies the angle between two vectors using the inner product.

        Args:
            a: The first vector
            b: The second vector

        Returns:
            float: The angle in radians between the two vectors

        Raises:
            ValueError: If the angle calculation fails or inputs are invalid
        """
        logger.debug("Calculating angle between vectors")
        # Compute the dot product using the inner product
        dot_product = self.inner_product.compute(a, b)
        # Compute magnitudes
        mag_a = self.inner_product.compute(a, a) ** 0.5
        mag_b = self.inner_product.compute(b, b) ** 0.5

        if mag_a == 0 or mag_b == 0:
            raise ValueError("Cannot compute angle with zero vectors")

        cosine_similarity = dot_product / (mag_a * mag_b)
        angle = np.arccos(cosine_similarity)

        return angle

    @abstractmethod
    def check_verify_orthogonality(self, a: Union[IVector, np.ndarray], b: Union[IVector, np.ndarray]) -> None:
        """
        Verifies that two vectors are orthogonal using the inner product.

        Args:
            a: The first vector
            b: The second vector

        Raises:
            ValueError: If the vectors are not orthogonal
        """
        logger.debug("Checking orthogonality")
        inner_product = self.inner_product.compute(a, b)
        if not np.isclose(inner_product, 0.0):
            raise ValueError("Vectors are not orthogonal")

    @abstractmethod
    def check_xy_project(self, a: Union[IVector, np.ndarray], b: Union[IVector, np.ndarray]) -> Union[IVector, np.ndarray]:
        """
        Projects vector a onto vector b using the inner product.

        Args:
            a: The vector to project
            b: The vector onto which to project

        Returns:
            Union[IVector, np.ndarray]: The projection of a onto b

        Raises:
            ValueError: If the projection fails
        """
        logger.debug("Projecting vector a onto vector b")
        dot_product = self.inner_product.compute(a, b)
        mag_b_squared = self.inner_product.compute(b, b)

        if mag_b_squared == 0:
            raise ValueError("Cannot project onto zero vector")

        projection_scalar = dot_product / mag_b_squared
        projection = projection_scalar * b

        return projection

    @abstractmethod
    def check_verify_parallelogram_law(self, a: Union[IVector, np.ndarray], b: Union[IVector, np.ndarray]) -> None:
        """
        Verifies the parallelogram law using the inner product.

        The parallelogram law states that:
        ||a + b||^2 + ||a - b||^2 = 2(||a||^2 + ||b||^2)

        Args:
            a: The first vector
            b: The second vector

        Raises:
            ValueError: If the parallelogram law is not satisfied
        """
        logger.debug("Verifying parallelogram law")
        a_plus_b = self.inner_product.compute(a + b, a + b)
        a_minus_b = self.inner_product.compute(a - b, a - b)
        left_side = a_plus_b + a_minus_b

        mag_a_squared = self.inner_product.compute(a, a)
        mag_b_squared = self.inner_product.compute(b, b)
        right_side = 2 * (mag_a_squared + mag_b_squared)

        if not np.isclose(left_side, right_side):
            raise ValueError("Parallelogram law not satisfied")