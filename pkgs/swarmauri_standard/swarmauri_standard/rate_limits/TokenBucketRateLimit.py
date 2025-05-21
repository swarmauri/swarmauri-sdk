from __future__ import annotations

from typing import Literal
import threading
import time
from pydantic import PrivateAttr
from swarmauri_base.rate_limits.RateLimitBase import RateLimitBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(RateLimitBase, "TokenBucketRateLimit")
class TokenBucketRateLimit(RateLimitBase):
    """Concrete rate limit using a token bucket algorithm."""

    type: Literal["TokenBucketRateLimit"] = "TokenBucketRateLimit"
    _lock: threading.Lock = PrivateAttr(default_factory=threading.Lock)

    def acquire(self, tokens: int = 1) -> None:
        """Block until the requested tokens are available."""
        while True:
            with self._lock:
                if self.allow(tokens):
                    return
                remaining = tokens - self._tokens
            time.sleep(max(remaining / self.refill_rate, 0))
