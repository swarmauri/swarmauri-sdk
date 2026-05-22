![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_llm_cerebras/">
        <img src="https://static.pepy.tech/badge/swarmauri_llm_cerebras/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_cerebras/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_cerebras.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_cerebras/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_cerebras/">
        <img src="https://img.shields.io/pypi/l/swarmauri_llm_cerebras" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_cerebras/">
        <img src="https://img.shields.io/pypi/v/swarmauri_llm_cerebras?label=swarmauri_llm_cerebras&color=green" alt="PyPI - swarmauri_llm_cerebras"/></a>
</p>

# Swarmauri Cerebras LLM

`swarmauri_llm_cerebras` provides the `CerebrasModel` import path for Swarmauri applications that use Cerebras Inference chat completions. The package re-exports the maintained implementation from `swarmauri_standard`, giving projects a provider-specific dependency for Cerebras-hosted Llama, Qwen, and GPT-OSS style model workflows.

## Why Swarmauri Cerebras LLM?

Use this package when you want Cerebras Inference behind the Swarmauri `LLMBase` interface. `CerebrasModel` formats Swarmauri conversations for the Cerebras chat completions endpoint, supports sync and async prediction, streams response deltas, runs sequential and concurrent batches, captures usage data, and exposes model options such as temperature, top-p, seed, stop sequences, and JSON output mode.

## FAQ

### Q: Which Cerebras endpoint does this adapter call?

A: The adapter posts to `https://api.cerebras.ai/v1/chat/completions` and uses bearer-token authentication with a Cerebras API key.

### Q: Which model names are configured locally?

A: The current configured list includes `llama-4-scout-17b-16e-instruct`, `llama3.1-8b`, `llama-3.3-70b`, `llama-4-maverick-17b-128e-instruct`, `qwen-3-32b`, `qwen-3-coder-480b`, and `gpt-oss-120b`. The default is `llama3.1-8b`.

### Q: Does this package contain a separate Cerebras implementation?

A: No. It re-exports `CerebrasModel` from `swarmauri_standard.llms.CerebrasModel` so applications can depend on this provider package while sharing the common implementation.

### Q: How do I request JSON output?

A: Pass `enable_json=True` to `predict()`, `apredict()`, `stream()`, or `astream()`. The adapter sets `response_format` to `json_object`.

## Features

- Provider-specific import: `from swarmauri_llm_cerebras import CerebrasModel`.
- Swarmauri `Conversation`, `HumanMessage`, `SystemMessage`, and `AgentMessage` integration.
- Sync `predict()` and async `apredict()` chat completion calls.
- Sync `stream()` and async `astream()` streaming deltas.
- Sync `batch()` and async `abatch()` helpers.
- Configurable `temperature`, `max_completion_tokens`, `top_p`, `seed`, `stop`, and `enable_json`.
- Usage metadata mapping to Swarmauri `UsageData` when provider usage data is returned.
- Model discovery through the Cerebras `/v1/models` endpoint.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

## Prerequisites

- Cerebras Inference API key.
- Network access to `api.cerebras.ai`.
- Swarmauri conversations built from Swarmauri message classes.

## Installation

Install with `uv`:

```bash
uv add swarmauri_llm_cerebras
```

Install with `pip`:

```bash
pip install swarmauri_llm_cerebras
```

## Usage

Run a chat completion:

```python
import os

from swarmauri_llm_cerebras import CerebrasModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.messages.SystemMessage import SystemMessage

conversation = Conversation()
conversation.add_message(SystemMessage(content="Answer with concise technical prose."))
conversation.add_message(HumanMessage(content="What is Cerebras Inference?"))

model = CerebrasModel(
    api_key=os.environ["CEREBRAS_API_KEY"],
    name="llama3.1-8b",
)
result = model.predict(
    conversation=conversation,
    temperature=0.2,
    max_completion_tokens=256,
)

print(result.get_last().content)
```

Stream response deltas:

```python
import os

from swarmauri_llm_cerebras import CerebrasModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="Write a short product summary."))

model = CerebrasModel(api_key=os.environ["CEREBRAS_API_KEY"])

for token in model.stream(conversation=conversation, max_completion_tokens=180):
    print(token, end="")
```

Use the async API:

```python
import asyncio
import os

from swarmauri_llm_cerebras import CerebrasModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage


async def main() -> None:
    conversation = Conversation()
    conversation.add_message(HumanMessage(content="Return JSON with a status field."))

    model = CerebrasModel(api_key=os.environ["CEREBRAS_API_KEY"])
    result = await model.apredict(conversation=conversation, enable_json=True)

    print(result.get_last().content)


asyncio.run(main())
```

## Related Packages

LLM provider packages:

- [swarmauri_llm_ai21](https://pypi.org/project/swarmauri_llm_ai21/)
- [swarmauri_llm_anthropic](https://pypi.org/project/swarmauri_llm_anthropic/)
- [swarmauri_llm_cohere](https://pypi.org/project/swarmauri_llm_cohere/)
- [swarmauri_llm_deepinfra](https://pypi.org/project/swarmauri_llm_deepinfra/)
- [swarmauri_llm_groq](https://pypi.org/project/swarmauri_llm_groq/)
- [swarmauri_llm_mistral](https://pypi.org/project/swarmauri_llm_mistral/)
- [swarmauri_llm_openai](https://pypi.org/project/swarmauri_llm_openai/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines core interfaces.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides base component classes.
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) contains the shared `CerebrasModel` implementation.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

## Best Practices

- Store `CEREBRAS_API_KEY` in a secret manager or environment variable.
- Set `name` explicitly for reproducible model behavior.
- Use `seed` when deterministic replay matters for supported models.
- Use async methods for high-concurrency workloads.
- Validate JSON mode outputs before feeding them into strict downstream parsers.

## License

Apache-2.0
