"""Client composition for xAI model families."""

from swarmauri_core.transports.i_http_client import IHttpClient
from swarmauri_core.transports.i_http_retry_policy import IHttpRetryPolicy
from swarmauri_provider_xai import XAIProvider
from swarmauri_transport_httpx import HttpxClient
from swarmauri_transport_retry import RetryingHttpClient

from .XAIChatRetryPolicy import XAIChatRetryPolicy


def build_xai_client(
    *,
    provider: XAIProvider,
    http_client: IHttpClient | None,
    retry_policy: IHttpRetryPolicy | None,
) -> IHttpClient:
    concrete_client = http_client or HttpxClient(
        base_url=provider.base_url,
        timeout=provider.timeout,
    )
    return RetryingHttpClient(
        client=concrete_client,
        policy=retry_policy
        or XAIChatRetryPolicy(max_attempts=max(provider.max_retries, 1)),
        own_client=http_client is None,
    )
