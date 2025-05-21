from __future__ import annotations

from typing import Literal
from swarmauri_base.rate_limits.RateLimitBase import RateLimitBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(RateLimitBase, "TokenBucketRateLimit")
class TokenBucketRateLimit(RateLimitBase):
    """Concrete rate limit using a token bucket algorithm."""

    type: Literal["TokenBucketRateLimit"] = "TokenBucketRateLimit"
