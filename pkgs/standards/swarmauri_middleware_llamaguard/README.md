![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_middleware_llamaguard/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_middleware_llamaguard" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_llamaguard/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_middleware_llamaguard.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_llamaguard/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_middleware_llamaguard" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_llamaguard/">
        <img src="https://img.shields.io/pypi/l/swarmauri_middleware_llamaguard" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_middleware_llamaguard/">
        <img src="https://img.shields.io/pypi/v/swarmauri_middleware_llamaguard?label=swarmauri_middleware_llamaguard&color=green" alt="PyPI - swarmauri_middleware_llamaguard"/>
    </a>
</p>

---

# Swarmauri Middleware LlamaGuard

A FastAPI middleware that wraps Groq's ``llama-guard-3-8b`` model to provide end-to-end content inspection for both inbound requests and outbound responses. The middleware is designed to slot into any FastAPI application and enforce safety policies before your handlers are invoked.

## Features

- Real-time scanning of incoming request bodies and outgoing responses (including streaming responses).
- Configurable language model injection – provide your own :class:`~swarmauri_standard.llms.GroqModel` or let the middleware create one for you.
- Graceful degradation when no model is configured (traffic is allowed but logged).

## Middleware behavior

``LlamaGuardMiddleware`` inspects content by default with Groq's ``llama-guard-3-8b`` model. Provide an API key via the ``api_key`` argument or the ``GROQ_API_KEY`` environment variable to enable enforcement. When no model is available the middleware logs a warning and treats all content as safe so that applications can continue to function while you configure credentials.

Both JSON responses and streaming responses are inspected. Unsafe content results in an HTTP 400 response with a descriptive error payload.

## Installation

Choose the workflow that matches your project tooling:

- **pip**

  ```bash
  pip install swarmauri_middleware_llamaguard
  ```

- **poetry**

  ```bash
  poetry add swarmauri_middleware_llamaguard
  ```

- **uv**

  ```bash
  uv add swarmauri_middleware_llamaguard
  ```

## Quickstart

1. Configure your Groq API key (either export ``GROQ_API_KEY`` or pass ``api_key`` when constructing the middleware).
2. Attach the middleware to your FastAPI application:

```python
from fastapi import FastAPI, Request

from swarmauri_middleware_llamaguard import LlamaGuardMiddleware

app = FastAPI()
middleware = LlamaGuardMiddleware()  # Uses GROQ_API_KEY from the environment


@app.middleware("http")
async def llama_guard(request: Request, call_next):
    return await middleware.dispatch(request, call_next)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

The middleware will block requests or responses when ``llama-guard-3-8b`` labels the payload as ``unsafe``.

## Example: Local safety checks without Groq

The middleware also accepts a custom language model implementation. The following self-contained example demonstrates how to supply a stub model for local development or tests while still benefiting from end-to-end request inspection.

```python
# README Example: Basic request filtering
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from swarmauri_middleware_llamaguard import LlamaGuardMiddleware
from swarmauri_standard.messages.AgentMessage import AgentMessage


class StubGuardModel:
    def predict(self, conversation, *args, **kwargs):
        latest = str(conversation.get_last().content).lower()
        verdict = "unsafe" if "malicious" in latest else "safe"
        conversation.add_message(AgentMessage(content=verdict))


app = FastAPI()
middleware = LlamaGuardMiddleware(llm=StubGuardModel())


@app.middleware("http")
async def llama_guard(request: Request, call_next):
    return await middleware.dispatch(request, call_next)


@app.post("/echo")
def echo(payload: dict) -> dict:
    return payload


with TestClient(app) as client:
    assert client.post("/echo", json={"message": "hello"}).status_code == 200
    assert (
        client.post("/echo", json={"message": "malicious content"}).status_code
        == 400
    )
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.