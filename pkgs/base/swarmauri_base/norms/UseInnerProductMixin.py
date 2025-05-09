from typing import Union
import logging
from swarmauri_core.norms.IUseInnerProduct import IUseInnerProduct
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.inner_products.IInnerProduct import IInnerProduct

# Define logger
logger = logging.getLogger(__name__)

@ComponentBase.register_model()
class UseInnerProductMixin(ComponentBase, IUseInnerProduct):
    """
    A mixin class providing basic functionality for components that utilize inner product geometry.
    This class should be inherited by components that require inner product operations.
    It provides a base implementation that must be extended with concrete geometric logic.
    """
    
    def __init__(self, inner_product: IInnerProduct):
        """
        Initializes the UseInnerProductMixin with an inner product implementation.

        Args:
            inner_product: An instance of IInnerProduct to be used for geometric operations
        """
        self.inner_product = inner_product
        super().__init__()

    def compute_angle(self, a: Union[IVector, Matrix], b: Union[IVector, Matrix]) -> float:
        """
        Computes the angle between two vectors using the inner product.
        
        Args:
            a: First vector
            b: Second vector
            
        Returns:
            float: The angle between the two vectors in radians
        """
        logger.info("Computing angle between vectors")
        raise NotImplementedError("Must implement compute_angle in subclass")

    def compute_projection(self, a: Union[IVector, Matrix], b: Union[IVector, Matrix]) -> Union[IVector, Matrix]:
        """
        Projects vector a onto vector b using the inner product.
        
        Args:
            a: Vector to project
            b: Vector onto which to project
            
        Returns:
            Union[IVector, Matrix]: Projection of a onto b
        """
        logger.info("Projecting vector a onto vector b")
        raise NotImplementedError("Must implement compute_projection in subclass")

    def compute_orthogonality(self, a: Union[IVector, Matrix], b: Union[IVector, Matrix]) -> bool:
        """
        Checks if two vectors are orthogonal using the inner product.
        
        Args:
            a: First vector
            b: Second vector
            
        Returns:
            bool: True if vectors are orthogonal, False otherwise
        """
        logger.info("Checking orthogonality")
        raise NotImplementedError("Must implement compute_orthogonality in subclass")

    def compute_parallelogram_law(self, a: Union[IVector, Matrix], b: Union[IVector, Matrix]) -> bool:
        """
        Verifies the parallelogram law using the inner product.
        
        Args:
            a: First vector
            b: Second vector
            
        Returns:
            bool: True if parallelogram law holds, False otherwise
        """
        logger.info("Checking parallelogram law")
        raise NotImplementedError("Must implement compute_parallelogram_law in subclass")