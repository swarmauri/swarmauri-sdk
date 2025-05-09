import logging
from typing import Optional
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.norms.IUseInnerProduct import IUseInnerProduct
from swarmauri_core.norms.IInnerProduct import IInnerProduct

logger = logging.getLogger("UseInnerProductMixin")

@ComponentBase.register_model()
class UseInnerProductMixin(IUseInnerProduct, ComponentBase):
    """
    Base mixin class for components that utilize inner product geometry.

    This class provides a base implementation for components that require an inner product
    structure. It includes basic setup for maintaining an inner product reference and
    provides abstract method stubs that should be implemented by concrete subclasses.

    Attributes:
        inner_product: Reference to an IInnerProduct instance
        resource: Optional resource identifier
    """
    
    resource: Optional[str] = Field(default=ResourceTypes.NORM.value)
    
    def __init__(self, inner_product: IInnerProduct = None):
        """
        Initialize the UseInnerProductMixin instance.

        Args:
            inner_product: Optional IInnerProduct instance to be used internally
        """
        super().__init__()
        if inner_product is not None:
            if not isinstance(inner_product, IInnerProduct):
                raise TypeError("inner_product must be an instance of IInnerProduct")
            self.inner_product = inner_product
        else:
            self.inner_product = None
    
    def check_angle_between_vectors(self, a: object, b: object) -> float:
        """
        Calculate and return the angle between two vectors using the inner product.

        Args:
            a: First vector
            b: Second vector

        Returns:
            The angle in radians between the two vectors.

        Raises:
            NotImplementedError: Always raised as this is an abstract method
        """
        logger.debug("check_angle_between_vectors called")
        raise NotImplementedError("Method check_angle_between_vectors must be implemented in subclass")

    def check_verify_orthogonality(self, a: object, b: object) -> bool:
        """
        Check if two vectors are orthogonal using the inner product.

        Args:
            a: First vector
            b: Second vector

        Returns:
            True if the vectors are orthogonal, False otherwise.

        Raises:
            NotImplementedError: Always raised as this is an abstract method
        """
        logger.debug("check_verify_orthogonality called")
        raise NotImplementedError("Method check_verify_orthogonality must be implemented in subclass")

    def check_xy_project(self, vector: object, basis: object) -> object:
        """
        Project a vector onto a specified basis using the inner product.

        Args:
            vector: Vector to be projected
            basis: Basis vectors for projection

        Returns:
            Projected vector onto the specified basis.

        Raises:
            NotImplementedError: Always raised as this is an abstract method
        """
        logger.debug("check_xy_project called")
        raise NotImplementedError("Method check_xy_project must be implemented in subclass")

    def check_verify_parallelogram_law(self, a: object, b: object) -> bool:
        """
        Verify the parallelogram law using the inner product.

        Args:
            a: First vector
            b: Second vector

        Returns:
            True if the parallelogram law holds, False otherwise.

        Raises:
            NotImplementedError: Always raised as this is an abstract method
        """
        logger.debug("check_verify_parallelogram_law called")
        raise NotImplementedError("Method check_verify_parallelogram_law must be implemented in subclass")