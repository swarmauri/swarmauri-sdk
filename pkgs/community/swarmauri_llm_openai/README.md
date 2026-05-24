![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_llm_openai/">
        <img src="https://static.pepy.tech/badge/swarmauri_llm_openai/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_openai/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_openai.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_openai/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_openai/">
        <img src="https://img.shields.io/pypi/l/swarmauri_llm_openai" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_llm_openai/">
        <img src="https://img.shields.io/pypi/v/swarmauri_llm_openai?label=swarmauri_llm_openai&color=green" alt="PyPI - swarmauri_llm_openai"/></a>
</p>

# Swarmauri OpenAI LLM

`swarmauri_llm_openai` provides provider-specific Swarmauri imports for OpenAI chat, reasoning, tool-calling, audio transcription, and text-to-speech workflows. The package exposes `OpenAIModel`, `OpenAIReasonModel`, `OpenAIToolModel`, `OpenAIAudio`, and `OpenAIAudioTTS` as direct provider-package imports while preserving the shared runtime implementations in `swarmauri_standard`.

The repo currently tracks OpenAI chat model families including `gpt-5.x`, `gpt-4.1`, `gpt-4o`, `gpt-4-turbo`, `gpt-oss`, reasoning families including `o1`, `o3`, and `o4-mini`, audio transcription models including `whisper-1` and `gpt-4o-*transcribe`, and text-to-speech models including `tts-1`, `tts-1-hd`, and `gpt-4o-mini-tts`.

## Why Use This Package?

- Keep OpenAI-specific imports explicit in Swarmauri applications.
- Use separate adapters for standard chat, reasoning, tool-calling, transcription, and TTS workflows.
- Reuse Swarmauri `Conversation`, toolkit, and component semantics across the OpenAI surface area.
- Track current OpenAI model families through one provider package boundary.

## FAQ

### What does `swarmauri_llm_openai` install?

It installs `OpenAIModel`, `OpenAIReasonModel`, `OpenAIToolModel`, `OpenAIAudio`, and `OpenAIAudioTTS`.

### Which OpenAI capabilities are wrapped today?

The package covers standard chat completions, reasoning-oriented chat models, tool-calling workflows, audio transcription, and text-to-speech generation.

### What is the difference between `OpenAIModel` and `OpenAIReasonModel`?

`OpenAIModel` targets general chat model families such as `gpt-5.x`, `gpt-4.1`, and `gpt-4o`. `OpenAIReasonModel` targets the reasoning families tracked in the repo, including `o1`, `o3`, and `o4-mini` variants.

### When should I use `OpenAIToolModel`?

Use it when the application needs OpenAI tool calling through a Swarmauri toolkit. It is the provider-specific surface for tool-backed agent workflows.

### What do `OpenAIAudio` and `OpenAIAudioTTS` do?

`OpenAIAudio` wraps audio transcription workflows. `OpenAIAudioTTS` wraps text-to-speech generation workflows.

### Where should I verify current models and pricing?

Use the OpenAI section in [docs/LLM_PROVIDER_MODEL_PRICING_LINKS.md](../../../docs/LLM_PROVIDER_MODEL_PRICING_LINKS.md), which points to the current OpenAI models, function-calling, audio, TTS, and pricing documentation.

## Features

- `OpenAIModel` for sync, async, streaming, and batch chat completion workflows.
- `OpenAIReasonModel` for reasoning-model workflows across the repo-tracked `o*` families.
- `OpenAIToolModel` for toolkit-backed tool-calling and agent execution flows.
- `OpenAIAudio` for speech-to-text workflows against the tracked OpenAI transcription models.
- `OpenAIAudioTTS` for text-to-speech workflows against the tracked OpenAI TTS models.
- Compatibility with Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_llm_openai
```

```bash
pip install swarmauri_llm_openai
```

## Usage

Set `OPENAI_API_KEY` in your environment before creating any of the OpenAI adapters.

### Chat Completion

```python
import os

from swarmauri_llm_openai import OpenAIModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="Summarize Swarmauri in two sentences."))

model = OpenAIModel(
    api_key=os.environ["OPENAI_API_KEY"],
    name="gpt-5.5",
)
result = model.predict(conversation=conversation)

print(result.get_last().content)
```

### Reasoning Model

```python
import os

from swarmauri_llm_openai import OpenAIReasonModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="Reason through a release rollback plan step by step."))

model = OpenAIReasonModel(
    api_key=os.environ["OPENAI_API_KEY"],
    name="o3",
)
result = model.predict(conversation=conversation)

print(result.get_last().content)
```

### Tool Calling

```python
import os

from swarmauri_llm_openai import OpenAIToolModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.toolkits.Toolkit import Toolkit
from swarmauri_standard.tools.AdditionTool import AdditionTool

conversation = Conversation()
conversation.add_message(HumanMessage(content="What is 19 + 23? Use the tool."))

toolkit = Toolkit(tools={"add": AdditionTool()})

model = OpenAIToolModel(
    api_key=os.environ["OPENAI_API_KEY"],
    name="gpt-5.5",
)
result = model.predict(
    conversation=conversation,
    toolkit=toolkit,
    tool_choice="auto",
)

print(result.get_last().content)
```

### Audio Transcription

```python
import os

from swarmauri_llm_openai import OpenAIAudio

audio_model = OpenAIAudio(
    api_key=os.environ["OPENAI_API_KEY"],
    name="whisper-1",
)

text = audio_model.predict("tests/static/test.mp3")
print(text)
```

### Text To Speech

```python
import os

from swarmauri_llm_openai import OpenAIAudioTTS

tts_model = OpenAIAudioTTS(
    api_key=os.environ["OPENAI_API_KEY"],
    name="tts-1",
)

audio_bytes = tts_model.predict("Swarmauri turns provider APIs into composable components.")
print(len(audio_bytes))
```

## Examples

- Use `OpenAIModel` for general-purpose chat completion workflows.
- Use `OpenAIReasonModel` when you want the reasoning-model family explicitly.
- Use `OpenAIToolModel` when an agent needs toolkit-backed tool invocation.
- Use `OpenAIAudio` and `OpenAIAudioTTS` when the workflow crosses text, speech, and audio generation boundaries.

## Related Packages

- [swarmauri_llm_mistral](https://pypi.org/project/swarmauri_llm_mistral/)
- [swarmauri_llm_groq](https://pypi.org/project/swarmauri_llm_groq/)
- [swarmauri_llm_hyperbolic](https://pypi.org/project/swarmauri_llm_hyperbolic/)
- [swarmauri_llm_deepinfra](https://pypi.org/project/swarmauri_llm_deepinfra/)
- [swarmauri_llm_perplexity](https://pypi.org/project/swarmauri_llm_perplexity/)
- [swarmauri_llm_playht](https://pypi.org/project/swarmauri_llm_playht/)

## Foundational Swarmauri Packages

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [LLM provider model and pricing links](../../../docs/LLM_PROVIDER_MODEL_PRICING_LINKS.md)
- [OpenAI models](https://platform.openai.com/docs/models)
- [OpenAI function calling](https://platform.openai.com/docs/guides/function-calling)
- [OpenAI text to speech](https://platform.openai.com/docs/guides/text-to-speech)

## Best Practices

- Keep `OPENAI_API_KEY` in environment variables or a secret manager.
- Pick the adapter that matches the workflow: chat, reasoning, tool-calling, transcription, or TTS.
- Validate model availability against current OpenAI docs before hard-coding a dated model variant in production.
- Use reasoning models deliberately, since they should be chosen for workflows that actually benefit from deeper multi-step reasoning.

## License

Apache-2.0
