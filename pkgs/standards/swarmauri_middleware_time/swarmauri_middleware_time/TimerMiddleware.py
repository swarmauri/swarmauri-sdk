import logging
import time
from typing import Any, Callable

from fastapi import HTTPException, Request
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.middlewares.MiddlewareBase import MiddlewareBase

_LOGGER = logging.getLogger(__name__)


@ComponentBase.register_type(MiddlewareBase, "TimerMiddleware")
class TimerMiddleware(MiddlewareBase, ComponentBase):
    """Middleware that tracks the time taken for each request.

    This middleware measures the latency of each request by recording
    the start time and calculating the duration after the response
    is received. It logs the time taken for each request and adds
    timing headers to the response.

    Attributes:
        type: Literal["TimerMiddleware"] = "TimerMiddleware"
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Any]
    ) -> Any:
        """Dispatches the request to the next middleware in the chain while tracking time.

        This method measures the time taken for processing the request
        from start to finish. It logs the start time, processes the
        request, measures the total time taken, and logs the result.

        Args:
            request: The incoming request object to be processed
            call_next: A callable that invokes the next middleware
                in the chain

        Returns:
            The response object after all middlewares have processed
            the request with timing headers added

        Raises:
            HTTPException: If any error occurs during processing
        """

        # Record the start time of the request
        start_time = time.time()
        _LOGGER.info(
            f"Request {request.method} {request.url.path} started at {start_time}"
        )

        try:
            # Process the request with the next middleware
            response = await call_next(request)
        except Exception as e:
            # Log any exceptions that occur during processing
            _LOGGER.error(
                f"Error processing request {request.method} {request.url.path}: {str(e)}"
            )
            raise HTTPException(status_code=500, detail=str(e))

        # Calculate the total time taken
        total_time = time.time() - start_time
        _LOGGER.info(
            f"Request {request.method} {request.url.path} completed in {total_time:.4f} seconds"
        )

        # Fix: Add timing headers to the response
        if hasattr(response, "headers"):
            response.headers["X-Request-Duration"] = f"{total_time:.4f}"
            response.headers["X-Request-Start-Time"] = str(start_time)

        return response
