from typing import Union, Optional
import numpy as np
import logging
from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.norms.IUseInnerProduct import IUseInnerProduct
from swarmauri_core.inner_products.IInnerProduct import IInnerProduct
from swarmauri_core.vectors.IVector import IVector

logger = logging.getLogger(__name__)


@ComponentBase.register_model()
class UseInnerProductMixin(IUseInnerProduct, ComponentBase):
    """
    A mixin class providing base implementation for components that use inner product geometry.

    This class serves as a foundation for other components that require inner product functionality.
    It implements the IUseInnerProduct interface by providing method signatures and basic structure,
    while delegating the actual implementation to subclasses through abstract methods.

    The class maintains a reference to an IInnerProduct implementation and provides logging functionality.
    All methods raise NotImplementedError as this class is intended to be extended by concrete implementations.
    """

    resource: Optional[str] = Field(default=ResourceTypes.NORM.value)

    def __init__(self, inner_product: IInnerProduct):
        """
        Initialize the UseInnerProductMixin with an inner product implementation.

        Args:
            inner_product: An instance of IInnerProduct that will be used for inner product operations
        """
        self.inner_product = inner_product

    def check_angle_between_vectors(self, a: Union[IVector, np.ndarray], b: Union[IVector, np.ndarray]) -> float:
        """
        Computes and verifies the angle between two vectors using the inner product.

        Args:
            a: The first vector
            b: The second vector

        Returns:
            float: The angle in radians between the two vectors

        Raises:
            NotImplementedError: This method must be implemented in a subclass
        """
        logger.debug("Calculating angle between vectors")
        raise NotImplementedError("Method must be implemented in a subclass")

    def check_verify_orthogonality(self, a: Union[IVector, np.ndarray], b: Union[IVector, np.ndarray]) -> None:
        """
        Verifies that two vectors are orthogonal using the inner product.

        Args:
            a: The first vector
            b: The second vector

        Raises:
            NotImplementedError: This method must be implemented in a subclass
        """
        logger.debug("Checking orthogonality")
        raise NotImplementedError("Method must be implemented in a subclass")

    def check_xy_project(self, a: Union[IVector, np.ndarray], b: Union[IVector, np.ndarray]) -> Union[IVector, np.ndarray]:
        """
        Projects vector a onto vector b using the inner product.

        Args:
            a: The vector to project
            b: The vector onto which to project

        Returns:
            Union[IVector, np.ndarray]: The projection of a onto b

        Raises:
            NotImplementedError: This method must be implemented in a subclass
        """
        logger.debug("Projecting vector a onto vector b")
        raise NotImplementedError("Method must be implemented in a subclass")

    def check_verify_parallelogram_law(self, a: Union[IVector, np.ndarray], b: Union[IVector, np.ndarray]) -> None:
        """
        Verifies the parallelogram law using the inner product.

        The parallelogram law states that:
        ||a + b||^2 + ||a - b||^2 = 2(||a||^2 + ||b||^2)

        Args:
            a: The first vector
            b: The second vector

        Raises:
            NotImplementedError: This method must be implemented in a subclass
        """
        logger.debug("Verifying parallelogram law")
        raise NotImplementedError("Method must be implemented in a subclass")