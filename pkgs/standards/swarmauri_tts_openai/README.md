![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

# swarmauri_tts_openai

Standalone alpha openai speech synthesis for Swarmauri. OpenAI `tts-1`, `tts-1-hd` and `gpt-4o-mini-tts`; optional speed, output format and mini-TTS instructions.

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_tts_openai)](https://pepy.tech/projects/swarmauri_tts_openai)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tts_openai.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tts_openai)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_tts_openai)](https://pypi.org/project/swarmauri_tts_openai/)
[![License](https://img.shields.io/pypi/l/swarmauri_tts_openai)](https://pypi.org/project/swarmauri_tts_openai/)
[![Version](https://img.shields.io/pypi/v/swarmauri_tts_openai?label=swarmauri_tts_openai&color=green)](https://pypi.org/project/swarmauri_tts_openai/)

## Features

- File generation through `predict` and `apredict`.
- Incremental audio through `stream` and `astream`, with connection cleanup.
- Synchronous batch execution and bounded async batches.
- Explicit provider URL, model, voice and output settings.
- No automatic retries of potentially billable generation requests.

Streaming yields binary HTTP audio chunks. Hosted buffering and time to first audio have not been measured.

## Installation

```bash
uv add --prerelease allow swarmauri_tts_openai
```

```bash
pip install --pre swarmauri_tts_openai
```

This source candidate requires the companion `swarmauri_base` release providing
`HttpTTSMixin` (`>=0.11.0.dev8`). Release that dependency before these wheels.

## Usage

Set `OPENAI_API_KEY` in your environment, then:

```python
import os
from swarmauri_tts_openai import OpenaiTTS

provider = OpenaiTTS(
    api_key=os.environ["OPENAI_API_KEY"],
    name="tts-1",
    voice="alloy",
)
path = provider.predict("Welcome to Swarmauri.", "welcome.mp3")
# await provider.apredict(text, audio_path)
# provider.batch({"First message": "first.mp3"})
# await provider.abatch({"Second message": "second.mp3"}, max_concurrent=2)
# Iterate provider.stream(text), or async-iterate provider.astream(text).
```

Choose voices appropriate to the selected model. The filename does not change the
codec: select `response_format` explicitly and use a matching extension. The
component implements `TTSBase` and can be passed to `TextToSpeechAgent`.

## Verification and alpha status

Live API behavior has **not** been verified by this change.
Tracked in [verification issue #6268](https://github.com/swarmauri/swarmauri-sdk/issues/6268). Offline tests validate
payloads, errors and transport behavior; they do not establish speech quality,
model availability or actual billed cost. Keep `Development Status :: 3 - Alpha`
in `pyproject.toml` until maintainers review live verification evidence.

Live tests are disabled even if a key is present. To explicitly authorize one
billable synthesis request, set `SWARMAURI_LIVE_TTS=1`, set `OPENAI_API_KEY` privately,
and run this package's `tests/i9n` suite. Only `predict` runs by default. Set
`SWARMAURI_LIVE_TTS_OPERATIONS=predict,apredict,stream,astream,batch,abatch` to
exercise all operations (eight requests including the two-item batches). Set
`SWARMAURI_TTS_MODEL` and `SWARMAURI_TTS_VOICE` to select another model/voice.
Do not paste API keys into issues or logs.

Verification issue links and evidence requirements are maintained in
[the verification guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/verification/tts-providers.md).

## License

Apache-2.0. Part of the [Swarmauri SDK](https://github.com/swarmauri/swarmauri-sdk).
