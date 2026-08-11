![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![PyPI version](https://img.shields.io/pypi/v/swarmauri_transport_retry.svg)](https://pypi.org/project/swarmauri_transport_retry/) [![Python](https://img.shields.io/pypi/pyversions/swarmauri_transport_retry.svg)](https://pypi.org/project/swarmauri_transport_retry/) [![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE) [![Downloads](https://static.pepy.tech/badge/swarmauri_transport_retry)](https://pepy.tech/project/swarmauri_transport_retry) [![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk.svg?path=pkgs%2Fstandards%2Fswarmauri_transport_retry)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/)

# swarmauri_transport_retry

Policy-driven retries for any client implementing Swarmauri's `IHttpClient` contract.

## Features

- Bounded exponential backoff with optional jitter.
- `Retry-After` support for seconds and HTTP dates.
- Separate policy decisions from sync, async, and streaming execution.
- Protect non-idempotent methods from replay by default.
- Wrap any Swarmauri HTTP client without depending on its HTTP library.

## Installation

```bash
uv add swarmauri_transport_retry
```

```bash
pip install swarmauri_transport_retry
```

## Usage

```python
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
```

The retry policy controls replay safety and delay. The wrapped transport remains responsible for moving HTTP requests and responses.
