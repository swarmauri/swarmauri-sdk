from abc import abstractmethod
from typing import Any, Callable, Optional

from swarmauri_core.middlewares.IMiddleware import IMiddleware

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class MiddlewareBase(IMiddleware, ComponentBase):
    """Base class for all middleware implementations.

    This class provides a skeleton implementation of the IMiddleware interface.
    All middleware classes should inherit from this base class and implement
    the required methods. The dispatch method is left unimplemented and
    must be overridden in subclasses.

    Attributes:
        resource: Optional[str] = "middleware"  # Default resource type for middlewares
    """

    resource: Optional[str] = ResourceTypes.MIDDLEWARE.value

    @abstractmethod
    def dispatch(self, request: Any, call_next: Callable[[Any], Any]) -> Any:
        """Dispatches the request to the next middleware in the chain.

        This method must be implemented by all subclasses. It is responsible
        for processing the request and passing it to the next middleware
        in the chain using the call_next parameter.

        Args:
            request: The incoming request object to be processed.
            call_next: A callable that invokes the next middleware
                in the chain.

        Returns:
            The response object after all middlewares have processed
            the request.

        Raises:
            NotImplementedError: This method is not implemented and must
                be overridden in subclasses.
        """
        raise NotImplementedError("Must be implemented by subclasses")
