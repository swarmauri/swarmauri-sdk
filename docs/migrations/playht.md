# Migrate from retired TTS providers

Play.ht is discontinued. Both distributions live in pkgs/90-deprecated with their
original distribution/import names, inactive metadata and published retirement
releases. PlayhtTTS and both PlayHTModel compatibility paths warn and fail
locally before credential validation or network access. Historical release
records remain in docs/releases/playht-deprecation.yaml.

Hyperbolic's old api.hyperbolic.xyz/v1 endpoint is also decommissioned.
HyperbolicTTS and HyperbolicAudioTTS imports remain available, but construction
and execution warn and fail locally. The replacement Hyperbolic inference
service documents text/vision, not a compatible replacement audio endpoint.
Do not redirect old audio credentials or payloads to its new chat endpoint.
See the [provider notice](https://www.hyperbolic.ai/docs/inference/overview#moving-from-the-previous-inference-api).

## Select a standalone provider

The [provider inventory](../research/tts-provider-options.md) and
[verification tracker](../verification/tts-providers.md) cover fourteen alpha
packages. OpenAI is 0.1.0a2; the other candidates are 0.1.0a1. All retain
Development Status :: 3 - Alpha. None has been
verified through paid synthesis in this work. Catalog entries, mocked tests
and a successful import do not establish live availability or audio quality.

| API family | Packages |
| --- | --- |
| Existing OpenAI Speech compatibility | swarmauri_tts_openai |
| DeepInfra OpenAI-compatible speech | swarmauri_tts_deepinfra |
| Native DeepInfra schemas | swarmauri_tts_deepinfra_kokoro, swarmauri_tts_deepinfra_qwen3, swarmauri_tts_deepinfra_qwen3_voicedesign |
| Together | swarmauri_tts_together |
| Cartesia | swarmauri_tts_cartesia |
| ElevenLabs single speaker / dialogue | swarmauri_tts_elevenlabs, swarmauri_tts_elevenlabs_dialogue |
| Deepgram Aura REST | swarmauri_tts_deepgram |
| Gemini Interactions single speaker / dialogue | swarmauri_tts_gemini, swarmauri_tts_gemini_dialogue |
| AWS / Azure | swarmauri_tts_polly, swarmauri_tts_azure |

OpenAI's Speech API models have a scheduled shutdown on January 6, 2027.
See [the OpenAI lifecycle guide](openai-speech.md) before selecting that
compatibility adapter for a new deployment. The recommended Realtime model
uses a different API; changing a model name on the Speech endpoint is invalid.

Native DeepInfra packages implement complete JSON-audio file/async/batch
workflows, and intentionally reject streaming locally. The dialogue packages
accept typed turn tuples; do not flatten speaker assignments into JSON text.
Other HTTP/SSE adapters expose their documented streaming contract, which is
not a bidirectional voice session. See [interface boundaries](../research/tts-interface-boundaries.md).

## Existing OpenAI integration

The following keeps the previously selected Speech workflow until its shutdown.
The corrected standalone OpenAI alpha and base releases are published:

```bash
uv add --prerelease allow swarmauri_tts_openai==0.1.0a2
# Or:
pip install --pre swarmauri_tts_openai==0.1.0a2
```

```python
import os
from swarmauri_tts_openai import OpenaiTTS

# Legacy Speech API: scheduled shutdown 2027-01-06.
tts = OpenaiTTS(
    api_key=os.environ["OPENAI_API_KEY"],
    name="gpt-4o-mini-tts",
    voice="alloy",
)
path = tts.predict("Welcome to Swarmauri.", "welcome.mp3")
```

The bundled standard import and legacy OpenAIAudioTTS imports still warn and
forward to this implementation; new code should import the standalone class.
Play.ht and Hyperbolic keys, user IDs and voice IDs cannot be reused. Voice
cloning/listing/deletion require a separately provisioned provider workflow.

## Existing consumers

TextToSpeechAgent accepts strings, text IMessage objects and typed dialogue
turn tuples. Calls remain stateless; async batches are bounded. Set output_path
and explicit batch paths to match the provider's actual codec, such as .wav
for Gemini or native DeepInfra defaults. A filename does not convert audio.

The realtime showcase keeps its Groq transcription/reasoning path, imports
OpenaiTTS from swarmauri_tts_openai, and pins the published SDK/provider versions from PyPI. Its MP3 contract is preserved. Website package
examples and public documentation use canonical imports and show alpha status.

Source merge and package publication do not deploy consumers or verify provider
billing/playability. The downstream PyPI pin change passed offline app tests,
Linux CI, an image build and a network-disabled provider initialization check.

## Publication status (2026-11-18)

OpenAI 0.1.0a2, DeepInfra 0.1.0a1, Together 0.1.0a1 and Gemini 0.1.0a1
are on PyPI, with base 0.11.0.dev12, standard 0.11.0.dev12,
OpenAI community 0.11.0.dev5, Hyperbolic community 0.11.0.dev4 and
TextToSpeechAgent 0.11.0.dev6. Core 0.11.0.dev7, typing 0.11.0.dev4 and
S3FS 0.11.0.dev3 were already available.

The ten remaining provider packages are source candidates: PyPI rejected the
next new project with HTTP 429 (Too many new projects created). Their built
wheels passed offline tests on Python 3.10-3.12, but are not index releases.
The new facade release and its fourteen-provider tts extra must wait for those
prerequisites. Follow [#6314](https://github.com/swarmauri/swarmauri-sdk/issues/6314)
and [release evidence](../releases/tts-alpha-2026-11-18.yaml).

OpenAI 0.1.0a1 is superseded by 0.1.0a2, which constrains HTTPX to the
supported 0.27-0.28 API. Successful installation is not live API verification;
all fourteen verification issues remain open and all providers remain Alpha.

TextToSpeechAgent 0.11.0.dev6 fixes late provider discovery and preserves
concrete provider fields when serializing an agent. It supersedes 0.11.0.dev5.
