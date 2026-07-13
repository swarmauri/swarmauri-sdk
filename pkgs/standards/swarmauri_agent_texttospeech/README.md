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

Install a TTS provider package alongside the agent. For PlayHT:

```bash
uv add swarmauri_llm_playht
```

## Usage

```python
import os

from swarmauri_agent_texttospeech import TextToSpeechAgent
from swarmauri_standard.tts.PlayhtTTS import PlayhtTTS

tts = PlayhtTTS(
    api_key=os.environ["PLAYHT_API_KEY"],
    user_id=os.environ["PLAYHT_USER_ID"],
    voice="Adolfo",
)
agent = TextToSpeechAgent(tts=tts, output_path="greeting.mp3")

audio_path = agent.exec("Welcome to Swarmauri.")
print(audio_path)
```

Each call is independent. The agent passes only that call's text to the TTS
provider and never constructs a conversation or system message.

## Contributing

This package is part of the
[Swarmauri SDK](https://github.com/swarmauri/swarmauri-sdk). Contributions
should follow the repository contribution and style guides.

## License

Apache-2.0
