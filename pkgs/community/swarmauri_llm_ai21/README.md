![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_llm_ai21/">
        <img src="https://static.pepy.tech/badge/swarmauri_llm_ai21/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_ai21/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_ai21.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_ai21/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_ai21/">
        <img src="https://img.shields.io/pypi/l/swarmauri_llm_ai21" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_ai21/">
        <img src="https://img.shields.io/pypi/v/swarmauri_llm_ai21?label=swarmauri_llm_ai21&color=green" alt="PyPI - swarmauri_llm_ai21"/></a>
</p>

# Swarmauri AI21 LLM

`swarmauri_llm_ai21` provides the `AI21StudioModel` import path for Swarmauri applications that use AI21 Studio Jamba chat models. The package re-exports the maintained implementation from `swarmauri_standard`, giving projects a provider-specific dependency while preserving Swarmauri conversation, message, usage, streaming, and batch workflows.

## Why Swarmauri AI21 LLM?

Use this package when you want to install only the AI21-facing LLM provider surface for a Swarmauri application. `AI21StudioModel` formats Swarmauri conversations for AI21 Studio chat completions, sends bearer-token authenticated HTTP requests, supports sync and async calls, streams token deltas, records usage data when available, and keeps model selection inside the Swarmauri `LLMBase` interface.

## FAQ

### Q: Which AI21 API does this adapter call?

A: The adapter posts to `https://api.ai21.com/studio/v1/chat/completions`, AI21 Studio's chat completions endpoint used by Jamba chat models.

### Q: Which model names are configured?

A: The current allowed model list is `jamba-large`, `jamba-mini`, `jamba-large-1.7`, and `jamba-mini-1.7`. The default model name is `jamba-large`.

### Q: Does this package contain a separate AI21 implementation?

A: No. It re-exports `AI21StudioModel` from `swarmauri_standard.llms.AI21StudioModel` so applications can depend on the provider package while using the shared implementation.

### Q: What credential is required?

A: Pass an AI21 Studio API key with `AI21StudioModel(api_key="...")`. The repository tests look for `AI21STUDIO_API_KEY` when running live provider checks.

## Features

- Provider-specific import: `from swarmauri_llm_ai21 import AI21StudioModel`.
- Swarmauri `Conversation`, `HumanMessage`, `SystemMessage`, and `AgentMessage` integration.
- Sync `predict()` and async `apredict()` chat completion calls.
- Sync `stream()` and async `astream()` token streaming.
- Sync `batch()` and async `abatch()` helpers for multiple conversations.
- Usage metadata mapping to Swarmauri `UsageData` when provider usage data is returned.
- Retry handling for rate-limit and overloaded-provider status codes.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

## Prerequisites

- An AI21 Studio account and API key.
- Network access to `api.ai21.com`.
- Swarmauri conversations built from Swarmauri message classes.

## Installation

Install with `uv`:

```bash
uv add swarmauri_llm_ai21
```

Install with `pip`:

```bash
pip install swarmauri_llm_ai21
```

## Usage

Run a single chat completion:

```python
import os

from swarmauri_llm_ai21 import AI21StudioModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.messages.SystemMessage import SystemMessage

conversation = Conversation()
conversation.add_message(SystemMessage(content="Answer with concise technical prose."))
conversation.add_message(HumanMessage(content="What is a Swarmauri component?"))

model = AI21StudioModel(
    api_key=os.environ["AI21STUDIO_API_KEY"],
    name="jamba-mini",
)
result = model.predict(conversation=conversation, temperature=0.3, max_tokens=256)

print(result.get_last().content)
```

Stream a response:

```python
import os

from swarmauri_llm_ai21 import AI21StudioModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="Write a short release note."))

model = AI21StudioModel(api_key=os.environ["AI21STUDIO_API_KEY"])

for token in model.stream(conversation=conversation, max_tokens=160):
    print(token, end="")
```

Use the async API:

```python
import os
import asyncio

from swarmauri_llm_ai21 import AI21StudioModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage


async def main() -> None:
    conversation = Conversation()
    conversation.add_message(HumanMessage(content="Summarize AI21 Jamba in one line."))

    model = AI21StudioModel(api_key=os.environ["AI21STUDIO_API_KEY"])
    result = await model.apredict(conversation=conversation)

    print(result.get_last().content)


asyncio.run(main())
```

## Related Packages

LLM provider packages:

- [swarmauri_llm_anthropic](https://pypi.org/project/swarmauri_llm_anthropic/)
- [swarmauri_llm_cerebras](https://pypi.org/project/swarmauri_llm_cerebras/)
- [swarmauri_llm_cohere](https://pypi.org/project/swarmauri_llm_cohere/)
- [swarmauri_llm_gemini](https://pypi.org/project/swarmauri_llm_gemini/)
- [swarmauri_llm_groq](https://pypi.org/project/swarmauri_llm_groq/)
- [swarmauri_llm_mistral](https://pypi.org/project/swarmauri_llm_mistral/)
- [swarmauri_llm_openai](https://pypi.org/project/swarmauri_llm_openai/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines core interfaces.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides base component classes.
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) contains the shared `AI21StudioModel` implementation.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

## Best Practices

- Read the API key from environment variables or a secret manager.
- Set `name` explicitly so deployments do not change behavior when defaults change.
- Use async methods for high-concurrency applications.
- Keep prompts and system messages in Swarmauri `Conversation` objects for provider portability.
- Capture `UsageData` for cost and latency monitoring where provider responses include token usage.

## License

Apache-2.0
