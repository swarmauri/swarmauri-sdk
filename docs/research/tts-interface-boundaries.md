# TTS package boundaries

Checked on 2026-11-18 using public documentation and unauthenticated model
metadata GETs. No synthesis, listening test or paid request was performed.
All new packages retain version 0.1.0a1 and the Alpha classifier.

## Implemented splits

| Package / component | Why the existing adapter cannot represent it faithfully |
| --- | --- |
| `swarmauri_tts_gemini_dialogue.GeminiDialogueTTS` | Speaker-labelled text items and speech_config.speakers, distinct from single-speaker voice configuration; shares Gemini audio decoding. |
| `swarmauri_tts_elevenlabs_dialogue.ElevenLabsDialogueTTS` | Ordered text/voice pairs, not one voice-specific URL. Dedicated dialogue unary and streaming routes. |
| `swarmauri_tts_deepinfra_kokoro.DeepInfraKokoroTTS` | Native model URL, `text`, a `preset_voice` list for mixing, `output_format`, and complete JSON audio. |
| `swarmauri_tts_deepinfra_qwen3.DeepInfraQwen3TTS` | Native `input`, preset/provisioned `voice`, `language`, optional `instruct` and `response_format`. |
| `swarmauri_tts_deepinfra_qwen3_voicedesign.DeepInfraQwen3VoiceDesignTTS` | Required natural-language voice description, rather than preset or saved voice selection. |

The native packages share JSON audio transport through JsonAudioTTSMixin, not
dependencies on one another or swarmauri_standard. Each owns its own schema and
fixed endpoint. Input/output schema fixtures include the source URL, retrieval
date and model revision. Decoder tests cover base64 and audio data URIs; remote
audio URLs are never fetched. Native stream framing remains unverified, so these
components reject stream/astream locally instead of yielding a buffered file.

Dialogue accepts a tuple of frozen DialogueTurn objects, including as a batch
key. Plain strings remain compatible with TTSBase/TextToSpeechAgent when an
explicit default_voice_id is configured. JSON strings are not parsed as turns.
The component preserves order and voice assignments without mutating provider
configuration during concurrent calls.

Verification: [dialogue #6304](https://github.com/swarmauri/swarmauri-sdk/issues/6304),
[Kokoro #6305](https://github.com/swarmauri/swarmauri-sdk/issues/6305),
[Qwen3 #6306](https://github.com/swarmauri/swarmauri-sdk/issues/6306),
[voice design #6307](https://github.com/swarmauri/swarmauri-sdk/issues/6307),
[Gemini dialogue #6308](https://github.com/swarmauri/swarmauri-sdk/issues/6308).

## Decisions for other boundaries

| Surface | Decision |
| --- | --- |
| Polly standard/neural/long-form/generative engines | Keep one package: they share SynthesizeSpeech. SSML is a future input mode, not a reason to copy the package per engine. |
| Azure stock voice choices and encoding settings | Keep one regional REST package. Extra stock voices do not create a different wire contract. |
| Gemini 3.8 single/multi-speaker configuration | Separate dialogue package because labelled turns and the speakers object form a different input contract. Reuse the single-speaker package's JSON/SSE audio decoding. |
| Gemini generateContent TTS previews | Different contract, but no new adapter added around models approaching retirement. Google's current schedule lists December 18, 2026 as the earliest shutdown for the 2.5/3.1 TTS previews and recommends 3.8 replacements. |
| Bidirectional WebSocket speech and Gemini Live | Genuinely different session/turn/interruption lifecycle. Future packages need an explicit session interface; they are not implemented by pretending TTSBase HTTP chunks are bidirectional sessions. |
| Voice creation/upload, custom-voice deployment and synthesis jobs | Separate management/job workflows. No placeholder packages or hidden uploads/jobs are introduced in this change. |

The existing DeepInfra OpenAI-compatible adapter now follows the model's
documented `/v1/openai/audio/speech` route. Its own verification remains pending
in [#6269](https://github.com/swarmauri/swarmauri-sdk/issues/6269); working native
inference would not establish compatibility with that endpoint.

## Primary sources

- [ElevenLabs dialogue](https://elevenlabs.io/docs/api-reference/text-to-dialogue/convert)
  and [streaming](https://elevenlabs.io/docs/api-reference/text-to-dialogue/stream).
- [Native Kokoro schema](https://api.deepinfra.com/models/hexgrad/Kokoro-82M)
  and [provider decoding example](https://deepinfra.com/blog/talking-images).
- [Native Qwen3 schema](https://api.deepinfra.com/models/Qwen/Qwen3-TTS)
  and [voice-design schema](https://api.deepinfra.com/models/Qwen/Qwen3-TTS-VoiceDesign).
- [DeepInfra OpenAI-compatible example](https://api.deepinfra.com/models/hexgrad/Kokoro-82M/docs/openai-tts-http.md).
- [Gemini multi-speaker schema](https://aistudio.google.com/docs/speech-generation#multi-speaker).
- [Gemini deprecation schedule](https://ai.google.dev/gemini-api/docs/deprecations).
