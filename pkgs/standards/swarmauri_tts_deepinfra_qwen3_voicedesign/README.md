![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

# swarmauri_tts_deepinfra_qwen3_voicedesign

Alpha Swarmauri DeepInfraQwen3VoiceDesignTTS component. Native Qwen3 voice-description synthesis, separate from preset voice IDs.

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_tts_deepinfra_qwen3_voicedesign)](https://pepy.tech/projects/swarmauri_tts_deepinfra_qwen3_voicedesign)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tts_deepinfra_qwen3_voicedesign.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tts_deepinfra_qwen3_voicedesign)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_tts_deepinfra_qwen3_voicedesign)](https://pypi.org/project/swarmauri_tts_deepinfra_qwen3_voicedesign/)
[![License](https://img.shields.io/pypi/l/swarmauri_tts_deepinfra_qwen3_voicedesign)](https://pypi.org/project/swarmauri_tts_deepinfra_qwen3_voicedesign/)
[![Version](https://img.shields.io/pypi/v/swarmauri_tts_deepinfra_qwen3_voicedesign?label=swarmauri_tts_deepinfra_qwen3_voicedesign&color=green)](https://pypi.org/project/swarmauri_tts_deepinfra_qwen3_voicedesign/)

## Features

- File synthesis, async synthesis and bounded batches from JSON-encoded audio.
- Provider-specific schemas and local input validation.
- Fixed provider endpoints and no automatic replay of billable requests.
- Python 3.10-3.12; no swarmauri_standard dependency.

## Installation

```bash
uv add --prerelease allow swarmauri_tts_deepinfra_qwen3_voicedesign
```

```bash
pip install --pre swarmauri_tts_deepinfra_qwen3_voicedesign
```

This source candidate needs swarmauri_base>=0.11.0.dev12 published first.

## Usage

```python
import os
from swarmauri_tts_deepinfra_qwen3_voicedesign import DeepInfraQwen3VoiceDesignTTS

provider = DeepInfraQwen3VoiceDesignTTS(
    api_key=os.environ["DEEPINFRA_API_KEY"],
    voice_description="A calm, warm narrator with a low voice",
    language="English",
)
path = provider.predict("Welcome to Swarmauri.", "welcome.wav")
# await provider.apredict(text, audio_path)
# provider.batch({"Hello": "hello.wav"})
# await provider.abatch({"Hello": "hello.wav"}, max_concurrent=2)
```

## API boundary

File responses must contain successful inference status (when reported) and
base64 audio or an audio data URI. URLs are rejected and never downloaded.
The reported output format must match the request. WAV responses need a RIFF/WAVE
header; no transcoding is performed. response_format supports wav (default),
mp3, opus, flac and pcm. Select matching file extensions. The component can be
used with TextToSpeechAgent; set its output_path to match the codec.

stream/astream raise NotImplementedError locally, before an API call. Catalog
streaming claims alone do not establish native framing or codec semantics.
No complete JSON response is presented as an incremental stream. Webhooks,
voice creation/deletion, reference uploads and account management are excluded.
Voice design uses input, required voice_description mapped to voice, language and response_format; text is limited to 4000 characters. The voice value describes a voice in natural language, rather than selecting a preset or saved ID.

Primary reference: [provider API](https://deepinfra.com/Qwen/Qwen3-TTS-VoiceDesign/api).

## Verification and alpha status

Live API behavior is **unverified**; tracked in [#6307](https://github.com/swarmauri/swarmauri-sdk/issues/6307). No paid synthesis was run. Retain version
0.1.0a1 and Development Status :: 3 - Alpha until maintainers review sufficient
live evidence. Mocked schemas do not prove playable audio, model availability,
voice controls, quality, latency or cost.

Live tests require SWARMAURI_LIVE_TTS=1 plus private DEEPINFRA_API_KEY. Configure SWARMAURI_TTS_VOICE_DESCRIPTION
for your account. Select the model with SWARMAURI_TTS_MODEL. A key alone never
enables the suite. Default selection is predict only (one billable request).
SWARMAURI_LIVE_TTS_OPERATIONS selects a comma-separated operation list.
The four supported operations make six billable requests per model. Streaming tests stay skipped. Never paste credentials or unmasked headers into issues or logs.
See the [verification tracker](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/verification/tts-providers.md).

## License

Apache-2.0. Part of the [Swarmauri SDK](https://github.com/swarmauri/swarmauri-sdk).
