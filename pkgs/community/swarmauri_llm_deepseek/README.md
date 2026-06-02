![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_llm_deepseek/">
        <img src="https://static.pepy.tech/badge/swarmauri_llm_deepseek/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_deepseek/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_deepseek.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_deepseek/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_deepseek/">
        <img src="https://img.shields.io/pypi/l/swarmauri_llm_deepseek" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_deepseek/">
        <img src="https://img.shields.io/pypi/v/swarmauri_llm_deepseek?label=swarmauri_llm_deepseek&color=green" alt="PyPI - swarmauri_llm_deepseek"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri DeepSeek LLM

`swarmauri_llm_deepseek` provides the provider-specific `DeepSeekModel`
import for Swarmauri applications that call DeepSeek's OpenAI-compatible chat
completion API. Install this package when a project should depend on the
DeepSeek adapter directly while keeping the runtime implementation aligned with
`swarmauri_standard`.

The adapter formats Swarmauri `Conversation` history as chat messages, sends
requests to DeepSeek chat completions, and appends the provider response as an
`AgentMessage`. It supports synchronous calls, asynchronous calls, streaming,
and simple batch workflows for assistants, coding agents, reasoning workflows,
and model-provider experiments.

DeepSeek's current API documentation describes an OpenAI-compatible chat API and
lists `deepseek-v4-flash` and `deepseek-v4-pro` as current model IDs. This
package currently defaults to the compatibility aliases `deepseek-chat` and
`deepseek-reasoner`, which DeepSeek documents as mapped compatibility model
names.

## Why Use This Package?

- Keep DeepSeek-specific imports explicit in application dependencies.
- Use Swarmauri conversation and message primitives instead of hand-rolled
  request dictionaries throughout the application.
- Swap DeepSeek with other Swarmauri LLM provider packages while preserving the
  same high-level `predict`, `stream`, `apredict`, and `astream` workflows.
- Use DeepSeek reasoning and chat models through one Swarmauri adapter surface.

## FAQ

### What does `swarmauri_llm_deepseek` install?

It installs a provider package that exports `DeepSeekModel` from
`swarmauri_standard.llms.DeepSeekModel` and registers the same model entry point
for Swarmauri plugin discovery.

### Which DeepSeek endpoint does the adapter call?

The implementation creates HTTP clients with the configured DeepSeek base URL
and posts to `/chat/completions` using DeepSeek's OpenAI-compatible chat
completion payload shape.

### Which models are available?

The package default is `deepseek-chat`, with `deepseek-reasoner` also listed in
`allowed_models`. DeepSeek's public documentation now also lists
`deepseek-v4-flash` and `deepseek-v4-pro` as current model IDs, so production
deployments should verify model availability against the DeepSeek platform
before pinning a model name.

### Does the package expose DeepSeek reasoning content?

The current Swarmauri adapter stores the assistant's final response content on
the conversation. DeepSeek-specific reasoning fields are not exposed as a
separate Swarmauri message property by this package.

## Features

- Provider-specific `DeepSeekModel` import for Swarmauri applications.
- Synchronous chat completion through `predict`.
- Asynchronous chat completion through `apredict`.
- Token streaming through `stream` and `astream`.
- Batch helpers through `batch` and `abatch`.
- Configurable chat generation parameters including `temperature`,
  `max_tokens`, `top_p`, `stop`, `frequency_penalty`, and `presence_penalty`.
- Compatibility with Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_llm_deepseek
```

```bash
pip install swarmauri_llm_deepseek
```

## Prerequisites

Create a DeepSeek API key in the DeepSeek platform and pass it to
`DeepSeekModel(api_key=...)`. The tests in this package look for
`DEEPSEEK_API_KEY` when running live provider checks.

## Usage

```python
from swarmauri_llm_deepseek import DeepSeekModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(
    HumanMessage(content="Summarize why OpenAI-compatible APIs are useful.")
)

model = DeepSeekModel(api_key="DEEPSEEK_API_KEY")
result = model.predict(conversation=conversation, max_tokens=200)

print(result.get_last().content)
```

### Streaming

```python
from swarmauri_llm_deepseek import DeepSeekModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="Write a three-line release note."))

model = DeepSeekModel(api_key="DEEPSEEK_API_KEY")

for token in model.stream(conversation=conversation):
    print(token, end="")
```

### Async Prediction

```python
import asyncio

from swarmauri_llm_deepseek import DeepSeekModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage


async def main() -> None:
    conversation = Conversation()
    conversation.add_message(HumanMessage(content="Explain agent memory in one paragraph."))

    model = DeepSeekModel(api_key="DEEPSEEK_API_KEY")
    result = await model.apredict(conversation=conversation)
    print(result.get_last().content)


asyncio.run(main())
```

## Related Packages

- [swarmauri_llm_ai21](https://pypi.org/project/swarmauri_llm_ai21/)
- [swarmauri_llm_anthropic](https://pypi.org/project/swarmauri_llm_anthropic/)
- [swarmauri_llm_cerebras](https://pypi.org/project/swarmauri_llm_cerebras/)
- [swarmauri_llm_deepinfra](https://pypi.org/project/swarmauri_llm_deepinfra/)
- [swarmauri_llm_groq](https://pypi.org/project/swarmauri_llm_groq/)
- [swarmauri_llm_mistral](https://pypi.org/project/swarmauri_llm_mistral/)
- [swarmauri_llm_openai](https://pypi.org/project/swarmauri_llm_openai/)

## Foundational Swarmauri Packages

- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)
- [swarmauri](https://pypi.org/project/swarmauri/)

## Provider Documentation

- [DeepSeek API quick start](https://api-docs.deepseek.com/)
- [DeepSeek chat completion reference](https://api-docs.deepseek.com/api/create-chat-completion)
- [DeepSeek reasoning model guide](https://api-docs.deepseek.com/guides/reasoning_model)

## Best Practices

- Keep DeepSeek credentials in environment variables or a secrets manager.
- Confirm current model names and availability in the DeepSeek platform before
  production deployment.
- Use `deepseek-reasoner` only when the workflow benefits from reasoning-model
  behavior; the current adapter records the final answer content.
- Set explicit `max_tokens` and timeout expectations for long-running reasoning
  requests.

## License

Apache-2.0


