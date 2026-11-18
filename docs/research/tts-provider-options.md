# TTS provider options

Checked against provider documentation on 2026-11-17. This is an API and
integration inventory, not a listening test or latency benchmark. Model catalogs
and prices can change. Keep `gpt-4o-mini-tts` as the immediate migration option;
evaluate DeepInfra next rather than assuming OpenAI is the only replacement.

## Existing Swarmauri adapters

The current SDK has `OpenaiTTS` and `HyperbolicTTS` under
`swarmauri_standard.tts`. The former supports `tts-1`, `tts-1-hd` and
`gpt-4o-mini-tts`. Hyperbolic's adapter calls `/v1/audio/generation` and accepts
language, speaker and speed; its current hosted availability was not verified.
The older LLM-named audio wrappers are compatibility surfaces.

No dedicated DeepInfra, Together, ElevenLabs, Cartesia, Deepgram, Gemini TTS,
Polly or Azure Speech `TTSBase` adapter was found in this checkout. Existing LLM
integrations with these vendors do not establish TTS support. `OpenaiTTS` has a
fixed OpenAI URL and model/voice validation, so changing a key alone cannot make
it call an OpenAI-compatible TTS vendor.

## DeepInfra

DeepInfra offers TTS and custom voices. Selected models from its
[live TTS catalog](https://deepinfra.com/models/text-to-speech):

| Model ID | Published price per 1M characters | Candidate use |
| --- | ---: | --- |
| `hexgrad/Kokoro-82M` | $0.99 | Low-cost baseline with preset voices |
| `ResembleAI/chatterbox-turbo` | $1.00 | Expressive speech and cloning evaluation |
| `ResembleAI/chatterbox-multilingual` | $1.00 | Multilingual speech evaluation |
| `canopylabs/orpheus-3b-0.1-ft` | $7.00 | Expressiveness and streaming evaluation |
| `Qwen/Qwen3-TTS` | $20.00 | Preset voices, voice cloning, instruction control |
| `Qwen/Qwen3-TTS-VoiceDesign` | $20.00 | Voices described in natural language |

The catalog also lists HiggsAudioV2.5, Sesame CSM, and partner-hosted Inworld and
MiMo models. Partner/preview entries need separate availability checks. Do not
treat a displayed zero price as a production cost commitment.

[Kokoro's API page](https://deepinfra.com/hexgrad/Kokoro-82M/api) documents the
native inference route. [Chatterbox's voice API](https://deepinfra.com/ResembleAI/chatterbox-turbo/api)
documents uploading a recording to `/v1/voices/add` and receiving a new voice ID.
[Qwen3-TTS](https://deepinfra.com/Qwen/Qwen3-TTS) documents PCM streaming, multiple
output formats and style instructions. Validate streaming format and voice
parameters per model instead of assuming every catalog entry has identical APIs.

## Other providers

| Provider | Models or product | Integration considerations |
| --- | --- | --- |
| [OpenAI](https://developers.openai.com/api/docs/guides/text-to-speech) | `gpt-4o-mini-tts`, `tts-1`, `tts-1-hd` | Existing SDK adapter; direct file/async/batch migration |
| [Together AI](https://docs.together.ai/docs/inference/text-to-speech/overview) | Orpheus, Kokoro, Qwen3 TTS CustomVoice | HTTP and WebSocket delivery; raw PCM/mulaw for streaming; WAV/MP3 file delivery |
| [Cartesia](https://docs.cartesia.ai/build-with-cartesia/tts-models/latest.md) | `sonic-3.6` | Realtime candidate; voice cloning available; use a dated snapshot when change control matters |
| [ElevenLabs](https://elevenlabs.io/docs/overview/models/) | `eleven_v4`, `eleven_v4_turbo`, `eleven_flash_v2_5`, `eleven_multilingual_v2` | Narration, expressiveness and realtime choices; check the endpoint required for each model |
| [Deepgram](https://developers.deepgram.com/docs/tts-models) | Aura-2, e.g. `aura-2-thalia-en` | Voice is part of the model ID; telephony/conversation candidate |
| [Google Gemini](https://ai.google.dev/gemini-api/docs/speech-generation) | Gemini TTS family | Single/multi-speaker generation and style control; separate from Gemini Live audio |
| [Amazon Polly](https://docs.aws.amazon.com/polly/latest/dg/neural-voices.html) | Neural voices | AWS-native speech and language/region-specific voice selection |
| [Azure Speech](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/text-to-speech) | Neural and custom voices | Azure-native standard/custom voice workflows |

## Recommended evaluation

1. Keep OpenAI's existing adapter as the immediate supported migration.
2. Prototype a dedicated `DeepInfraTTS` implementing `TTSBase`: start with Kokoro
   and Chatterbox, then Qwen3-TTS for cloning and style controls. Use distinct
   provider configuration; never send one provider's credentials to another.
3. Compare Cartesia Sonic and Deepgram Aura-2 for interactive voice agents;
   compare ElevenLabs for voice cloning and expressive narration.
4. Run the same short dialogue, long narration, names/numbers and multilingual
   prompts. Measure first audio, total generation time, listenability, actual
   billed cost, voice controls, output format and interruption cleanup.

These are integration priorities inferred from documented capabilities. No new
adapter, provider account, paid synthesis run or benchmark is claimed here.
