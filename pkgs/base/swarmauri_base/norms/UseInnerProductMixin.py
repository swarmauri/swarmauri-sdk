from typing import Type, Optional
from abc import ABC
import logging
from swarmauri_core.inner_products.IInnerProduct import IInnerProduct
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.norms.IUseInnerProduct import IUseInnerProduct

logger = logging.getLogger(__name__)


@ComponentBase.register_model()
class UseInnerProductMixin(IUseInnerProduct, ComponentBase):
    """Mixin class providing base implementation for components using inner product geometry.

    This class serves as a foundation for components that require inner product operations.
    It provides a reference to an inner product implementation and defines abstract methods
    that must be implemented by concrete subclasses.

    Args:
        inner_product: Implementation of IInnerProduct to be used for operations
    """
    resource: Optional[str] = ResourceTypes.NORM.value

    def __init__(self, inner_product: Type[IInnerProduct]):
        """Initialize the mixin with an inner product implementation.

        Args:
            inner_product: A class implementing IInnerProduct interface

        Raises:
            NotImplementedError: If any abstract method is called before being implemented
        """
        super().__init__()
        self.inner_product = inner_product()
        logger.info("Initialized UseInnerProductMixin with inner product: %s", self.inner_product.__class__.__name__)

    def check_angle_between_vectors(self, x: IInnerProduct, y: IInnerProduct) -> float:
        """Compute the angle between two vectors using the inner product.

        Args:
            x: First vector
            y: Second vector

        Returns:
            Angle in radians between the two vectors

        Raises:
            NotImplementedError: This method must be implemented by subclass
        """
        logger.info("Attempting to compute angle between vectors")
        raise NotImplementedError("Method must be implemented by subclass")

    def check_verify_orthogonality(self, x: IInnerProduct, y: IInnerProduct) -> bool:
        """Verify if two vectors are orthogonal using the inner product.

        Args:
            x: First vector
            y: Second vector

        Returns:
            True if vectors are orthogonal, False otherwise

        Raises:
            NotImplementedError: This method must be implemented by subclass
        """
        logger.info("Attempting to verify orthogonality between vectors")
        raise NotImplementedError("Method must be implemented by subclass")

    def check_xy_project(self, x: IInnerProduct, y: IInnerProduct) -> IInnerProduct:
        """Project vector x onto vector y using the inner product.

        Args:
            x: Vector to project
            y: Vector onto which to project

        Returns:
            Projection of x onto y

        Raises:
            NotImplementedError: This method must be implemented by subclass
        """
        logger.info("Attempting to project vector x onto vector y")
        raise NotImplementedError("Method must be implemented by subclass")

    def check_verify_parallelogram_law(self, x: IInnerProduct, y: IInnerProduct) -> bool:
        """Verify the parallelogram law using the inner product.

        The parallelogram law states that:
        ||x + y||² + ||x - y||² = 2||x||² + 2||y||²

        Args:
            x: First vector
            y: Second vector

        Returns:
            True if the parallelogram law holds, False otherwise

        Raises:
            NotImplementedError: This method must be implemented by subclass
        """
        logger.info("Attempting to verify parallelogram law")
        raise NotImplementedError("Method must be implemented by subclass")