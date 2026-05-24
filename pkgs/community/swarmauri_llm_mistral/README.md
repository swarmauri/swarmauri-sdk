![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_llm_mistral/">
        <img src="https://static.pepy.tech/badge/swarmauri_llm_mistral/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_mistral/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_mistral.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_mistral/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_mistral/">
        <img src="https://img.shields.io/pypi/l/swarmauri_llm_mistral" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_mistral/">
        <img src="https://img.shields.io/pypi/v/swarmauri_llm_mistral?label=swarmauri_llm_mistral&color=green" alt="PyPI - swarmauri_llm_mistral"/></a>
</p>

# Swarmauri Mistral LLM

`swarmauri_llm_mistral` provides provider-specific Swarmauri imports for the Mistral API. The package exposes `MistralModel` for chat completion workflows and `MistralToolModel` for tool-calling workflows that execute toolkit functions and optionally follow up with a second model turn.

The runtime targets Mistral's hosted API at `https://api.mistral.ai/v1/`, supports the current allowlisted Mistral, Magistral, Codestral, Devstral, Pixtral, OCR, embedding, and moderation model families tracked in the repo, and preserves Swarmauri `Conversation` and toolkit semantics.

## Why Use This Package?

- Keep Mistral-specific imports explicit in Swarmauri applications.
- Use a chat model adapter and a separate tool-calling adapter that match Swarmauri’s `llms` and `tool_llms` package boundaries.
- Support sync, async, streaming, and batch generation workflows against the Mistral API.
- Execute tools through `MistralToolModel` without hand-writing provider-specific function-calling payloads.

## FAQ

### What does `swarmauri_llm_mistral` install?

It installs `MistralModel` under `swarmauri.llms` and `MistralToolModel` under `swarmauri.tool_llms`.

### Which Mistral capabilities are wrapped today?

`MistralModel` wraps chat completion workflows, including streaming and optional JSON response formatting. `MistralToolModel` wraps tool-calling workflows that serialize Swarmauri tools into Mistral-compatible schemas, execute tool calls, and optionally request a final assistant answer in a second turn.

### Does it support usage metadata?

`MistralModel` can attach Swarmauri `UsageData` when usage information is returned and `include_usage` is enabled.

### Does `MistralToolModel` support streaming?

Yes. The tool model performs the tool-call round first, appends tool results to the conversation, then streams the final assistant response when streaming is requested.

### Which model families are covered?

The current allowlists include Mistral chat models plus related families such as Magistral, Codestral, Devstral, Pixtral, OCR, embed, and moderation surfaces tracked in the runtime code.

### Where should I verify current model and pricing details?

Use the provider documentation links in [docs/LLM_PROVIDER_MODEL_PRICING_LINKS.md](../../../docs/LLM_PROVIDER_MODEL_PRICING_LINKS.md), especially the Mistral models, function-calling, and pricing pages, before publishing model availability or pricing claims.

## Features

- `MistralModel` for sync, async, streaming, and batch chat completion workflows.
- Optional JSON response mode and safe prompt support on chat requests.
- `MistralToolModel` for tool-calling and multiturn tool execution workflows.
- Current repo-tracked allowlists for Mistral, Magistral, Codestral, Devstral, Pixtral, OCR, embed, and moderation models.
- Compatibility with Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_llm_mistral
```

```bash
pip install swarmauri_llm_mistral
```

## Usage

Set `MISTRAL_API_KEY` in your environment before creating the model.

### Chat Completion

```python
import os

from swarmauri_llm_mistral import MistralModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="Summarize Swarmauri in two sentences."))

model = MistralModel(
    api_key=os.environ["MISTRAL_API_KEY"],
    name="mistral-medium-2508",
)
result = model.predict(conversation=conversation, max_tokens=200)

print(result.get_last().content)
```

### Streaming

```python
import os

from swarmauri_llm_mistral import MistralModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="Write a short haiku about AI tooling."))

model = MistralModel(api_key=os.environ["MISTRAL_API_KEY"])

for token in model.stream(conversation=conversation):
    print(token, end="", flush=True)
```

### Tool Calling

```python
import os

from swarmauri_llm_mistral import MistralToolModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.toolkits.Toolkit import Toolkit
from swarmauri_standard.tools.AdditionTool import AdditionTool

conversation = Conversation()
conversation.add_message(HumanMessage(content="What is 19 + 23? Use the tool."))

toolkit = Toolkit(tools={"add": AdditionTool()})

model = MistralToolModel(
    api_key=os.environ["MISTRAL_API_KEY"],
    name="mistral-medium-2508",
)
result = model.predict(
    conversation=conversation,
    toolkit=toolkit,
    tool_choice="auto",
)

print(result.get_last().content)
```

## Examples

- Use `MistralModel` for standard chat completion workflows when you want a direct Mistral provider package import.
- Use `MistralToolModel` when the application needs function calling and tool execution through a Swarmauri toolkit.
- Use `enable_json=True` on `MistralModel` when downstream code expects structured JSON output.

## Related Packages

- [swarmauri_llm_openai](https://pypi.org/project/swarmauri_llm_openai/)
- [swarmauri_llm_groq](https://pypi.org/project/swarmauri_llm_groq/)
- [swarmauri_llm_hyperbolic](https://pypi.org/project/swarmauri_llm_hyperbolic/)
- [swarmauri_llm_deepinfra](https://pypi.org/project/swarmauri_llm_deepinfra/)
- [swarmauri_llm_perplexity](https://pypi.org/project/swarmauri_llm_perplexity/)
- [swarmauri_llm_llamacpp](https://pypi.org/project/swarmauri_llm_llamacpp/)

## Foundational Swarmauri Packages

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [LLM provider model and pricing links](../../../docs/LLM_PROVIDER_MODEL_PRICING_LINKS.md)
- [Mistral models](https://docs.mistral.ai/models)
- [Mistral function calling](https://docs.mistral.ai/capabilities/function_calling/)

## Best Practices

- Keep `MISTRAL_API_KEY` in environment variables or a secret manager.
- Validate model availability against Mistral’s current catalog before hard-coding a specific family into production workflows.
- Use `MistralToolModel` only when a toolkit-backed tool loop is actually needed; plain chat is simpler with `MistralModel`.
- Tune `temperature`, `top_p`, `max_tokens`, and `safe_prompt` to match your product constraints.

## License

Apache-2.0
