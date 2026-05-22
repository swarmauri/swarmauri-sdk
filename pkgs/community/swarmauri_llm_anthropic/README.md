![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_llm_anthropic/">
        <img src="https://static.pepy.tech/badge/swarmauri_llm_anthropic/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_anthropic/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_anthropic.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_anthropic/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_anthropic/">
        <img src="https://img.shields.io/pypi/l/swarmauri_llm_anthropic" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_anthropic/">
        <img src="https://img.shields.io/pypi/v/swarmauri_llm_anthropic?label=swarmauri_llm_anthropic&color=green" alt="PyPI - swarmauri_llm_anthropic"/></a>
</p>

# Swarmauri Anthropic LLM

`swarmauri_llm_anthropic` provides provider-specific imports for Anthropic Claude models in Swarmauri. It re-exports `AnthropicModel` for standard Messages API chat workflows and `AnthropicToolModel` for tool-assisted conversations, both backed by the maintained implementations in `swarmauri_standard`.

## Why Swarmauri Anthropic LLM?

Use this package when a Swarmauri application should depend explicitly on Anthropic Claude support while keeping the shared Swarmauri conversation and tool abstractions. The adapters send requests to Anthropic's `/v1/messages` endpoint, handle system-message extraction, support sync and async prediction, stream server-sent events, map token usage into Swarmauri `UsageData`, and connect Swarmauri toolkits to Anthropic tool schemas.

## FAQ

### Q: Which Anthropic API does this package use?

A: Both adapters use the Anthropic Messages API at `https://api.anthropic.com/v1/messages` with the `anthropic-version` header set to `2023-06-01`.

### Q: Which classes are exported?

A: The package exports `AnthropicModel` through the `swarmauri.llms` entry point and `AnthropicToolModel` through the `swarmauri.tool_llms` entry point.

### Q: Which Claude model names are configured locally?

A: `AnthropicModel` and `AnthropicToolModel` include configured model IDs such as `claude-opus-4-1`, `claude-opus-4-0`, `claude-sonnet-4-0`, `claude-3-7-sonnet-latest`, and `claude-3-5-haiku-latest`. Set `name` explicitly in production.

### Q: Does the tool model execute Swarmauri tools?

A: Yes. `AnthropicToolModel` converts Swarmauri toolkit tool schemas, sends them in the Anthropic `tools` payload, invokes matching Swarmauri tools when a `tool_use` block is returned, and adds the result to the conversation.

## Features

- Provider-specific imports for `AnthropicModel` and `AnthropicToolModel`.
- Swarmauri `Conversation`, message, toolkit, and usage-data integration.
- Sync `predict()` and async `apredict()` message generation.
- Sync `stream()` and async `astream()` event streaming.
- Sync `batch()` and async `abatch()` helpers for multiple conversations.
- System-message extraction into Anthropic's top-level `system` field for `AnthropicModel`.
- Toolkit schema conversion for `AnthropicToolModel`.
- Retry handling for rate-limit and overloaded-provider status codes on the standard model.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

## Prerequisites

- Anthropic API key from the Anthropic Console.
- Network access to `api.anthropic.com`.
- Swarmauri conversations and messages.
- Swarmauri `Toolkit` objects when using `AnthropicToolModel`.

## Installation

Install with `uv`:

```bash
uv add swarmauri_llm_anthropic
```

Install with `pip`:

```bash
pip install swarmauri_llm_anthropic
```

## Usage

Run a standard Claude Messages API request:

```python
import os

from swarmauri_llm_anthropic import AnthropicModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.messages.SystemMessage import SystemMessage

conversation = Conversation()
conversation.add_message(SystemMessage(content="Answer in concise technical prose."))
conversation.add_message(HumanMessage(content="What is Swarmauri?"))

model = AnthropicModel(
    api_key=os.environ["ANTHROPIC_API_KEY"],
    name="claude-sonnet-4-0",
)
result = model.predict(conversation=conversation, max_tokens=256, temperature=0.2)

print(result.get_last().content)
```

Stream a Claude response:

```python
import os

from swarmauri_llm_anthropic import AnthropicModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="Draft a short API changelog entry."))

model = AnthropicModel(api_key=os.environ["ANTHROPIC_API_KEY"])

for token in model.stream(conversation=conversation, max_tokens=200):
    print(token, end="")
```

Use the tool model with a Swarmauri toolkit:

```python
import os

from swarmauri_llm_anthropic import AnthropicToolModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.toolkits.Toolkit import Toolkit

toolkit = Toolkit()
# toolkit.add_tool(...)

conversation = Conversation()
conversation.add_message(HumanMessage(content="Use an available tool if needed."))

model = AnthropicToolModel(api_key=os.environ["ANTHROPIC_API_KEY"])
result = model.predict(conversation=conversation, toolkit=toolkit)

print(result.get_last().content)
```

## Related Packages

LLM provider packages:

- [swarmauri_llm_ai21](https://pypi.org/project/swarmauri_llm_ai21/)
- [swarmauri_llm_cerebras](https://pypi.org/project/swarmauri_llm_cerebras/)
- [swarmauri_llm_cohere](https://pypi.org/project/swarmauri_llm_cohere/)
- [swarmauri_llm_gemini](https://pypi.org/project/swarmauri_llm_gemini/)
- [swarmauri_llm_groq](https://pypi.org/project/swarmauri_llm_groq/)
- [swarmauri_llm_mistral](https://pypi.org/project/swarmauri_llm_mistral/)
- [swarmauri_llm_openai](https://pypi.org/project/swarmauri_llm_openai/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines core interfaces.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides base component classes.
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) contains the shared Anthropic implementations.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

## Best Practices

- Store `ANTHROPIC_API_KEY` in a secret manager or environment variable.
- Set `name` explicitly for reproducible model behavior.
- Use async methods for high-concurrency service workloads.
- Keep system instructions in `SystemMessage` so the standard model can map them to Anthropic's `system` field.
- Test tool schemas before production use so Anthropic tool calls map cleanly to Swarmauri toolkit functions.

## License

Apache-2.0
