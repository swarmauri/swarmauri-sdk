![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

# swarmauri_tts_elevenlabs_dialogue

Alpha Swarmauri ElevenLabsDialogueTTS component. Ordered text/voice turns on the dialogue API, separate from single-speaker ElevenLabs TTS.

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_tts_elevenlabs_dialogue)](https://pepy.tech/projects/swarmauri_tts_elevenlabs_dialogue)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tts_elevenlabs_dialogue.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tts_elevenlabs_dialogue)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_tts_elevenlabs_dialogue)](https://pypi.org/project/swarmauri_tts_elevenlabs_dialogue/)
[![License](https://img.shields.io/pypi/l/swarmauri_tts_elevenlabs_dialogue)](https://pypi.org/project/swarmauri_tts_elevenlabs_dialogue/)
[![Version](https://img.shields.io/pypi/v/swarmauri_tts_elevenlabs_dialogue?label=swarmauri_tts_elevenlabs_dialogue&color=green)](https://pypi.org/project/swarmauri_tts_elevenlabs_dialogue/)

## Features

- Structured multi-voice files, async synthesis, streams and bounded batches.
- Provider-specific schemas and local input validation.
- Fixed provider endpoints and no automatic replay of billable requests.
- Python 3.10-3.14; no swarmauri_standard dependency.

## Installation

```bash
uv add --prerelease allow swarmauri_tts_elevenlabs_dialogue
```

```bash
pip install --pre swarmauri_tts_elevenlabs_dialogue
```

This source candidate needs swarmauri_base>=0.11.0.dev12 published first.

## Usage

```python
import os
from swarmauri_tts_elevenlabs_dialogue import ElevenLabsDialogueTTS, DialogueTurn

provider = ElevenLabsDialogueTTS(api_key=os.environ["ELEVENLABS_API_KEY"])
turns = (
    DialogueTurn(text="[curious] Hello?", voice_id=os.environ["VOICE_ONE"]),
    DialogueTurn(text="Hello back!", voice_id=os.environ["VOICE_TWO"]),
)
path = provider.predict(turns, "dialogue.mp3")
# await provider.apredict(turns, "dialogue.mp3")
# provider.batch({turns: "dialogue.mp3"})
# await provider.abatch({turns: "dialogue.mp3"}, max_concurrent=2)
# Iterate provider.stream(turns), or async-iterate provider.astream(turns).
```

## API boundary

Use a tuple of frozen DialogueTurn values, including as batch dictionary keys.
The order and voice IDs are preserved. Plain strings require default_voice_id;
that mode also works with TextToSpeechAgent. JSON text is never interpreted as a
turn list. The component enforces ten unique voices and a conservative 2000
character total, following the reliable-generation guidance. Model IDs are
eleven_v4 (default) and eleven_v3. output_format supports mp3_44100_128 (default),
pcm_24000 and ulaw_8000. Streaming uses /v1/text-to-dialogue/stream; output
retains the selected codec. Voice cloning, timestamps and WebSockets are outside
this interface. Raw PCM/mulaw need matching playback settings, not an MP3 decoder.

Primary reference: [provider API](https://elevenlabs.io/docs/api-reference/text-to-dialogue/convert).

## Verification and alpha status

Live API behavior is **unverified**; tracked in [#6304](https://github.com/swarmauri/swarmauri-sdk/issues/6304). No paid synthesis was run. Retain version
0.1.0a1 and Development Status :: 3 - Alpha until maintainers review sufficient
live evidence. Mocked schemas do not prove playable audio, model availability,
voice controls, quality, latency or cost.

Live tests require SWARMAURI_LIVE_TTS=1 plus private ELEVENLABS_API_KEY. Configure SWARMAURI_TTS_VOICE and SWARMAURI_TTS_SECOND_VOICE
for your account. Select the model with SWARMAURI_TTS_MODEL. A key alone never
enables the suite. Default selection is predict only (one billable request).
SWARMAURI_LIVE_TTS_OPERATIONS selects a comma-separated operation list.
All six operations make eight billable requests per model. Never paste credentials or unmasked headers into issues or logs.
See the [verification tracker](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/verification/tts-providers.md).

## License

Apache-2.0. Part of the [Swarmauri SDK](https://github.com/swarmauri/swarmauri-sdk).
