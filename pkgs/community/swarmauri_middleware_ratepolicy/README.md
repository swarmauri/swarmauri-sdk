![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_middleware_ratepolicy/">
        <img src="https://static.pepy.tech/badge/swarmauri_middleware_ratepolicy/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_middleware_ratepolicy/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_middleware_ratepolicy.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_middleware_ratepolicy/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_middleware_ratepolicy/">
        <img src="https://img.shields.io/pypi/l/swarmauri_middleware_ratepolicy" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_middleware_ratepolicy/">
        <img src="https://img.shields.io/pypi/v/swarmauri_middleware_ratepolicy?label=swarmauri_middleware_ratepolicy&color=green" alt="PyPI - swarmauri_middleware_ratepolicy"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Middleware Rate Policy

`swarmauri_middleware_ratepolicy` is the Swarmauri retry-policy middleware for
wrapping request-like call flows with bounded retry attempts and exponential
backoff. It provides a synchronous `dispatch(request, call_next)` surface that
retries failing operations before finally re-raising the exception.

## Why Use Swarmauri Middleware Rate Policy

- Retry flaky upstream operations with a consistent middleware surface.
- Bound retry counts while still applying exponential backoff.
- Add basic resilience to synchronous request-processing or job-execution
  pipelines.
- Combine with circuit breakers and logging to build layered fault handling.

## FAQ

> **What parameters does this middleware expose?**  
> `max_retries` and `initial_wait`.

> **How is the wait interval calculated?**  
> The middleware sleeps for `initial_wait * 2**attempts` between retries.

> **Is the middleware async?**  
> No. The current implementation is synchronous.

> **What happens after the retry limit is reached?**  
> The last exception is re-raised.

## Features

- Bounded retry loops over a synchronous `call_next` callable.
- Exponential backoff using `initial_wait`.
- Log messages for processing, retry attempts, and success.
- Swarmauri `MiddlewareBase` integration for reusable resilience flows.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_middleware_ratepolicy
```

```bash
pip install swarmauri_middleware_ratepolicy
```

## Usage

```python
from swarmauri_middleware_ratepolicy import RetryPolicyMiddleware

retry = RetryPolicyMiddleware(max_retries=3, initial_wait=0.5)

class RequestEnvelope:
    def __init__(self, payload: str):
        self.payload = payload

request = RequestEnvelope("work-item-123")

def call_next(req):
    raise RuntimeError("Simulated upstream failure")

retry.dispatch(request, call_next)
```

## Examples

### Retry a failing operation

```python
import logging
from swarmauri_middleware_ratepolicy import RetryPolicyMiddleware

logging.basicConfig(level=logging.INFO)

retry = RetryPolicyMiddleware(max_retries=3, initial_wait=0.25)

def unstable(_request):
    raise RuntimeError("Temporary failure")

retry.dispatch({"task": "sync"}, unstable)
```

### Wrap an external API call

```python
import httpx
from swarmauri_middleware_ratepolicy import RetryPolicyMiddleware

retry = RetryPolicyMiddleware(max_retries=4, initial_wait=0.25)

class RequestWrapper:
    def __init__(self, url: str):
        self.url = url

response = retry.dispatch(
    RequestWrapper("https://api.example.com/data"),
    lambda req: httpx.get(req.url, timeout=5),
)

print(response.status_code)
```

### Register in a larger middleware stack

```python
from swarmauri_middleware_ratepolicy import RetryPolicyMiddleware

middleware = RetryPolicyMiddleware(max_retries=2, initial_wait=1.0)
print(middleware.type)
```

## Related Packages

- [swarmauri_middleware_circuitbreaker](https://pypi.org/project/swarmauri_middleware_circuitbreaker/)
- [swarmauri_state_clipboard](https://pypi.org/project/swarmauri_state_clipboard/)
- [swarmauri_middleware_ratepolicy](https://pypi.org/project/swarmauri_middleware_ratepolicy/)

## Swarmauri Foundations

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [Tenacity documentation](https://tenacity.readthedocs.io/en/stable/index.html)

## Best Practices

- Keep retry counts small for latency-sensitive user requests.
- Use circuit breakers when a dependency is consistently unhealthy instead of
  only increasing retries.
- Apply retries around idempotent operations whenever possible.
- Convert async flows deliberately if you need to wrap them with this
  synchronous middleware surface.

## License

This project is licensed under the Apache-2.0 License.


