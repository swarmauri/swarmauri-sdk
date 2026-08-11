"""Compose OpenRouter provider configuration with Swarmauri transports."""

from collections.abc import AsyncIterator, Iterator

from swarmauri_core.transports.i_http_client import IHttpClient
from swarmauri_core.transports.i_http_retry_policy import IHttpRetryPolicy
from swarmauri_core.transports.i_http_response import IHttpResponse
from swarmauri_core.transports.i_managed_http_client import IManagedHttpClient
from swarmauri_provider_openrouter import OpenRouterProvider
from swarmauri_transport_httpx import HttpxClient
from swarmauri_transport_retry import RetryingHttpClient

from .OpenRouterRetryPolicy import OpenRouterRetryPolicy
from ._internal.common import decode_sse_line


def build_openrouter_client(
    *,
    provider: OpenRouterProvider,
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
        or OpenRouterRetryPolicy(max_attempts=max(provider.max_retries, 1)),
        own_client=http_client is None,
    )


def connection(
    provider: OpenRouterProvider,
    capability: str,
    *,
    model: str | None = None,
) -> tuple[str, dict[str, str]]:
    config = provider.connection_config(capability, model=model)
    return str(config.endpoint), provider.authorize(config)


def request(
    provider: OpenRouterProvider,
    client: IHttpClient,
    capability: str,
    *,
    model: str | None = None,
    json_data: dict | None = None,
) -> IHttpResponse:
    endpoint, headers = connection(provider, capability, model=model)
    response = client.request(
        "GET" if json_data is None else "POST",
        endpoint,
        headers=headers,
        json=json_data,
    )
    response.raise_for_status()
    return response


async def arequest(
    provider: OpenRouterProvider,
    client: IHttpClient,
    capability: str,
    *,
    model: str | None = None,
    json_data: dict | None = None,
) -> IHttpResponse:
    endpoint, headers = connection(provider, capability, model=model)
    response = await client.arequest(
        "GET" if json_data is None else "POST",
        endpoint,
        headers=headers,
        json=json_data,
    )
    response.raise_for_status()
    return response


def stream_events(
    provider: OpenRouterProvider,
    client: IHttpClient,
    capability: str,
    payload: dict,
    *,
    model: str | None = None,
) -> Iterator[dict]:
    endpoint, headers = connection(provider, capability, model=model)
    with client.stream(
        "POST", endpoint, headers=headers, json=payload
    ) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if event := decode_sse_line(line):
                yield event


async def astream_events(
    provider: OpenRouterProvider,
    client: IHttpClient,
    capability: str,
    payload: dict,
    *,
    model: str | None = None,
) -> AsyncIterator[dict]:
    endpoint, headers = connection(provider, capability, model=model)
    async with client.astream(
        "POST", endpoint, headers=headers, json=payload
    ) as response:
        response.raise_for_status()
        async for line in response.aiter_lines():
            if event := decode_sse_line(line):
                yield event


def close_client(client: IHttpClient) -> None:
    if isinstance(client, IManagedHttpClient):
        client.close()


async def aclose_client(client: IHttpClient) -> None:
    if isinstance(client, IManagedHttpClient):
        await client.aclose()
