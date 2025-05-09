from typing import Optional, Union, Sequence, List, Any
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.pseudometrics.IPseudometric import IPseudometric
import logging

logger = logging.getLogger(__name__)

@ComponentBase.register_model()
class PseudometricBase(IPseudometric, ComponentBase):
    """
    Base implementation for the IPseudometric interface.

    This class provides a concrete base implementation that raises NotImplementedError
    for all abstract methods that must be implemented by subclasses. It includes
    basic logging functionality and ensures compliance with the pseudometric
    properties interface.

    Inherits:
        IPseudometric: Interface defining the pseudometric properties
        ComponentBase: Base class for components in the system
    """
    resource: Optional[str] = Field(default=ResourceTypes.PSEUDOMETRIC.value)
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def distance(self, x: Union[IVector, IMatrix, Sequence, str, Callable],
                  y: Union[IVector, IMatrix, Sequence, str, Callable]) -> float:
        """
        Computes the pseudometric distance between two elements.

        Args:
            x: Union[IVector, IMatrix, Sequence, str, Callable]
                The first element to compute distance between
            y: Union[IVector, IMatrix, Sequence, str, Callable]
                The second element to compute distance between

        Returns:
            float: The computed pseudometric distance

        Raises:
            NotImplementedError: This method must be implemented in a subclass
        """
        self.logger.error("distance method not implemented in subclass")
        raise NotImplementedError("distance method must be implemented")

    def distances(self, xs: Sequence[Union[IVector, IMatrix, Sequence, str, Callable]],
                  ys: Sequence[Union[IVector, IMatrix, Sequence, str, Callable]]) -> List[float]:
        """
        Computes pairwise pseudometric distances between two sequences of elements.

        Args:
            xs: Sequence[Union[IVector, IMatrix, Sequence, str, Callable]]
                The first sequence of elements
            ys: Sequence[Union[IVector, IMatrix, Sequence, str, Callable]]
                The second sequence of elements

        Returns:
            List[float]: A list of computed pseudometric distances

        Raises:
            NotImplementedError: This method must be implemented in a subclass
        """
        self.logger.error("distances method not implemented in subclass")
        raise NotImplementedError("distances method must be implemented")