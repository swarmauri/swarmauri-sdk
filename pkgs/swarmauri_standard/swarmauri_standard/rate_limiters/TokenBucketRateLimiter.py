"""Token bucket rate limiter implementation."""

from __future__ import annotations

import threading
import time


class TokenBucketRateLimiter:
    """Limit calls using a token bucket algorithm."""

    def __init__(self, capacity: int = 1, refill_rate: float = 1.0) -> None:
        """Initialize the rate limiter.

        Args:
            capacity (int): Maximum number of tokens in the bucket.
            refill_rate (float): Number of tokens added per second.
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self._tokens = float(capacity)
        self._last_refill = time.time()
        self._lock = threading.Lock()

    def _refill(self) -> None:
        """Add tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self._last_refill
        self._last_refill = now
        self._tokens = min(self.capacity, self._tokens + elapsed * self.refill_rate)

    def acquire(self, tokens: int = 1) -> None:
        """Block until the requested tokens are available."""
        while True:
            with self._lock:
                self._refill()
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return
                remaining = tokens - self._tokens
            time.sleep(max(remaining / self.refill_rate, 0))
