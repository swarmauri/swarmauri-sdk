#         swarmauri_middleware_ratepolicy/RetryPolicyMiddleware.py
import logging
import time
from typing import Any, Callable

from swarmauri_base.middlewares.MiddlewareBase import MiddlewareBase


class RetryPolicyMiddleware(MiddlewareBase):
    def __init__(self, max_retries: int = 3, initial_wait: float = 1):
        super().__init__()
        self.max_retries = max(0, max_retries)
        self.initial_wait = max(0, initial_wait)

    def dispatch(self, request: Any, call_next: Callable[[Any], Any]) -> Any:
        log = logging.getLogger()
        log.info("Processing request with retry policy")
        attempts = 0

        while True:
            try:
                response = call_next(request)
                log.info("Request processed successfully")
                return response

            except Exception as e:
                if attempts < self.max_retries:
                    log.warning(f"Request failed - retrying: {e}")
                    time.sleep(self.initial_wait * (2**attempts))
                    attempts += 1
                    continue
                raise

    def __call__(self, request: Any, call_next: Callable[[Any], Any]) -> Any:
        return self.dispatch(request, call_next)
