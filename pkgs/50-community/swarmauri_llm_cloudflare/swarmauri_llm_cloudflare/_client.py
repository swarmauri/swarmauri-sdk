"""HTTP client composition for Cloudflare Workers AI models."""

from swarmauri_core.transports.i_http_client import IHttpClient
from swarmauri_core.transports.i_http_retry_policy import IHttpRetryPolicy
from swarmauri_transport_httpx import HttpxClient
from swarmauri_transport_retry import RetryingHttpClient

from .CloudflareChatRetryPolicy import CloudflareChatRetryPolicy


def build_cloudflare_client(
    *,
    base_url: str,
    timeout: float,
    max_attempts: int,
    http_client: IHttpClient | None,
    retry_policy: IHttpRetryPolicy | None,
) -> IHttpClient:
    """Build a persistent client while preserving injected ownership."""
    concrete_client = http_client or HttpxClient(
        base_url=base_url,
        timeout=timeout,
    )
    return RetryingHttpClient(
        client=concrete_client,
        policy=retry_policy
        or CloudflareChatRetryPolicy(max_attempts=max(max_attempts, 1)),
        own_client=http_client is None,
    )
