import logging
from typing import Any, Callable

from fastapi import Request
from pybreaker import CircuitBreaker
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.middlewares.MiddlewareBase import MiddlewareBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(MiddlewareBase, "CircuitBreakerMiddleware")
class CircuitBreakerMiddleware(MiddlewareBase):
    """Circuit Breaker Middleware with async support and PyBreaker state storage."""

    fail_max: int = 5
    reset_timeout: int = 30
    half_open_wait_time: int = 10

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

        cb = CircuitBreaker(
            fail_max=fail_max,
            reset_timeout=reset_timeout,
        )
        cb.open = False
        self.circuit_breaker = cb

        self._half_open_used = False

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Any],
    ) -> Any:
        cb = self.circuit_breaker

        # if open, allow one test call
        if cb.open:
            if not self._half_open_used:
                self._half_open_used = True
                CircuitBreaker.half_open(cb)
                logger.info(
                    "Circuit half-open: Waiting for test request to determine health"
                )
            else:
                from fastapi import HTTPException

                raise HTTPException(status_code=429, detail="Circuit is open")

        try:
            response = await call_next(request)
        except Exception:
            if not cb.open:
                cb._state_storage.increment_counter()
                if cb._state_storage.counter > self.fail_max:
                    CircuitBreaker.open(cb)
                    cb.open = True
                    logger.warning("Circuit opened: Excessive failures detected")
            raise
        else:
            if cb.open:
                CircuitBreaker.close(cb)
                cb.open = False
                self._half_open_used = False
                cb._state_storage.reset_counter()
                logger.info("Circuit closed: Service is healthy again")
            else:
                cb._state_storage.reset_counter()
            return response

    def __call__(self, request: Request) -> Any:
        return self.dispatch(request)
