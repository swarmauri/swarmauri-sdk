"""Retry policy for NVIDIA NIM chat operations."""

from swarmauri_core.transports.i_http_response import IHttpResponse
from swarmauri_transport_retry import ExponentialBackoffRetryPolicy


class NvidiaNIMChatRetryPolicy(ExponentialBackoffRetryPolicy):
    """Retry safe reads and rate-limited chat submissions."""

    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("retryable_methods", {"GET", "POST"})
        super().__init__(**kwargs)

    def should_retry(
        self,
        *,
        method: str,
        attempt: int,
        response: IHttpResponse | None = None,
        error: Exception | None = None,
    ) -> bool:
        if method.upper() == "POST":
            return (
                attempt < self.max_attempts
                and error is None
                and response is not None
                and response.status_code == 429
            )
        return super().should_retry(
            method=method,
            attempt=attempt,
            response=response,
            error=error,
        )
