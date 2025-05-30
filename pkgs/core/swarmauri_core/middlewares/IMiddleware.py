from abc import ABC, abstractmethod

"""Middleware interface module.
Defines the core interface for all middleware implementations.
"""


class IMiddleware(ABC):
    """Abstract base class for all middleware implementations.

    All middleware classes must inherit from this interface and implement
    the :meth:`dispatch` method. Middleware classes are responsible for
    processing requests and passing them to the next middleware in the chain.
    """

    @abstractmethod
    def dispatch(self, request, call_next):
        """Dispatches the request to the next middleware in the chain.

        Args:
            request: The incoming request object to be processed.
            call_next: A callable that invokes the next middleware
                in the chain.

        Returns:
            The response object after all middlewares have processed
            the request.
        """
        pass
