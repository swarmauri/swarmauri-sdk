from asyncio import Semaphore
from logging import getLogger
from typing import Any, Callable

from fastapi import Request
from pydantic import PrivateAttr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.middlewares.MiddlewareBase import MiddlewareBase

logger = getLogger(__name__)


@ComponentBase.register_type(MiddlewareBase, "BulkheadMiddleware")
class BulkheadMiddleware(MiddlewareBase):
    """Bulkhead middleware implementation to control concurrency isolation.

    This middleware restricts the maximum number of concurrent requests to prevent
    resource overload. It uses a semaphore to manage the concurrency level.

    Attributes:
        max_concurrency: int = 10  # Maximum number of concurrent requests
        _semaphore: Semaphore  # Semaphore for concurrency control
    """

    max_concurrency: int = 10
    _semaphore: Semaphore = PrivateAttr()

    def __init__(self, max_concurrency: int = 10, **kwargs: Any) -> None:
        """Initializes the BulkheadMiddleware with specified concurrency limit.

        Args:
            max_concurrency: Maximum number of concurrent requests allowed
            logger: Optional logger instance to use for logging
        """
        super().__init__(**kwargs)
        if max_concurrency <= 0:
            raise ValueError("max_concurrency must be greater than 0")
        self.max_concurrency = max_concurrency
        self._semaphore = Semaphore(max_concurrency)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Any]
    ) -> Any:
        """Dispatches the request while controlling concurrency using a semaphore.

        This method uses a semaphore to limit the number of concurrent requests.
        If the maximum concurrency is reached, the request will wait until a slot
        becomes available.

        Args:
            request: The incoming request object to be processed
            call_next: A callable that invokes the next middleware
                in the chain

        Returns:
            The response object after all middlewares have processed
            the request
        """
        try:
            # Acquire the semaphore to manage concurrency
            await self._semaphore.acquire()
            logger.debug(f"Processing request: {request}")

            # Define an async wrapper for the call_next function
            async def _call_next(request: Request):
                return await call_next(request)

            # Process the request and return the response
            response = await _call_next(request)
            return response

        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            raise

        finally:
            # Release the semaphore after processing
            self._semaphore.release()
            logger.debug("Released semaphore slot")

    async def close(self) -> None:
        """Closes any resources held by the middleware.

        This method is currently a placeholder but can be extended
        to release any additional resources if needed.
        """
        logger.debug("Closing BulkheadMiddleware resources")
