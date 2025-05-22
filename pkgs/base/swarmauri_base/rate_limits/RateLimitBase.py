from __future__ import annotations

import time
from typing import Optional, Literal
from pydantic import Field, PrivateAttr, ConfigDict

from swarmauri_core.rate_limits.IRateLimit import IRateLimit
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class RateLimitBase(IRateLimit, ComponentBase):
    """Base class implementing common token bucket logic."""

    capacity: int = 1
    refill_rate: float = 1.0
    _tokens: float = PrivateAttr(0.0)
    _last_refill: float = PrivateAttr(default_factory=time.time)

    resource: Optional[str] = Field(default=ResourceTypes.RATE_LIMIT.value, frozen=True)
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["RateLimitBase"] = "RateLimitBase"

    def refill(self) -> None:
        """Refill tokens according to elapsed time."""
        now = time.time()
        elapsed = now - self._last_refill
        self._last_refill = now
        self._tokens = min(self.capacity, self._tokens + elapsed * self.refill_rate)

    def allow(self, tokens: int = 1) -> bool:
        """Attempt to consume tokens and return whether the request is allowed."""
        self.refill()
        if self._tokens >= tokens:
            self._tokens -= tokens
            return True
        return False

    def available_tokens(self) -> int:
        """Return the number of currently available tokens."""
        self.refill()
        return int(self._tokens)
