![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

# Swarmauri Text-to-Speech Agent

`swarmauri_agent_texttospeech` provides a stateless agent that converts each
text prompt into an audio file through any Swarmauri `TTSBase` provider.

[![PyPI Downloads](https://static.pepy.tech/badge/swarmauri_agent_texttospeech)](https://pepy.tech/projects/swarmauri_agent_texttospeech)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_agent_texttospeech.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_agent_texttospeech/)
[![Python Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://pypi.org/project/swarmauri_agent_texttospeech/)
[![License](https://img.shields.io/pypi/l/swarmauri_agent_texttospeech)](https://pypi.org/project/swarmauri_agent_texttospeech/)
[![PyPI Version](https://img.shields.io/pypi/v/swarmauri_agent_texttospeech)](https://pypi.org/project/swarmauri_agent_texttospeech/)

## Features

- Converts one fresh text input into one audio file.
- Uses any provider implementing Swarmauri's `TTSBase` contract.
- Keeps no conversation history, memory, or system context.
- Supports synchronous, asynchronous, and batch agent execution.
- Generates distinct default paths for batch outputs.

## Installation

```bash
uv add swarmauri_agent_texttospeech
```

```bash
pip install swarmauri_agent_texttospeech
```

Install a TTS provider package alongside the agent. For the alpha OpenAI provider:

```bash
uv add --prerelease allow swarmauri_tts_openai
```

Or with `pip`:

```bash
pip install --pre swarmauri_tts_openai
```

## Usage

```python
import os

from swarmauri_agent_texttospeech import TextToSpeechAgent
from swarmauri_tts_openai import OpenaiTTS

tts = OpenaiTTS(
    api_key=os.environ["OPENAI_API_KEY"],
    name="gpt-4o-mini-tts",
    voice="alloy",
)
agent = TextToSpeechAgent(tts=tts, output_path="greeting.mp3")

audio_path = agent.exec("Welcome to Swarmauri.")
print(audio_path)
```

Each call is independent. The agent passes only that call's text to the TTS
provider and never constructs a conversation or system message.

## Structured dialogue and bounded batches

The agent also forwards a nonempty tuple of typed dialogue turns unchanged:

```python
import os

from swarmauri_agent_texttospeech import TextToSpeechAgent
from swarmauri_tts_gemini_dialogue import (
    GeminiDialogueTTS, GeminiDialogueTurn,
)

provider = GeminiDialogueTTS(
    api_key=os.environ["GEMINI_API_KEY"],
    speaker_voices={"A": "Puck", "B": "Kore"},
)
agent = TextToSpeechAgent(tts=provider, output_path="dialogue.wav")
turns = (
    GeminiDialogueTurn(text="Hello", speaker="A"),
    GeminiDialogueTurn(text="Hello back", speaker="B"),
)
agent.exec(turns)
# await agent.abatch([turns], max_concurrent=2)
```

Speaker and voice validation belongs to the selected provider. A JSON string
is not parsed into turns. Set filenames to match the codec; Gemini/native
DeepInfra WAV defaults require .wav paths. Async batches default to at most
five concurrent calls, with a positive integer max_concurrent override.

The OpenAI Speech example above is temporary compatibility: its models have a
scheduled 2027-01-06 shutdown. All new provider packages remain alpha and live
verification is pending; see the SDK migration and verification guides.

## Contributing

This package is part of the
[Swarmauri SDK](https://github.com/swarmauri/swarmauri-sdk). Contributions
should follow the repository contribution and style guides.

## License

Apache-2.0

Provider instances are validated against TTSBase at call-time construction, so
providers imported after the agent class remain usable. Serialized providers
retain their concrete fields; import that provider before deserialization.
