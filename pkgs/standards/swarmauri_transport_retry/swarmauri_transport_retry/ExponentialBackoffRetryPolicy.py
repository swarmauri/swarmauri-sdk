"""Concrete exponential-backoff policy for HTTP operations."""

from __future__ import annotations

import random
from collections.abc import Collection
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Literal

from swarmauri_core.transports.i_http_response import IHttpResponse
from swarmauri_core.transports.i_http_retry_policy import IHttpRetryPolicy


class ExponentialBackoffRetryPolicy(IHttpRetryPolicy):
    """Retry safe HTTP operations with bounded exponential backoff."""

    type: Literal["ExponentialBackoffRetryPolicy"] = (
        "ExponentialBackoffRetryPolicy"
    )

    def __init__(
        self,
        *,
        max_attempts: int = 3,
        retryable_status_codes: Collection[int] = (429, 500, 502, 503, 504),
        retryable_methods: Collection[str] = (
            "GET",
            "HEAD",
            "OPTIONS",
            "PUT",
            "DELETE",
        ),
        base_delay: float = 1.0,
        maximum_delay: float = 30.0,
        respect_retry_after: bool = True,
        retry_request_errors: bool = True,
        jitter_ratio: float = 0.0,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if base_delay < 0 or maximum_delay < 0:
            raise ValueError("retry delays cannot be negative")
        if not 0 <= jitter_ratio <= 1:
            raise ValueError("jitter_ratio must be between 0 and 1")
        self.max_attempts = max_attempts
        self.retryable_status_codes = frozenset(retryable_status_codes)
        self.retryable_methods = frozenset(
            method.upper() for method in retryable_methods
        )
        self.base_delay = base_delay
        self.maximum_delay = maximum_delay
        self.respect_retry_after = respect_retry_after
        self.retry_request_errors = retry_request_errors
        self.jitter_ratio = jitter_ratio

    def should_retry(
        self,
        *,
        method: str,
        attempt: int,
        response: IHttpResponse | None = None,
        error: Exception | None = None,
    ) -> bool:
        if attempt >= self.max_attempts:
            return False
        if method.upper() not in self.retryable_methods:
            return False
        if error is not None:
            return self.retry_request_errors
        return (
            response is not None
            and response.status_code in self.retryable_status_codes
        )

    def delay_seconds(
        self,
        *,
        attempt: int,
        response: IHttpResponse | None = None,
    ) -> float:
        retry_after = self._retry_after_seconds(response)
        if retry_after is not None:
            delay = retry_after
        else:
            delay = self.base_delay * (2 ** max(attempt - 1, 0))
        delay = min(delay, self.maximum_delay)
        if self.jitter_ratio:
            spread = delay * self.jitter_ratio
            delay = random.uniform(max(0.0, delay - spread), delay + spread)
        return max(0.0, min(delay, self.maximum_delay))

    def _retry_after_seconds(
        self, response: IHttpResponse | None
    ) -> float | None:
        if not self.respect_retry_after or response is None:
            return None
        value = response.headers.get("Retry-After")
        if not value:
            return None
        try:
            return max(float(value), 0.0)
        except ValueError:
            try:
                retry_at = parsedate_to_datetime(value)
            except (TypeError, ValueError):
                return None
            if retry_at.tzinfo is None:
                retry_at = retry_at.replace(tzinfo=timezone.utc)
            return max(
                (retry_at - datetime.now(timezone.utc)).total_seconds(),
                0.0,
            )
