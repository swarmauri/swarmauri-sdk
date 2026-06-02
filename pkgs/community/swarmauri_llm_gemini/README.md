![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_llm_gemini/">
        <img src="https://static.pepy.tech/badge/swarmauri_llm_gemini/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_gemini/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_gemini.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_gemini/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_gemini/">
        <img src="https://img.shields.io/pypi/l/swarmauri_llm_gemini" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_gemini/">
        <img src="https://img.shields.io/pypi/v/swarmauri_llm_gemini?label=swarmauri_llm_gemini&color=green" alt="PyPI - swarmauri_llm_gemini"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Gemini LLM

`swarmauri_llm_gemini` provides provider-specific imports for Google Gemini
models in Swarmauri applications. It exports `GeminiProModel` for standard
generation and streaming workflows and `GeminiToolModel` for Gemini function
calling through Swarmauri toolkits.

The adapters use Google Gemini's `generateContent` and `streamGenerateContent`
API shape through `generativelanguage.googleapis.com/v1beta`. They translate
Swarmauri conversations into Gemini `contents`, apply safety settings, preserve
system instructions where supported by the implementation, and append generated
responses back to the conversation as `AgentMessage` instances.

## Why Use This Package?

- Keep Google Gemini-specific dependencies explicit in provider-aware Swarmauri
  applications.
- Use the same Swarmauri `Conversation`, message, and toolkit workflows across
  Gemini and other LLM providers.
- Support both direct text generation and Gemini function-calling workflows.
- Stream Gemini responses through the same high-level Swarmauri model interface
  used by other provider packages.

## FAQ

### What does `swarmauri_llm_gemini` install?

It installs provider package entry points for `GeminiProModel` and
`GeminiToolModel`, both re-exported from `swarmauri_standard`.

### Which Gemini API methods does it use?

`GeminiProModel` calls `models.generateContent` for standard prediction and
`models.streamGenerateContent` for streaming. `GeminiToolModel` uses
`generateContent` with Gemini-compatible function declarations converted from a
Swarmauri `Toolkit`.

### Does this package support tools?

Yes. Use `GeminiToolModel` when a conversation should give Gemini access to
Swarmauri tools. The adapter converts toolkit schemas with
`GeminiSchemaConverter`, executes returned function calls, and can make a
follow-up model call with tool results.

### Which models are listed by default?

The current implementation includes Gemini 2.0 Flash, Gemini 2.0 Flash Lite,
Gemini 2.0 Pro experimental, Gemini 1.5 Flash, Gemini 1.5 Flash 8B, and Gemini
1.5 Pro in its allowed model list. Confirm current production model availability
in Google's Gemini API documentation before pinning deployment defaults.

### Can it include usage metadata?

`GeminiProModel` can attach token usage metadata to the returned Swarmauri
`AgentMessage` when `include_usage` is enabled and the provider response
contains usage metadata.

## Features

- `GeminiProModel` for generation, async generation, streaming, and batch
  conversation workflows.
- `GeminiToolModel` for Gemini function calling through Swarmauri toolkits.
- Support for Gemini `systemInstruction` / `system_instruction` payloads in the
  current adapters.
- Safety settings for harassment, hate speech, sexually explicit content, and
  dangerous content thresholds.
- Configurable generation controls such as `temperature` and `max_tokens`.
- Optional usage metadata handling on `GeminiProModel`.
- Compatibility with Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_llm_gemini
```

```bash
pip install swarmauri_llm_gemini
```

## Prerequisites

Create a Gemini API key in Google AI Studio or Google Cloud and pass it to the
model constructor as `api_key=...`.

## Usage

```python
from swarmauri_llm_gemini import GeminiProModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="Write a concise project status update."))

model = GeminiProModel(api_key="GEMINI_API_KEY")
result = model.predict(conversation=conversation, max_tokens=200)

print(result.get_last().content)
```

### Streaming

```python
from swarmauri_llm_gemini import GeminiProModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="List three risks for an AI release."))

model = GeminiProModel(api_key="GEMINI_API_KEY")

for token in model.stream(conversation=conversation, max_tokens=200):
    print(token, end="")
```

### Tool Calling

```python
from swarmauri_llm_gemini import GeminiToolModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.toolkits.Toolkit import Toolkit

conversation = Conversation()
conversation.add_message(HumanMessage(content="Use the available tool if needed."))

toolkit = Toolkit()
model = GeminiToolModel(api_key="GEMINI_API_KEY")
result = model.predict(conversation=conversation, toolkit=toolkit)

print(result.get_last().content)
```

## Related Packages

- [swarmauri_llm_anthropic](https://pypi.org/project/swarmauri_llm_anthropic/)
- [swarmauri_llm_cohere](https://pypi.org/project/swarmauri_llm_cohere/)
- [swarmauri_llm_deepseek](https://pypi.org/project/swarmauri_llm_deepseek/)
- [swarmauri_llm_groq](https://pypi.org/project/swarmauri_llm_groq/)
- [swarmauri_llm_mistral](https://pypi.org/project/swarmauri_llm_mistral/)
- [swarmauri_llm_openai](https://pypi.org/project/swarmauri_llm_openai/)

## Foundational Swarmauri Packages

- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)
- [swarmauri](https://pypi.org/project/swarmauri/)

## Provider Documentation

- [Gemini API reference](https://ai.google.dev/api)
- [Generate content with Gemini](https://ai.google.dev/api/generate-content)
- [Gemini function calling](https://ai.google.dev/gemini-api/docs/function-calling)

## Best Practices

- Store Gemini API keys in environment variables or a secrets manager.
- Confirm model availability against the current Gemini API before pinning model
  names for production.
- Use `GeminiToolModel` only when the workflow actually needs tool execution.
- Keep tool schemas small and deterministic so Gemini can select and call tools
  reliably.

## License

Apache-2.0


