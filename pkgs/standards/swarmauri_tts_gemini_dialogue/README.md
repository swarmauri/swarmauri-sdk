![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

# swarmauri_tts_gemini_dialogue

Alpha Swarmauri GeminiDialogueTTS component. Speaker-labelled Interactions turns, separate from single-speaker Gemini TTS.

[![Downloads](https://static.pepy.tech/badge/swarmauri_tts_gemini_dialogue)](https://pepy.tech/projects/swarmauri_tts_gemini_dialogue)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tts_gemini_dialogue.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tts_gemini_dialogue)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://pypi.org/project/swarmauri_tts_gemini_dialogue/)
[![License](https://img.shields.io/pypi/l/swarmauri_tts_gemini_dialogue)](https://pypi.org/project/swarmauri_tts_gemini_dialogue/)
[![Version](https://img.shields.io/pypi/v/swarmauri_tts_gemini_dialogue)](https://pypi.org/project/swarmauri_tts_gemini_dialogue/)

## Features

- Structured multi-voice files, async synthesis, streams and bounded batches.
- Provider-specific schemas and local input validation.
- Fixed provider endpoints and no automatic replay of billable requests.
- Python 3.10-3.12; no swarmauri_standard dependency.

## Installation

```bash
uv add --prerelease allow swarmauri_tts_gemini_dialogue
```

```bash
pip install --pre swarmauri_tts_gemini_dialogue
```

This source candidate needs swarmauri_base>=0.11.0.dev11 published first.

## Usage

```python
import os
from swarmauri_tts_gemini_dialogue import GeminiDialogueTTS, GeminiDialogueTurn

provider = GeminiDialogueTTS(
    api_key=os.environ["GEMINI_API_KEY"],
    speaker_voices={"Joe": "Puck", "Jane": "Kore"},
)
turns = (
    GeminiDialogueTurn(text="How are you?", speaker="Joe", style="cheerful"),
    GeminiDialogueTurn(text="Doing well!", speaker="Jane"),
)
path = provider.predict(turns, "dialogue.wav")
# await provider.apredict(turns, "dialogue.wav")
# provider.batch({turns: "dialogue.wav"})
# await provider.abatch({turns: "dialogue.wav"}, max_concurrent=2)
# Iterate provider.stream(turns), or async-iterate provider.astream(turns).
```

## API boundary

This package uses Gemini 3.8 Interactions with separate speaker-labelled text
items and speech_config.speakers. Bind exactly two speaker labels to voice names
or already-provisioned IDs. Every turn must reference a bound speaker. Turn
styles override the optional global style. Tuples of frozen turns can be used
as batch keys. Strings require default_speaker, which must be bound; that mode
can be used by TextToSpeechAgent. The single-speaker voice setting is not
accepted by this component. JSON strings are not parsed into turns.

Models are gemini-3.8-flash-tts and gemini-3.8-flash-lite-tts. The existing
swarmauri_tts_gemini package supplies JSON WAV decoding and SSE raw PCM decoding.
Files are WAV; streams are headerless pcm_s16le, 24 kHz mono and require the
interaction.completed event. store=false is preserved. Old generateContent
previews, Gemini Live and voice management are excluded.

Primary reference: [multi-speaker speech](https://aistudio.google.com/docs/speech-generation#multi-speaker).

## Verification and alpha status

Live API behavior is **unverified**; tracked in [#6308](https://github.com/swarmauri/swarmauri-sdk/issues/6308). No paid synthesis was run. Retain version
0.1.0a1 and Development Status :: 3 - Alpha until maintainers review sufficient
live evidence. Mocked schemas do not prove playable audio, model availability,
voice controls, quality, latency or cost.

Live tests require SWARMAURI_LIVE_TTS=1 plus private GEMINI_API_KEY. The live suite defaults to Puck/Kore; use SWARMAURI_TTS_VOICE and
SWARMAURI_TTS_SECOND_VOICE for account-accessible alternatives. Select the model with SWARMAURI_TTS_MODEL. A key alone never
enables the suite. Default selection is predict only (one billable request).
SWARMAURI_LIVE_TTS_OPERATIONS selects a comma-separated operation list.
All six operations make eight billable requests per model. Never paste credentials or unmasked headers into issues or logs.
See the [verification tracker](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/verification/tts-providers.md).

## License

Apache-2.0. Part of the [Swarmauri SDK](https://github.com/swarmauri/swarmauri-sdk).
