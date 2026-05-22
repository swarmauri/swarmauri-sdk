![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_llm_groq/">
        <img src="https://static.pepy.tech/badge/swarmauri_llm_groq/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_groq/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_groq.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_groq/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_groq/">
        <img src="https://img.shields.io/pypi/l/swarmauri_llm_groq" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_groq/">
        <img src="https://img.shields.io/pypi/v/swarmauri_llm_groq?label=swarmauri_llm_groq&color=green" alt="PyPI - swarmauri_llm_groq"/></a>
</p>

# Swarmauri Groq LLM

`swarmauri_llm_groq` provides provider-specific Groq imports for Swarmauri
applications that need fast OpenAI-compatible inference. The package exports
chat, tool-calling, vision, and audio adapters while keeping their runtime
implementations aligned with `swarmauri_standard`.

Groq's public API documentation describes an OpenAI-compatible base URL at
`https://api.groq.com/openai/v1`, with endpoints for chat completions, audio
transcriptions, and audio translations. This package maps those API surfaces
into Swarmauri components:

- `GroqModel` for chat completions, streaming, JSON responses, and batch helper
  workflows.
- `GroqToolModel` for function/tool calling through Swarmauri `Toolkit`
  instances.
- `GroqVisionModel` for vision-language chat completion payloads.
- `GroqAIAudio` for transcription and translation with Groq-hosted Whisper
  models.

## Why Use This Package?

- Keep Groq-specific model dependencies explicit while preserving common
  Swarmauri conversation and toolkit patterns.
- Use Groq's low-latency OpenAI-compatible chat completions without rewriting
  application code around raw HTTP payloads.
- Add tool calling, vision-language prompts, or speech-to-text workflows from
  one provider package.
- Swap between Groq and other Swarmauri LLM provider packages while retaining
  familiar `predict`, `stream`, `apredict`, `astream`, `batch`, and `abatch`
  workflows.

## FAQ

### What does `swarmauri_llm_groq` install?

It installs provider package entry points for `GroqModel`, `GroqToolModel`,
`GroqVisionModel`, and `GroqAIAudio`.

### Which Groq endpoints does it call?

The chat, tool, and vision adapters post to
`https://api.groq.com/openai/v1/chat/completions`. The audio adapter uses
`https://api.groq.com/openai/v1/audio/transcriptions` and
`https://api.groq.com/openai/v1/audio/translations`.

### Does it support tool calling?

Yes. `GroqToolModel` converts Swarmauri toolkit schemas to Groq-compatible tool
definitions, sends them with chat completions, executes returned tool calls, and
can perform a follow-up model call with tool results.

### Does it support vision?

Yes. `GroqVisionModel` accepts Swarmauri message content that can include
structured content lists for OpenAI-compatible vision chat payloads. The runtime
also emits a deprecation warning that new projects should review the newer
Swarmauri VLM imports when available.

### Does audio streaming work?

No. `GroqAIAudio` supports file-based transcription and translation through
`predict`, `apredict`, `batch`, and `abatch`. Its `stream` and `astream` methods
raise `NotImplementedError`.

## Features

- `GroqModel` for synchronous, asynchronous, streaming, JSON, and batch chat
  completion workflows.
- `GroqToolModel` for Groq tool use with Swarmauri `Toolkit` schemas.
- `GroqVisionModel` for OpenAI-compatible vision-language chat payloads.
- `GroqAIAudio` for Whisper transcription and translation tasks.
- Usage metadata support where Groq chat responses include usage data.
- Model discovery through Groq's OpenAI-compatible models endpoint for chat.
- Compatibility with Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_llm_groq
```

```bash
pip install swarmauri_llm_groq
```

## Prerequisites

Create a Groq API key in the Groq console and pass it to the model constructor
as `api_key=...`. Package live tests are skipped unless provider credentials are
available in the environment.

## Usage

```python
from swarmauri_llm_groq import GroqModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="Write a one-sentence release note."))

model = GroqModel(api_key="GROQ_API_KEY")
result = model.predict(conversation=conversation, max_tokens=120)

print(result.get_last().content)
```

### Streaming Chat Completion

```python
from swarmauri_llm_groq import GroqModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="List three build pipeline risks."))

model = GroqModel(api_key="GROQ_API_KEY")

for token in model.stream(conversation=conversation):
    print(token, end="")
```

### Tool Calling

```python
from swarmauri_llm_groq import GroqToolModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.toolkits.Toolkit import Toolkit

conversation = Conversation()
conversation.add_message(HumanMessage(content="Use a tool if one is relevant."))

toolkit = Toolkit()
model = GroqToolModel(api_key="GROQ_API_KEY")
result = model.predict(conversation=conversation, toolkit=toolkit)

print(result.get_last().content)
```

### Audio Transcription

```python
from swarmauri_llm_groq import GroqAIAudio

audio = GroqAIAudio(api_key="GROQ_API_KEY")
text = audio.predict("meeting.wav", task="transcription")

print(text)
```

### Vision-Language Prompt

```python
from swarmauri_llm_groq import GroqVisionModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(
    HumanMessage(
        content=[
            {"type": "text", "text": "Describe the image."},
            {"type": "image_url", "image_url": {"url": "https://example.com/image.png"}},
        ]
    )
)

model = GroqVisionModel(api_key="GROQ_API_KEY")
result = model.predict(conversation=conversation)

print(result.get_last().content)
```

## Related Packages

- [swarmauri_llm_anthropic](https://pypi.org/project/swarmauri_llm_anthropic/)
- [swarmauri_llm_deepinfra](https://pypi.org/project/swarmauri_llm_deepinfra/)
- [swarmauri_llm_deepseek](https://pypi.org/project/swarmauri_llm_deepseek/)
- [swarmauri_llm_gemini](https://pypi.org/project/swarmauri_llm_gemini/)
- [swarmauri_llm_mistral](https://pypi.org/project/swarmauri_llm_mistral/)
- [swarmauri_llm_openai](https://pypi.org/project/swarmauri_llm_openai/)
- [swarmauri_llm_whisper](https://pypi.org/project/swarmauri_llm_whisper/)

## Foundational Swarmauri Packages

- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)
- [swarmauri](https://pypi.org/project/swarmauri/)

## Provider Documentation

- [Groq API reference](https://console.groq.com/docs/api-reference)
- [Groq OpenAI compatibility](https://console.groq.com/docs/openai)
- [Groq models](https://console.groq.com/docs/models)
- [Groq tool use](https://console.groq.com/docs/tool-use)
- [Groq speech to text](https://console.groq.com/docs/speech-to-text)

## Best Practices

- Store Groq API keys in environment variables or a secrets manager.
- Confirm model availability against Groq's current model catalog before
  production deployment.
- Use `GroqToolModel` only when tools are needed; plain chat requests are simpler
  with `GroqModel`.
- Use `GroqAIAudio` for file-based transcription and translation, not streaming
  audio.
- Prefer newer Swarmauri VLM and STT imports for new projects when available.

## License

Apache-2.0
