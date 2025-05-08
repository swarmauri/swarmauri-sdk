import logging
from typing import Optional
from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.inner_product_users.IUseInnerProduct import IUseInnerProduct, IInnerProduct

# Set up logging
logger = logging.getLogger(__name__)


@ComponentBase.register_model()
class UseInnerProductBase(IUseInnerProduct, ComponentBase):
    """
    Base class for structures dependent on inner products.
    
    This class provides a concrete implementation of the IUseInnerProduct interface,
    serving as a base for components that require inner product operations.
    It maintains a reference to an inner product object which can be used for
    various geometric calculations.
    """
    resource: Optional[str] = Field(default=ResourceTypes.INNER_PRODUCT_USER.value)
    _inner_product: Optional[IInnerProduct] = None
    
    def __init__(self, **data):
        """
        Initialize the UseInnerProductBase.
        
        Parameters
        ----------
        **data
            Additional keyword arguments to pass to the parent class
        """
        super().__init__(**data)
        logger.debug(f"Initialized {self.__class__.__name__}")
    
    def get_inner_product(self) -> Optional[IInnerProduct]:
        """
        Get the inner product implementation used by this component.
        
        Returns
        -------
        Optional[IInnerProduct]
            The inner product implementation or None if not set
        """
        if self._inner_product is None and self.requires_inner_product():
            logger.warning(f"{self.__class__.__name__} requires an inner product but none is set")
        return self._inner_product
    
    def set_inner_product(self, inner_product: IInnerProduct) -> None:
        """
        Set the inner product implementation to be used by this component.
        
        Parameters
        ----------
        inner_product : IInnerProduct
            The inner product implementation to use
        """
        logger.debug(f"Setting inner product for {self.__class__.__name__}")
        self._inner_product = inner_product
    
    def requires_inner_product(self) -> bool:
        """
        Check if this component requires an inner product to function.
        
        This is a base implementation that should be overridden by subclasses
        to indicate their specific requirements.
        
        Returns
        -------
        bool
            True if an inner product is required, False otherwise
        
        Raises
        ------
        NotImplementedError
            When the method is not implemented by a subclass
        """
        raise NotImplementedError(
            f"The method 'requires_inner_product' must be implemented by subclasses of {self.__class__.__name__}"
        )