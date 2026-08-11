import json
from contextlib import asynccontextmanager, contextmanager

import pytest
from swarmauri_core.transports import HttpRequestError, IHttpClient
from swarmauri_transport_retry import (
    ExponentialBackoffRetryPolicy,
    RetryingHttpClient,
)


class Response:
    def __init__(self, status_code: int):
        self.status_code = status_code
        self.headers = {}

    def read(self):
        return b"{}"

    async def aread(self):
        return self.read()

    def json(self):
        return json.loads(self.read())

    def raise_for_status(self):
        return None


class SequencedClient(IHttpClient):
    def __init__(self, statuses):
        self.statuses = iter(statuses)
        self.calls = 0

    def request(self, method, path, **kwargs):
        self.calls += 1
        value = next(self.statuses)
        if isinstance(value, Exception):
            raise value
        return Response(value)

    async def arequest(self, method, path, **kwargs):
        return self.request(method, path, **kwargs)

    @contextmanager
    def stream(self, method, path, **kwargs):
        yield self.request(method, path, **kwargs)

    @asynccontextmanager
    async def astream(self, method, path, **kwargs):
        yield await self.arequest(method, path, **kwargs)


def test_retries_retryable_response_without_sleeping_in_test():
    wrapped = SequencedClient([429, 200])
    sleeps = []
    client = RetryingHttpClient(
        client=wrapped,
        policy=ExponentialBackoffRetryPolicy(base_delay=0),
        sleep=sleeps.append,
    )

    assert client.request("GET", "/models").status_code == 200
    assert wrapped.calls == 2
    assert sleeps == [0]


def test_does_not_replay_post_request_error():
    wrapped = SequencedClient([HttpRequestError("network")])
    client = RetryingHttpClient(
        client=wrapped,
        policy=ExponentialBackoffRetryPolicy(base_delay=0),
    )

    with pytest.raises(HttpRequestError):
        client.request("POST", "/chat")
    assert wrapped.calls == 1


@pytest.mark.asyncio
async def test_async_retry_uses_async_sleep():
    wrapped = SequencedClient([503, 200])
    sleeps = []

    async def record_sleep(delay):
        sleeps.append(delay)

    client = RetryingHttpClient(
        client=wrapped,
        policy=ExponentialBackoffRetryPolicy(base_delay=0),
        async_sleep=record_sleep,
    )
    assert (await client.arequest("GET", "/models")).status_code == 200
    assert sleeps == [0]
