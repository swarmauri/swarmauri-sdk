![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

# Swarmauri PlayHT Text-to-Speech

`swarmauri_tts_playht` is the standalone PlayHT provider package for Swarmauri.
Its `PlayHTModel` implements `TTSBase` and converts independent text inputs into
audio files without pretending to be an LLM.

[![PyPI Downloads](https://static.pepy.tech/badge/swarmauri_tts_playht)](https://pepy.tech/projects/swarmauri_tts_playht)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tts_playht.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tts_playht/)
[![Python Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://pypi.org/project/swarmauri_tts_playht/)
[![License](https://img.shields.io/pypi/l/swarmauri_tts_playht)](https://pypi.org/project/swarmauri_tts_playht/)
[![PyPI Version](https://img.shields.io/pypi/v/swarmauri_tts_playht)](https://pypi.org/project/swarmauri_tts_playht/)

## Features

- Native `TTSBase` provider registered as `swarmauri.tts.PlayHTModel`.
- Synchronous, asynchronous, and batch audio generation.
- PlayHT voice discovery and cloned-voice management.
- Configurable voice engine, voice, output format, and timeout.
- Agent-only CLI support for positional, piped, file-based, and interactive
  text.
- Command-line selection of the PlayHT voice model and voice.

## Installation

```bash
uv add swarmauri_tts_playht
```

```bash
pip install swarmauri_tts_playht
```

Set `PLAYHT_API_KEY` and `PLAYHT_USER_ID` before generating audio.

## Usage

```python
import os

from swarmauri_tts_playht import PlayHTModel

tts = PlayHTModel(
    api_key=os.environ["PLAYHT_API_KEY"],
    user_id=os.environ["PLAYHT_USER_ID"],
    name="Play3.0-mini",
    voice="Adolfo",
)
audio_path = tts.predict("Welcome to Swarmauri.", "welcome.mp3")
print(audio_path)
```

Generate through the stateless `TextToSpeechAgent`:

```bash
swarmauri-playht "Welcome to Swarmauri." \
  --voice-model PlayHT2.0-turbo \
  --voice Adolfo \
  --output welcome.mp3
```

Every CLI invocation uses `TextToSpeechAgent`. It adds no conversation, memory,
system context, or text-generating LLM. `--model` remains available as an alias
for `--voice-model`.

## Contributing

This package is part of the
[Swarmauri SDK](https://github.com/swarmauri/swarmauri-sdk). Contributions
should follow the repository contribution and style guides.

## License

Apache-2.0
