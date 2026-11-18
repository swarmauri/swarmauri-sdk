![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

# swarmauri_tts_deepinfra

Standalone alpha deepinfra speech synthesis for Swarmauri. DeepInfra `/v1/audio/speech`: Kokoro, Chatterbox Turbo/Multilingual and Orpheus. Catalog model presence does not establish working coverage through this endpoint; verify each model. Native inference, voice cloning and voice design are excluded.

[![Downloads](https://static.pepy.tech/badge/swarmauri_tts_deepinfra)](https://pepy.tech/projects/swarmauri_tts_deepinfra)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tts_deepinfra.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tts_deepinfra)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://pypi.org/project/swarmauri_tts_deepinfra/)
[![License](https://img.shields.io/pypi/l/swarmauri_tts_deepinfra)](https://pypi.org/project/swarmauri_tts_deepinfra/)
[![Version](https://img.shields.io/pypi/v/swarmauri_tts_deepinfra)](https://pypi.org/project/swarmauri_tts_deepinfra/)

## Features

- File generation through `predict` and `apredict`.
- Incremental audio through `stream` and `astream`, with connection cleanup.
- Synchronous batch execution and bounded async batches.
- Explicit provider URL, model, voice and output settings.
- No automatic retries of potentially billable generation requests.

Streaming yields binary HTTP audio chunks. Hosted buffering and time to first audio have not been measured.

## Installation

```bash
uv add --prerelease allow swarmauri_tts_deepinfra
```

```bash
pip install --pre swarmauri_tts_deepinfra
```

This source candidate requires the companion `swarmauri_base` release providing
`HttpTTSMixin` (`>=0.11.0.dev8`). Release that dependency before these wheels.

## Usage

Set `DEEPINFRA_API_KEY` in your environment, then:

```python
import os
from swarmauri_tts_deepinfra import DeepInfraTTS

provider = DeepInfraTTS(
    api_key=os.environ["DEEPINFRA_API_KEY"],
    name="hexgrad/Kokoro-82M",
    voice="af_heart",
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
Tracked in [verification issue #6269](https://github.com/swarmauri/swarmauri-sdk/issues/6269). Offline tests validate
payloads, errors and transport behavior; they do not establish speech quality,
model availability or actual billed cost. Keep `Development Status :: 3 - Alpha`
in `pyproject.toml` until maintainers review live verification evidence.

Live tests are disabled even if a key is present. To explicitly authorize one
billable synthesis request, set `SWARMAURI_LIVE_TTS=1`, set `DEEPINFRA_API_KEY` privately,
and run this package's `tests/i9n` suite. Only `predict` runs by default. Set
`SWARMAURI_LIVE_TTS_OPERATIONS=predict,apredict,stream,astream,batch,abatch` to
exercise all operations (eight requests including the two-item batches). Set
`SWARMAURI_TTS_MODEL` and `SWARMAURI_TTS_VOICE` to select another model/voice.
Do not paste API keys into issues or logs.

Verification issue links and evidence requirements are maintained in
[the verification guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/verification/tts-providers.md).

## License

Apache-2.0. Part of the [Swarmauri SDK](https://github.com/swarmauri/swarmauri-sdk).
