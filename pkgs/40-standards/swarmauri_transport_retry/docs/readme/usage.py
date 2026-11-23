from swarmauri_transport_httpx import HttpxClient
from swarmauri_transport_retry import (
    ExponentialBackoffRetryPolicy,
    RetryingHttpClient,
)

client = RetryingHttpClient(
    client=HttpxClient(base_url="https://api.example.com"),
    policy=ExponentialBackoffRetryPolicy(max_attempts=3),
)
response = client.request("GET", "/models")
response.raise_for_status()
