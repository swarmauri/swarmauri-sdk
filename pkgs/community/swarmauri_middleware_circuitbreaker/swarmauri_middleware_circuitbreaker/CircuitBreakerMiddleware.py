import logging
from typing import Any, Callable, Optional

from fastapi import Request
from pybreaker import CircuitBreaker
from swarmauri_base.middlewares.MiddlewareBase import MiddlewareBase

logger = logging.getLogger(__name__)


class CircuitBreakerMiddleware(MiddlewareBase):
    """Circuit Breaker Middleware implementation using pybreaker.

    This middleware protects downstream services by monitoring failed requests.
    When the number of consecutive failures exceeds the specified threshold,
    the circuit breaker opens and prevents further requests until the circuit
    is reset or becomes half-open again.

    Attributes:
        circuit_breaker: The CircuitBreaker instance that manages the state
        fail_max: Maximum number of consecutive failures before breaking the circuit
        reset_timeout: Time in seconds before attempting to close the circuit
        half_open_wait_time: Time to wait before allowing a single request
            to test if the service is healthy again (half-open state)
    """

    fail_max: int = 5
    reset_timeout: int = 30
    half_open_wait_time: int = 10
    circuit_breaker: Optional[CircuitBreaker] = None

    def __init__(
        self,
        fail_max: int = 5,
        reset_timeout: int = 30,
        half_open_wait_time: int = 10,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.fail_max = fail_max
        self.reset_timeout = reset_timeout
        self.half_open_wait_time = half_open_wait_time
        self.circuit_breaker = CircuitBreaker(
            fail_max=fail_max,
            reset_timeout=reset_timeout,
        )

    def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> Any:
        """Dispatches the request to the next middleware with circuit breaking functionality.

        
        Args:
            request: The incoming request object
            call_next: The next middleware or route handler in the chain

        Returns:
            The response from the next middleware or route handler

        Raises:
            HTTPException: If the circuit is open and the request should be failed
        """
        try:
            # Use circuit_breaker context manager to monitor for failures
            with self.circuit_breaker:
                response = call_next(request)
                return response

        except Exception as e:
            # Log the failure and let the circuit_breaker handle the state
            logger.error("Request failed, circuit breaker will monitor", exc_info=True)
            raise e

    def __call__(self, request: Request) -> Any:
        """Makes the middleware instance callable.

        Args:
            request: The incoming request object

        Returns:
            The response from the middleware chain
        """
        return self.dispatch(request)

    def on_circuit_open(self):
        """Called when the circuit opens due to excessive failures."""
        logger.warning("Circuit opened: Excessive failures detected")

    def on_circuit_close(self):
        """Called when the circuit is closed again after successful requests."""
        logger.info("Circuit closed: Service is healthy again")

    def on_circuit_half_open(self):
        """Called when the circuit enters half-open state."""
        logger.info("Circuit half-open: Waiting for test request to determine health")
