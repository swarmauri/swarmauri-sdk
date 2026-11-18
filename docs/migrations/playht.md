# Migrate from retired TTS providers

Play.ht is discontinued. Both distributions live in pkgs/deprecated with their
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
packages. They remain 0.1.0a1 / Development Status :: 3 - Alpha. None has been
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
Install the standalone package after its candidate and base releases publish:

```bash
uv add --prerelease allow swarmauri_tts_openai
# Or:
pip install --pre swarmauri_tts_openai
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
OpenaiTTS from swarmauri_tts_openai, and pins the SDK source revision while
candidates are unpublished. Its MP3 contract is preserved. Website package
examples and public documentation use canonical imports and show alpha status.

Source updates do not publish PyPI releases, merge PRs, deploy consumers or
verify provider billing/playability. Release the SDK candidates before replacing
immutable source dependencies with index versions in downstream consumers.
