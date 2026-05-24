![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_llm_llamacpp/">
        <img src="https://static.pepy.tech/badge/swarmauri_llm_llamacpp/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_llamacpp/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_llamacpp.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_llamacpp/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_llamacpp/">
        <img src="https://img.shields.io/pypi/l/swarmauri_llm_llamacpp" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_llamacpp/">
        <img src="https://img.shields.io/pypi/v/swarmauri_llm_llamacpp?label=swarmauri_llm_llamacpp&color=green" alt="PyPI - swarmauri_llm_llamacpp"/></a>
</p>

# Swarmauri llama.cpp LLM

`swarmauri_llm_llamacpp` provides the provider-specific Swarmauri import package for `LlamaCppModel`. It is intended for local or self-hosted `llama.cpp` deployments that expose an OpenAI-compatible API, not a hosted SaaS provider.

The runtime delegates to `swarmauri_standard.llms.LlamaCppModel`, which talks to a local `llama.cpp` server at `http://localhost:8080/v1` by default, discovers models from `/models`, and sends chat completion requests to `/chat/completions`.

## Why Use This Package?

- Keep local `llama.cpp` model usage explicit in Swarmauri applications.
- Run self-hosted LLM inference through the same `Conversation` workflow used by other Swarmauri provider packages.
- Support sync, async, streaming, and batch execution against an OpenAI-compatible local endpoint.
- Avoid coupling local model runtime choices to hosted-provider packages.

## FAQ

### What does `swarmauri_llm_llamacpp` install?

It installs the `LlamaCppModel` provider package entry point under `swarmauri.llms`.

### Does this package download or bundle a model?

No. You must run your own `llama.cpp` server and make at least one model available through its OpenAI-compatible API.

### Which endpoint does the runtime call?

By default the underlying runtime targets `http://localhost:8080/v1`, queries `/models` for model discovery, and calls `/chat/completions` for inference.

### Does it require an API key?

Usually no for local development. The runtime can include an API key if your self-hosted endpoint is configured to require one.

### Does it support streaming and async workflows?

Yes. `LlamaCppModel` supports `predict`, `apredict`, `stream`, `astream`, `batch`, and `abatch`.

### Where should I verify model pricing?

There is no provider pricing surface for `llama.cpp` itself. Cost depends on your hardware, hosting, and model selection. See [docs/LLM_PROVIDER_MODEL_PRICING_LINKS.md](../../../docs/LLM_PROVIDER_MODEL_PRICING_LINKS.md) for the project-level note on local-runtime pricing.

## Features

- `LlamaCppModel` import package for local or self-hosted `llama.cpp` inference.
- OpenAI-compatible chat completion requests against a local `llama.cpp` server.
- Automatic model discovery via the `/models` endpoint.
- Sync, async, streaming, and batch generation workflows.
- Optional JSON response mode and stop-sequence support.
- Compatibility with Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_llm_llamacpp
```

```bash
pip install swarmauri_llm_llamacpp
```

## Usage

Start a `llama.cpp` server that exposes an OpenAI-compatible API before creating the model.

### Basic Chat Completion

```python
from swarmauri_llm_llamacpp import LlamaCppModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="Explain Swarmauri in one paragraph."))

model = LlamaCppModel()
result = model.predict(conversation=conversation, max_tokens=200)

print(result.get_last().content)
```

### Streaming

```python
from swarmauri_llm_llamacpp import LlamaCppModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="Write a short haiku about local inference."))

model = LlamaCppModel()

for token in model.stream(conversation=conversation):
    print(token, end="", flush=True)
```

### Async

```python
import asyncio

from swarmauri_llm_llamacpp import LlamaCppModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage


async def main() -> None:
    conversation = Conversation()
    conversation.add_message(HumanMessage(content="List three reasons to self-host an LLM."))

    model = LlamaCppModel()
    result = await model.apredict(conversation=conversation)
    print(result.get_last().content)


# asyncio.run(main())
```

## Examples

- Use `LlamaCppModel` when you want Swarmauri agents to run against a local `llama.cpp` server instead of a remote provider.
- Use `stream` or `astream` when the UI should render tokens as they are produced by the local model.
- Use `enable_json=True` when your downstream logic expects structured JSON output from the model.

## Related Packages

- [swarmauri_llm_openai](https://pypi.org/project/swarmauri_llm_openai/)
- [swarmauri_llm_mistral](https://pypi.org/project/swarmauri_llm_mistral/)
- [swarmauri_llm_deepinfra](https://pypi.org/project/swarmauri_llm_deepinfra/)
- [swarmauri_llm_groq](https://pypi.org/project/swarmauri_llm_groq/)
- [swarmauri_llm_hyperbolic](https://pypi.org/project/swarmauri_llm_hyperbolic/)
- [swarmauri_llm_leptonai](https://pypi.org/project/swarmauri_llm_leptonai/)

## Foundational Swarmauri Packages

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [LLM provider model and pricing links](../../../docs/LLM_PROVIDER_MODEL_PRICING_LINKS.md)
- [llama.cpp](https://github.com/ggml-org/llama.cpp)

## Best Practices

- Keep your `llama.cpp` server configuration aligned with the OpenAI-compatible routes this runtime expects.
- Confirm the local server is reachable before starting agent workflows that depend on it.
- Use self-hosted model names returned by `/models` instead of hard-coding assumptions about local model IDs.
- Tune `temperature`, `max_tokens`, `stop`, and `enable_json` to match your application contract.

## License

Apache-2.0
