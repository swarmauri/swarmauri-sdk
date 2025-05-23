from __future__ import annotations

from typing import Literal

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.rate_limits.RateLimitBase import RateLimitBase


@ComponentBase.register_type(RateLimitBase, "TokenBucketRateLimit")
class TokenBucketRateLimit(RateLimitBase):
    """Concrete rate limit using a token bucket algorithm."""

    type: Literal["TokenBucketRateLimit"] = "TokenBucketRateLimit"

    def __init__(self, **data):
        super().__init__(**data)
        self._tokens = float(self.capacity)
