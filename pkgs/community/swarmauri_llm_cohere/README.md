![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_llm_cohere/">
        <img src="https://static.pepy.tech/badge/swarmauri_llm_cohere/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_cohere/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_cohere.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_cohere/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_cohere/">
        <img src="https://img.shields.io/pypi/l/swarmauri_llm_cohere" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_cohere/">
        <img src="https://img.shields.io/pypi/v/swarmauri_llm_cohere?label=swarmauri_llm_cohere&color=green" alt="PyPI - swarmauri_llm_cohere"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Cohere LLM

`swarmauri_llm_cohere` provides provider-specific imports for Cohere Command models in Swarmauri. It re-exports `CohereModel` for standard chat workflows and `CohereToolModel` for tool-assisted conversations, both backed by the maintained implementations in `swarmauri_standard`.

## Why Swarmauri Cohere LLM?

Use this package when a Swarmauri application should depend explicitly on Cohere chat support while preserving Swarmauri conversations, messages, toolkits, usage records, streaming, and batch workflows. The adapters call Cohere API v1 `/chat`, map Swarmauri system messages to Cohere `preamble`, pass prior messages as `chat_history`, and support Command model families used for enterprise chat, RAG, multilingual, and tool-use workloads.

## FAQ

### Q: Which Cohere API does this package use?

A: The current adapters call Cohere API v1 at `https://api.cohere.ai/v1/chat`. They do not yet target the newer `/v2/chat` endpoint.

### Q: Which classes are exported?

A: The package exports `CohereModel` through the `swarmauri.llms` entry point and `CohereToolModel` through the `swarmauri.tool_llms` entry point.

### Q: Which model names are configured locally?

A: The configured list includes `command-a-03-2025`, `command-r7b-12-2024`, `command-a-translate-08-2025`, `command-a-reasoning-08-2025`, `command-a-vision-07-2025`, `command-r-plus`, `command-r`, `command`, and related dated aliases. The default is `command-a-03-2025`.

### Q: How does tool use work?

A: `CohereToolModel` converts Swarmauri toolkit tools into Cohere-compatible tool schemas, sends an initial `/chat` request with tools, executes returned tool calls with the Swarmauri toolkit, then sends a second `/chat` request with `tool_results`.

## Features

- Provider-specific imports for `CohereModel` and `CohereToolModel`.
- Swarmauri `Conversation`, message, toolkit, and usage-data integration.
- Sync `predict()` and async `apredict()` chat calls.
- Sync `stream()` and async `astream()` response streaming.
- Sync `batch()` and async `abatch()` helpers.
- Cohere v1 `preamble` support from Swarmauri system messages.
- Cohere v1 `chat_history` construction from previous Swarmauri messages.
- Cohere tool schema conversion and tool result submission in `CohereToolModel`.
- Retry handling for rate-limit and overloaded-provider status codes.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

## Prerequisites

- Cohere API key from the Cohere dashboard.
- Network access to `api.cohere.ai`.
- Swarmauri conversations built from Swarmauri message classes.
- Swarmauri `Toolkit` objects when using `CohereToolModel`.

## Installation

Install with `uv`:

```bash
uv add swarmauri_llm_cohere
```

Install with `pip`:

```bash
pip install swarmauri_llm_cohere
```

## Usage

Run a standard Cohere chat request:

```python
import os

from swarmauri_llm_cohere import CohereModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.messages.SystemMessage import SystemMessage

conversation = Conversation()
conversation.add_message(SystemMessage(content="Answer with concise technical prose."))
conversation.add_message(HumanMessage(content="What is Cohere Command A?"))

model = CohereModel(
    api_key=os.environ["COHERE_API_KEY"],
    name="command-a-03-2025",
)
result = model.predict(conversation=conversation, max_tokens=256, temperature=0.2)

print(result.get_last().content)
```

Stream a response:

```python
import os

from swarmauri_llm_cohere import CohereModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="Draft a short support response."))

model = CohereModel(api_key=os.environ["COHERE_API_KEY"])

for token in model.stream(conversation=conversation, max_tokens=200):
    print(token, end="")
```

Use the tool model with a Swarmauri toolkit:

```python
import os

from swarmauri_llm_cohere import CohereToolModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.toolkits.Toolkit import Toolkit

toolkit = Toolkit()
# toolkit.add_tool(...)

conversation = Conversation()
conversation.add_message(HumanMessage(content="Use an available tool if needed."))

model = CohereToolModel(api_key=os.environ["COHERE_API_KEY"])
result = model.predict(conversation=conversation, toolkit=toolkit)

print(result.get_last().content)
```

## Related Packages

LLM provider packages:

- [swarmauri_llm_ai21](https://pypi.org/project/swarmauri_llm_ai21/)
- [swarmauri_llm_anthropic](https://pypi.org/project/swarmauri_llm_anthropic/)
- [swarmauri_llm_cerebras](https://pypi.org/project/swarmauri_llm_cerebras/)
- [swarmauri_llm_gemini](https://pypi.org/project/swarmauri_llm_gemini/)
- [swarmauri_llm_groq](https://pypi.org/project/swarmauri_llm_groq/)
- [swarmauri_llm_mistral](https://pypi.org/project/swarmauri_llm_mistral/)
- [swarmauri_llm_openai](https://pypi.org/project/swarmauri_llm_openai/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines core interfaces.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides base component classes.
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) contains the shared Cohere implementations.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

## Best Practices

- Store `COHERE_API_KEY` in a secret manager or environment variable.
- Set `name` explicitly for reproducible model behavior.
- Use `CohereToolModel` only with tool schemas that have been tested against Cohere's v1 tool format.
- Use async methods for high-concurrency service workloads.
- Capture Swarmauri `UsageData` for cost and latency monitoring when Cohere returns usage fields.

## License

Apache-2.0


