# LLM Provider Model and Pricing Links

Last reviewed: 2026-05-23

This file maps the LLM, VLM, STT, and TTS provider model allowlists used by the SDK to the provider documentation that describes supported models and pricing. Pricing changes frequently; treat the pricing links as the source of truth before quoting rates in package README files or release notes.

## AI21

Provider links:

- Models: [AI21 Jamba foundation models](https://docs.ai21.com/docs/jamba-foundation-models)
- API reference: [AI21 Jamba API reference](https://docs.ai21.com/reference/jamba-15-api-ref)
- Pricing: [AI21 pricing](https://www.ai21.com/pricing) and [AI21 usage cost docs](https://docs.ai21.com/docs/usage-cost)

| Model | SDK surface | Model documentation | Pricing documentation |
| --- | --- | --- | --- |
| `jamba-large` | `AI21StudioModel` | [Jamba foundation models](https://docs.ai21.com/docs/jamba-foundation-models) | [AI21 pricing](https://www.ai21.com/pricing) |
| `jamba-mini` | `AI21StudioModel` | [Jamba foundation models](https://docs.ai21.com/docs/jamba-foundation-models) | [AI21 pricing](https://www.ai21.com/pricing) |
| `jamba-large-1.7` | `AI21StudioModel` | [Jamba foundation models](https://docs.ai21.com/docs/jamba-foundation-models) | [AI21 pricing](https://www.ai21.com/pricing) |
| `jamba-mini-2` | `AI21StudioModel` | [Jamba foundation models](https://docs.ai21.com/docs/jamba-foundation-models) | [AI21 pricing](https://www.ai21.com/pricing) |
| `jamba-large-1.7-2025-07` | `AI21StudioModel` | [Jamba foundation models](https://docs.ai21.com/docs/jamba-foundation-models) | [AI21 pricing](https://www.ai21.com/pricing) |
| `jamba-mini-2-2026-01` | `AI21StudioModel` | [Jamba foundation models](https://docs.ai21.com/docs/jamba-foundation-models) | [AI21 pricing](https://www.ai21.com/pricing) |

## Anthropic

Provider links:

- Models: [Claude models](https://docs.anthropic.com/en/docs/about-claude/models)
- Tool use: [Claude tool use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- Pricing: [Claude pricing](https://docs.anthropic.com/en/docs/about-claude/pricing)

| Model | SDK surface | Model documentation | Pricing documentation |
| --- | --- | --- | --- |
| `claude-opus-4-7` | `AnthropicModel` | [Claude models](https://docs.anthropic.com/en/docs/about-claude/models) | [Claude pricing](https://docs.anthropic.com/en/docs/about-claude/pricing) |
| `claude-sonnet-4-6` | `AnthropicModel` | [Claude models](https://docs.anthropic.com/en/docs/about-claude/models) | [Claude pricing](https://docs.anthropic.com/en/docs/about-claude/pricing) |
| `claude-haiku-4-5` | `AnthropicModel` | [Claude models](https://docs.anthropic.com/en/docs/about-claude/models) | [Claude pricing](https://docs.anthropic.com/en/docs/about-claude/pricing) |
| `claude-haiku-4-5-20251001` | `AnthropicModel` | [Claude models](https://docs.anthropic.com/en/docs/about-claude/models) | [Claude pricing](https://docs.anthropic.com/en/docs/about-claude/pricing) |
| `claude-opus-4-1-20250805` | `AnthropicModel`, `AnthropicToolModel` | [Claude models](https://docs.anthropic.com/en/docs/about-claude/models) | [Claude pricing](https://docs.anthropic.com/en/docs/about-claude/pricing) |
| `claude-opus-4-20250514` | `AnthropicModel`, `AnthropicToolModel` | [Claude models](https://docs.anthropic.com/en/docs/about-claude/models) | [Claude pricing](https://docs.anthropic.com/en/docs/about-claude/pricing) |
| `claude-sonnet-4-20250514` | `AnthropicModel`, `AnthropicToolModel` | [Claude models](https://docs.anthropic.com/en/docs/about-claude/models) | [Claude pricing](https://docs.anthropic.com/en/docs/about-claude/pricing) |
| `claude-3-7-sonnet-20250219` | `AnthropicModel`, `AnthropicToolModel` | [Claude models](https://docs.anthropic.com/en/docs/about-claude/models) | [Claude pricing](https://docs.anthropic.com/en/docs/about-claude/pricing) |
| `claude-3-5-haiku-20241022` | `AnthropicModel`, `AnthropicToolModel` | [Claude models](https://docs.anthropic.com/en/docs/about-claude/models) | [Claude pricing](https://docs.anthropic.com/en/docs/about-claude/pricing) |
| `claude-3-haiku-20240307` | `AnthropicModel`, `AnthropicToolModel` | [Claude models](https://docs.anthropic.com/en/docs/about-claude/models) | [Claude pricing](https://docs.anthropic.com/en/docs/about-claude/pricing) |
| `claude-3-7-sonnet-latest` | `AnthropicToolModel` | [Claude models](https://docs.anthropic.com/en/docs/about-claude/models) | [Claude pricing](https://docs.anthropic.com/en/docs/about-claude/pricing) |
| `claude-3-5-haiku-latest` | `AnthropicToolModel` | [Claude models](https://docs.anthropic.com/en/docs/about-claude/models) | [Claude pricing](https://docs.anthropic.com/en/docs/about-claude/pricing) |

## Cerebras

Provider links:

- Models: [Choose a model](https://inference-docs.cerebras.ai/models/choose-a-model)
- Public model API: [Public models](https://inference-docs.cerebras.ai/api-reference/models/public-models)
- Pricing: [Cerebras Inference pricing](https://inference-docs.cerebras.ai/support/pricing)

| Model | SDK surface | Model documentation | Pricing documentation |
| --- | --- | --- | --- |
| `zai-glm-4.7` | `CerebrasModel` | [Public models](https://inference-docs.cerebras.ai/api-reference/models/public-models) | [Pricing](https://inference-docs.cerebras.ai/support/pricing) |
| `gpt-oss-120b` | `CerebrasModel` | [Public models](https://inference-docs.cerebras.ai/api-reference/models/public-models) | [Pricing](https://inference-docs.cerebras.ai/support/pricing) |
| `qwen-3-235b-a22b-instruct-2507` | `CerebrasModel` | [Public models](https://inference-docs.cerebras.ai/api-reference/models/public-models) | [Pricing](https://inference-docs.cerebras.ai/support/pricing) |
| `llama3.1-8b` | `CerebrasModel` | [Public models](https://inference-docs.cerebras.ai/api-reference/models/public-models) | [Pricing](https://inference-docs.cerebras.ai/support/pricing) |

## Cohere

Provider links:

- Models: [Cohere models](https://docs.cohere.com/docs/models)
- Pricing explanation: [How Cohere pricing works](https://docs.cohere.com/docs/how-does-cohere-pricing-work)
- Pricing: [Cohere pricing](https://cohere.com/pricing)

| Model | SDK surface | Model documentation | Pricing documentation |
| --- | --- | --- | --- |
| `command-a-plus-05-2026` | `CohereModel`, `CohereToolModel` | [Cohere models](https://docs.cohere.com/docs/models) | [Cohere pricing](https://cohere.com/pricing) |
| `command-a-03-2025` | `CohereModel`, `CohereToolModel` | [Cohere models](https://docs.cohere.com/docs/models) | [Cohere pricing](https://cohere.com/pricing) |
| `command-a-reasoning-08-2025` | `CohereModel`, `CohereToolModel` | [Cohere models](https://docs.cohere.com/docs/models) | [Cohere pricing](https://cohere.com/pricing) |
| `command-a-translate-08-2025` | `CohereModel`, `CohereToolModel` | [Cohere models](https://docs.cohere.com/docs/models) | [Cohere pricing](https://cohere.com/pricing) |
| `command-a-vision-07-2025` | `CohereModel`, `CohereToolModel` | [Cohere models](https://docs.cohere.com/docs/models) | [Cohere pricing](https://cohere.com/pricing) |
| `command-r7b-12-2024` | `CohereModel`, `CohereToolModel` | [Cohere models](https://docs.cohere.com/docs/models) | [Cohere pricing](https://cohere.com/pricing) |
| `command-r-08-2024` | `CohereModel`, `CohereToolModel` | [Cohere models](https://docs.cohere.com/docs/models) | [Cohere pricing](https://cohere.com/pricing) |
| `command-r-plus-08-2024` | `CohereModel`, `CohereToolModel` | [Cohere models](https://docs.cohere.com/docs/models) | [Cohere pricing](https://cohere.com/pricing) |

## DeepInfra

Provider links:

- Models: [DeepInfra models](https://docs.deepinfra.com/models)
- OpenAI-compatible public model endpoint: [DeepInfra `/v1/openai/models`](https://api.deepinfra.com/v1/openai/models)
- Pricing: per-model prices are exposed on model pages and through model metadata.

| Model | SDK surface | Model documentation | Pricing documentation |
| --- | --- | --- | --- |
| `zai-org/GLM-4.6` | `DeepInfraModel`, dynamic `DeepInfraToolModel` | [DeepInfra models](https://docs.deepinfra.com/models) | [Model catalog/API](https://api.deepinfra.com/v1/openai/models) |
| `deepseek-ai/DeepSeek-V4-Pro` | `DeepInfraModel`, dynamic `DeepInfraToolModel` | [DeepInfra models](https://docs.deepinfra.com/models) | [Model catalog/API](https://api.deepinfra.com/v1/openai/models) |
| `Qwen/Qwen3-30B-A3B` | `DeepInfraModel`, dynamic `DeepInfraToolModel` | [DeepInfra models](https://docs.deepinfra.com/models) | [Model catalog/API](https://api.deepinfra.com/v1/openai/models) |
| `Sao10K/L3-8B-Lunaris-v1-Turbo` | `DeepInfraModel`, dynamic `DeepInfraToolModel` | [DeepInfra models](https://docs.deepinfra.com/models) | [Model catalog/API](https://api.deepinfra.com/v1/openai/models) |
| `Qwen/Qwen3.6-27B` | `DeepInfraModel`, dynamic `DeepInfraToolModel` | [DeepInfra models](https://docs.deepinfra.com/models) | [Model catalog/API](https://api.deepinfra.com/v1/openai/models) |
| `nvidia/Nemotron-3-Nano-30B-A3B` | `DeepInfraModel`, dynamic `DeepInfraToolModel` | [DeepInfra models](https://docs.deepinfra.com/models) | [Model catalog/API](https://api.deepinfra.com/v1/openai/models) |
| `meta-llama/Meta-Llama-3.1-70B-Instruct` | `DeepInfraModel`, dynamic `DeepInfraToolModel` | [DeepInfra models](https://docs.deepinfra.com/models) | [Model catalog/API](https://api.deepinfra.com/v1/openai/models) |
| `ByteDance/Seed-2.0-mini` | `DeepInfraModel`, dynamic `DeepInfraToolModel` | [DeepInfra models](https://docs.deepinfra.com/models) | [Model catalog/API](https://api.deepinfra.com/v1/openai/models) |
| `openai/gpt-oss-120b-Turbo` | `DeepInfraModel`, dynamic `DeepInfraToolModel` | [DeepInfra models](https://docs.deepinfra.com/models) | [Model catalog/API](https://api.deepinfra.com/v1/openai/models) |
| `zai-org/GLM-5.1` | `DeepInfraModel`, dynamic `DeepInfraToolModel` | [DeepInfra models](https://docs.deepinfra.com/models) | [Model catalog/API](https://api.deepinfra.com/v1/openai/models) |
| `Qwen/Qwen3.5-4B` | `DeepInfraModel`, dynamic `DeepInfraToolModel` | [DeepInfra models](https://docs.deepinfra.com/models) | [Model catalog/API](https://api.deepinfra.com/v1/openai/models) |
| `Qwen/Qwen3-235B-A22B-Instruct-2507` | `DeepInfraModel`, dynamic `DeepInfraToolModel` | [DeepInfra models](https://docs.deepinfra.com/models) | [Model catalog/API](https://api.deepinfra.com/v1/openai/models) |
| `anthropic/claude-opus-4-7` | `DeepInfraModel`, dynamic `DeepInfraToolModel` | [DeepInfra models](https://docs.deepinfra.com/models) | [Model catalog/API](https://api.deepinfra.com/v1/openai/models) |
| `google/gemini-3.1-flash-lite` | `DeepInfraModel`, dynamic `DeepInfraToolModel` | [DeepInfra models](https://docs.deepinfra.com/models) | [Model catalog/API](https://api.deepinfra.com/v1/openai/models) |
| `meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8` | `DeepInfraModel`, dynamic `DeepInfraToolModel` | [DeepInfra models](https://docs.deepinfra.com/models) | [Model catalog/API](https://api.deepinfra.com/v1/openai/models) |
| `google/gemma-3-12b-it` | `DeepInfraModel`, dynamic `DeepInfraToolModel` | [DeepInfra models](https://docs.deepinfra.com/models) | [Model catalog/API](https://api.deepinfra.com/v1/openai/models) |
| `google/gemini-3.1-pro` | `DeepInfraModel`, dynamic `DeepInfraToolModel` | [DeepInfra models](https://docs.deepinfra.com/models) | [Model catalog/API](https://api.deepinfra.com/v1/openai/models) |
| `mistralai/Mistral-Small-3.2-24B-Instruct-2506` | `DeepInfraModel`, dynamic `DeepInfraToolModel` | [DeepInfra models](https://docs.deepinfra.com/models) | [Model catalog/API](https://api.deepinfra.com/v1/openai/models) |
| `Qwen/Qwen3-Max-Thinking` | `DeepInfraModel`, dynamic `DeepInfraToolModel` | [DeepInfra models](https://docs.deepinfra.com/models) | [Model catalog/API](https://api.deepinfra.com/v1/openai/models) |
| `google/gemini-2.5-flash` | `DeepInfraModel`, dynamic `DeepInfraToolModel` | [DeepInfra models](https://docs.deepinfra.com/models) | [Model catalog/API](https://api.deepinfra.com/v1/openai/models) |
| `nvidia/NVIDIA-Nemotron-Nano-9B-v2` | `DeepInfraModel`, dynamic `DeepInfraToolModel` | [DeepInfra models](https://docs.deepinfra.com/models) | [Model catalog/API](https://api.deepinfra.com/v1/openai/models) |
| `Qwen/Qwen3.5-2B` | `DeepInfraModel`, dynamic `DeepInfraToolModel` | [DeepInfra models](https://docs.deepinfra.com/models) | [Model catalog/API](https://api.deepinfra.com/v1/openai/models) |
| `deepseek-ai/DeepSeek-V3` | `DeepInfraModel`, dynamic `DeepInfraToolModel` | [DeepInfra models](https://docs.deepinfra.com/models) | [Model catalog/API](https://api.deepinfra.com/v1/openai/models) |
| `NousResearch/Hermes-3-Llama-3.1-70B` | `DeepInfraModel`, dynamic `DeepInfraToolModel` | [DeepInfra models](https://docs.deepinfra.com/models) | [Model catalog/API](https://api.deepinfra.com/v1/openai/models) |
| `Sao10K/L3.1-70B-Euryale-v2.2` | `DeepInfraModel`, dynamic `DeepInfraToolModel` | [DeepInfra models](https://docs.deepinfra.com/models) | [Model catalog/API](https://api.deepinfra.com/v1/openai/models) |
| `meta-llama/Meta-Llama-3.1-8B-Instruct` | `DeepInfraModel`, dynamic `DeepInfraToolModel` | [DeepInfra models](https://docs.deepinfra.com/models) | [Model catalog/API](https://api.deepinfra.com/v1/openai/models) |
| `zai-org/GLM-5` | `DeepInfraModel`, dynamic `DeepInfraToolModel` | [DeepInfra models](https://docs.deepinfra.com/models) | [Model catalog/API](https://api.deepinfra.com/v1/openai/models) |
| `stepfun-ai/Step-3.5-Flash` | `DeepInfraModel`, dynamic `DeepInfraToolModel` | [DeepInfra models](https://docs.deepinfra.com/models) | [Model catalog/API](https://api.deepinfra.com/v1/openai/models) |
| `Qwen/Qwen3-Coder-480B-A35B-Instruct-Turbo` | `DeepInfraModel`, dynamic `DeepInfraToolModel` | [DeepInfra models](https://docs.deepinfra.com/models) | [Model catalog/API](https://api.deepinfra.com/v1/openai/models) |
| `google/gemini-2.5-pro` | `DeepInfraModel`, dynamic `DeepInfraToolModel` | [DeepInfra models](https://docs.deepinfra.com/models) | [Model catalog/API](https://api.deepinfra.com/v1/openai/models) |
| `meta-llama/Llama-3.3-70B-Instruct-Turbo` | `DeepInfraModel`, dynamic `DeepInfraToolModel` | [DeepInfra models](https://docs.deepinfra.com/models) | [Model catalog/API](https://api.deepinfra.com/v1/openai/models) |

## DeepSeek

Provider links:

- Models and pricing: [DeepSeek pricing details](https://api-docs.deepseek.com/quick_start/pricing-details-usd)
- API docs: [DeepSeek API docs](https://api-docs.deepseek.com/)

| Model | SDK surface | Model documentation | Pricing documentation |
| --- | --- | --- | --- |
| `deepseek-v4-flash` | `DeepSeekModel` | [DeepSeek API docs](https://api-docs.deepseek.com/) | [Pricing details](https://api-docs.deepseek.com/quick_start/pricing-details-usd) |
| `deepseek-v4-pro` | `DeepSeekModel` | [DeepSeek API docs](https://api-docs.deepseek.com/) | [Pricing details](https://api-docs.deepseek.com/quick_start/pricing-details-usd) |
| `deepseek-chat` | `DeepSeekModel` | [DeepSeek API docs](https://api-docs.deepseek.com/) | [Pricing details](https://api-docs.deepseek.com/quick_start/pricing-details-usd) |
| `deepseek-reasoner` | `DeepSeekModel` | [DeepSeek API docs](https://api-docs.deepseek.com/) | [Pricing details](https://api-docs.deepseek.com/quick_start/pricing-details-usd) |

## fal.ai

Provider links:

- Model APIs: [fal Model APIs](https://docs.fal.ai/model-apis)
- Vision model catalog: [fal vision models](https://fal.ai/models?categories=vision)
- Pricing: [fal pricing docs](https://docs.fal.ai/documentation/model-apis/pricing)

| Model | SDK surface | Model documentation | Pricing documentation |
| --- | --- | --- | --- |
| `fal-ai/got-ocr/v2` | `FalAIVisionModel` | [fal vision catalog](https://fal.ai/models?categories=vision) | [fal pricing](https://docs.fal.ai/documentation/model-apis/pricing) |
| `fal-ai/any-llm/vision` | `FalAIVisionModel` | [fal vision catalog](https://fal.ai/models?categories=vision) | [fal pricing](https://docs.fal.ai/documentation/model-apis/pricing) |
| `fal-ai/llavav15-13b` | `FalAIVisionModel` | [fal vision catalog](https://fal.ai/models?categories=vision) | [fal pricing](https://docs.fal.ai/documentation/model-apis/pricing) |
| `fal-ai/llava-next` | `FalAIVisionModel` | [fal vision catalog](https://fal.ai/models?categories=vision) | [fal pricing](https://docs.fal.ai/documentation/model-apis/pricing) |
| `fal-ai/imageutils/nsfw` | `FalAIVisionModel` | [fal vision catalog](https://fal.ai/models?categories=vision) | [fal pricing](https://docs.fal.ai/documentation/model-apis/pricing) |
| `fal-ai/moondream/batched` | `FalAIVisionModel` | [fal vision catalog](https://fal.ai/models?categories=vision) | [fal pricing](https://docs.fal.ai/documentation/model-apis/pricing) |
| `fal-ai/florence-2-large/caption` | `FalAIVisionModel` | [fal vision catalog](https://fal.ai/models?categories=vision) | [fal pricing](https://docs.fal.ai/documentation/model-apis/pricing) |
| `fal-ai/florence-2-large/detailed-caption` | `FalAIVisionModel` | [fal vision catalog](https://fal.ai/models?categories=vision) | [fal pricing](https://docs.fal.ai/documentation/model-apis/pricing) |
| `fal-ai/florence-2-large/more-detailed-caption` | `FalAIVisionModel` | [fal vision catalog](https://fal.ai/models?categories=vision) | [fal pricing](https://docs.fal.ai/documentation/model-apis/pricing) |
| `fal-ai/florence-2-large/region-to-category` | `FalAIVisionModel` | [fal vision catalog](https://fal.ai/models?categories=vision) | [fal pricing](https://docs.fal.ai/documentation/model-apis/pricing) |
| `fal-ai/florence-2-large/ocr` | `FalAIVisionModel` | [fal vision catalog](https://fal.ai/models?categories=vision) | [fal pricing](https://docs.fal.ai/documentation/model-apis/pricing) |
| `fal-ai/sa2va/8b/image` | `FalAIVisionModel` | [fal vision catalog](https://fal.ai/models?categories=vision) | [fal pricing](https://docs.fal.ai/documentation/model-apis/pricing) |
| `fal-ai/sa2va/8b/video` | `FalAIVisionModel` | [fal vision catalog](https://fal.ai/models?categories=vision) | [fal pricing](https://docs.fal.ai/documentation/model-apis/pricing) |
| `fal-ai/sa2va/4b/video` | `FalAIVisionModel` | [fal vision catalog](https://fal.ai/models?categories=vision) | [fal pricing](https://docs.fal.ai/documentation/model-apis/pricing) |
| `fal-ai/sa2va/4b/image` | `FalAIVisionModel` | [fal vision catalog](https://fal.ai/models?categories=vision) | [fal pricing](https://docs.fal.ai/documentation/model-apis/pricing) |
| `fal-ai/mini-cpm` | `FalAIVisionModel` | [fal vision catalog](https://fal.ai/models?categories=vision) | [fal pricing](https://docs.fal.ai/documentation/model-apis/pricing) |
| `fal-ai/moondream-next` | `FalAIVisionModel` | [fal vision catalog](https://fal.ai/models?categories=vision) | [fal pricing](https://docs.fal.ai/documentation/model-apis/pricing) |
| `fal-ai/moondream-next/batch` | `FalAIVisionModel` | [fal vision catalog](https://fal.ai/models?categories=vision) | [fal pricing](https://docs.fal.ai/documentation/model-apis/pricing) |

## Gemini

Provider links:

- Models: [Gemini API models](https://ai.google.dev/gemini-api/docs/models)
- Pricing: [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)

| Model | SDK surface | Model documentation | Pricing documentation |
| --- | --- | --- | --- |
| `gemini-3-pro-preview` | `GeminiProModel`, `GeminiToolModel` | [Gemini models](https://ai.google.dev/gemini-api/docs/models) | [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| `gemini-2.5-pro` | `GeminiProModel`, `GeminiToolModel` | [Gemini models](https://ai.google.dev/gemini-api/docs/models) | [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| `gemini-2.5-flash` | `GeminiProModel`, `GeminiToolModel` | [Gemini models](https://ai.google.dev/gemini-api/docs/models) | [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| `gemini-2.5-flash-lite` | `GeminiProModel`, `GeminiToolModel` | [Gemini models](https://ai.google.dev/gemini-api/docs/models) | [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| `gemini-2.0-flash` | `GeminiProModel`, `GeminiToolModel` | [Gemini models](https://ai.google.dev/gemini-api/docs/models) | [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing) |
| `gemini-2.0-flash-lite` | `GeminiProModel`, `GeminiToolModel` | [Gemini models](https://ai.google.dev/gemini-api/docs/models) | [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing) |

## Groq

Provider links:

- Models: [Groq models](https://console.groq.com/docs/models)
- Tool use: [Groq tool use](https://console.groq.com/docs/tool-use)
- Speech-to-text: [Groq speech-to-text](https://console.groq.com/docs/speech-to-text)
- Pricing: [Groq pricing](https://groq.com/pricing/)

| Model | SDK surface | Model documentation | Pricing documentation |
| --- | --- | --- | --- |
| `meta-llama/llama-4-maverick-17b-128e-instruct` | `GroqModel`, `GroqToolModel`, `GroqVisionModel` | [Groq models](https://console.groq.com/docs/models) | [Groq pricing](https://groq.com/pricing/) |
| `meta-llama/llama-4-scout-17b-16e-instruct` | `GroqModel`, `GroqToolModel`, `GroqVisionModel` | [Groq models](https://console.groq.com/docs/models) | [Groq pricing](https://groq.com/pricing/) |
| `llama-3.3-70b-versatile` | `GroqModel`, `GroqToolModel` | [Groq models](https://console.groq.com/docs/models) | [Groq pricing](https://groq.com/pricing/) |
| `llama-3.1-8b-instant` | `GroqModel`, `GroqToolModel` | [Groq models](https://console.groq.com/docs/models) | [Groq pricing](https://groq.com/pricing/) |
| `moonshotai/kimi-k2-instruct` | `GroqModel`, `GroqToolModel` | [Groq models](https://console.groq.com/docs/models) | [Groq pricing](https://groq.com/pricing/) |
| `moonshotai/kimi-k2-instruct-0905` | `GroqToolModel` | [Groq models](https://console.groq.com/docs/models) | [Groq pricing](https://groq.com/pricing/) |
| `qwen/qwen3-32b` | `GroqModel` | [Groq models](https://console.groq.com/docs/models) | [Groq pricing](https://groq.com/pricing/) |
| `deepseek-r1-distill-llama-70b` | `GroqModel` | [Groq models](https://console.groq.com/docs/models) | [Groq pricing](https://groq.com/pricing/) |
| `meta-llama/llama-guard-4-12b` | `GroqModel` | [Groq models](https://console.groq.com/docs/models) | [Groq pricing](https://groq.com/pricing/) |
| `openai/gpt-oss-120b` | `GroqModel`, `GroqToolModel` | [Groq models](https://console.groq.com/docs/models) | [Groq pricing](https://groq.com/pricing/) |
| `openai/gpt-oss-20b` | `GroqModel`, `GroqToolModel` | [Groq models](https://console.groq.com/docs/models) | [Groq pricing](https://groq.com/pricing/) |
| `whisper-large-v3-turbo` | `GroqAIAudio` | [Groq speech-to-text](https://console.groq.com/docs/speech-to-text) | [Groq pricing](https://groq.com/pricing/) |
| `distil-whisper-large-v3-en` | `GroqAIAudio` | [Groq speech-to-text](https://console.groq.com/docs/speech-to-text) | [Groq pricing](https://groq.com/pricing/) |
| `whisper-large-v3` | `GroqAIAudio` | [Groq speech-to-text](https://console.groq.com/docs/speech-to-text) | [Groq pricing](https://groq.com/pricing/) |

## Hugging Face Whisper

Provider links:

- Model card: [openai/whisper-large-v3](https://huggingface.co/openai/whisper-large-v3)
- Inference Providers: [Hugging Face Inference Providers](https://huggingface.co/docs/inference-providers/index)
- Pricing: [Hugging Face Inference pricing](https://huggingface.co/docs/api-inference/en/pricing)

| Model | SDK surface | Model documentation | Pricing documentation |
| --- | --- | --- | --- |
| `openai/whisper-large-v3` | `WhisperLargeModel` | [Model card](https://huggingface.co/openai/whisper-large-v3) | [Inference pricing](https://huggingface.co/docs/api-inference/en/pricing) |

## Hyperbolic

Provider links:

- Models: [Hyperbolic supported models](https://docs.hyperbolic.xyz/docs/supported-models)
- Inference overview: [Hyperbolic inference overview](https://www.hyperbolic.ai/docs/inference/overview)
- Pricing: [Hyperbolic inference pricing](https://docs.hyperbolic.xyz/docs/hyperbolic-ai-inference-pricing)

| Model | SDK surface | Model documentation | Pricing documentation |
| --- | --- | --- | --- |
| `openai/gpt-oss-120b` | `HyperbolicModel` | [Supported models](https://docs.hyperbolic.xyz/docs/supported-models) | [Inference pricing](https://docs.hyperbolic.xyz/docs/hyperbolic-ai-inference-pricing) |
| `openai/gpt-oss-20b` | `HyperbolicModel` | [Supported models](https://docs.hyperbolic.xyz/docs/supported-models) | [Inference pricing](https://docs.hyperbolic.xyz/docs/hyperbolic-ai-inference-pricing) |
| `Qwen/Qwen3-Coder-480B-A35B-Instruct` | `HyperbolicModel` | [Supported models](https://docs.hyperbolic.xyz/docs/supported-models) | [Inference pricing](https://docs.hyperbolic.xyz/docs/hyperbolic-ai-inference-pricing) |
| `Qwen/Qwen3-235B-A22B-Instruct-2507` | `HyperbolicModel` | [Supported models](https://docs.hyperbolic.xyz/docs/supported-models) | [Inference pricing](https://docs.hyperbolic.xyz/docs/hyperbolic-ai-inference-pricing) |
| `moonshotai/Kimi-K2-Instruct` | `HyperbolicModel` | [Supported models](https://docs.hyperbolic.xyz/docs/supported-models) | [Inference pricing](https://docs.hyperbolic.xyz/docs/hyperbolic-ai-inference-pricing) |
| `deepseek-ai/DeepSeek-R1-0528` | `HyperbolicModel` | [Supported models](https://docs.hyperbolic.xyz/docs/supported-models) | [Inference pricing](https://docs.hyperbolic.xyz/docs/hyperbolic-ai-inference-pricing) |
| `Qwen/Qwen3-235B-A22B` | `HyperbolicModel` | [Supported models](https://docs.hyperbolic.xyz/docs/supported-models) | [Inference pricing](https://docs.hyperbolic.xyz/docs/hyperbolic-ai-inference-pricing) |
| `deepseek-ai/DeepSeek-V3-0324` | `HyperbolicModel` | [Supported models](https://docs.hyperbolic.xyz/docs/supported-models) | [Inference pricing](https://docs.hyperbolic.xyz/docs/hyperbolic-ai-inference-pricing) |
| `meta-llama/Meta-Llama-3-70B-Instruct` | `HyperbolicModel` | [Supported models](https://docs.hyperbolic.xyz/docs/supported-models) | [Inference pricing](https://docs.hyperbolic.xyz/docs/hyperbolic-ai-inference-pricing) |
| `meta-llama/Meta-Llama-3.1-70B-Instruct` | `HyperbolicModel` | [Supported models](https://docs.hyperbolic.xyz/docs/supported-models) | [Inference pricing](https://docs.hyperbolic.xyz/docs/hyperbolic-ai-inference-pricing) |
| `meta-llama/Meta-Llama-3.1-8B-Instruct` | `HyperbolicModel` | [Supported models](https://docs.hyperbolic.xyz/docs/supported-models) | [Inference pricing](https://docs.hyperbolic.xyz/docs/hyperbolic-ai-inference-pricing) |
| `meta-llama/Meta-Llama-3.1-405B-FP8` | `HyperbolicModel` | [Supported models](https://docs.hyperbolic.xyz/docs/supported-models) | [Inference pricing](https://docs.hyperbolic.xyz/docs/hyperbolic-ai-inference-pricing) |
| `meta-llama/Meta-Llama-3.1-405B-Instruct` | `HyperbolicModel` | [Supported models](https://docs.hyperbolic.xyz/docs/supported-models) | [Inference pricing](https://docs.hyperbolic.xyz/docs/hyperbolic-ai-inference-pricing) |
| `Qwen/Qwen2.5-VL-72B-Instruct` | `HyperbolicVisionModel` | [Supported models](https://docs.hyperbolic.xyz/docs/supported-models) | [Inference pricing](https://docs.hyperbolic.xyz/docs/hyperbolic-ai-inference-pricing) |
| `Qwen/Qwen2.5-VL-7B-Instruct` | `HyperbolicVisionModel` | [Supported models](https://docs.hyperbolic.xyz/docs/supported-models) | [Inference pricing](https://docs.hyperbolic.xyz/docs/hyperbolic-ai-inference-pricing) |
| `mistralai/Pixtral-12B-2409` | `HyperbolicVisionModel` | [Supported models](https://docs.hyperbolic.xyz/docs/supported-models) | [Inference pricing](https://docs.hyperbolic.xyz/docs/hyperbolic-ai-inference-pricing) |

## LeptonAI

Provider links:

- Playground: [Lepton AI playground](https://www.lepton.ai/playground)
- Current public pricing status: Lepton's original public serverless model catalog has limited public documentation; verify account-specific pricing in the provider dashboard before publishing rates.

| Model | SDK surface | Model documentation | Pricing documentation |
| --- | --- | --- | --- |
| `llama2-13b` | `LeptonAIModel` | [Lepton AI playground](https://www.lepton.ai/playground) | Provider dashboard |
| `llama3-1-405b` | `LeptonAIModel` | [Lepton AI playground](https://www.lepton.ai/playground) | Provider dashboard |
| `llama3-1-70b` | `LeptonAIModel` | [Lepton AI playground](https://www.lepton.ai/playground) | Provider dashboard |
| `llama3-1-8b` | `LeptonAIModel` | [Lepton AI playground](https://www.lepton.ai/playground) | Provider dashboard |
| `llama3-70b` | `LeptonAIModel` | [Lepton AI playground](https://www.lepton.ai/playground) | Provider dashboard |
| `llama3-8b` | `LeptonAIModel` | [Lepton AI playground](https://www.lepton.ai/playground) | Provider dashboard |
| `mixtral-8x7b` | `LeptonAIModel` | [Lepton AI playground](https://www.lepton.ai/playground) | Provider dashboard |
| `mistral-7b` | `LeptonAIModel` | [Lepton AI playground](https://www.lepton.ai/playground) | Provider dashboard |
| `nous-hermes-llama2-13b` | `LeptonAIModel` | [Lepton AI playground](https://www.lepton.ai/playground) | Provider dashboard |
| `openchat-3-5` | `LeptonAIModel` | [Lepton AI playground](https://www.lepton.ai/playground) | Provider dashboard |
| `qwen2-72b` | `LeptonAIModel` | [Lepton AI playground](https://www.lepton.ai/playground) | Provider dashboard |
| `toppy-m-7b` | `LeptonAIModel` | [Lepton AI playground](https://www.lepton.ai/playground) | Provider dashboard |
| `wizardlm-2-7b` | `LeptonAIModel` | [Lepton AI playground](https://www.lepton.ai/playground) | Provider dashboard |
| `wizardlm-2-8x22b` | `LeptonAIModel` | [Lepton AI playground](https://www.lepton.ai/playground) | Provider dashboard |

## llama.cpp

Provider links:

- Runtime: [llama.cpp](https://github.com/ggml-org/llama.cpp)
- Pricing: no hosted provider pricing; cost depends on local hardware or the user's chosen hosting environment.

| Model | SDK surface | Model documentation | Pricing documentation |
| --- | --- | --- | --- |
| User-supplied local model path | `LlamaCppModel` | [llama.cpp](https://github.com/ggml-org/llama.cpp) | Not applicable |

## Mistral

Provider links:

- Models: [Mistral model docs](https://docs.mistral.ai/models)
- Function calling models: [Mistral function calling](https://docs.mistral.ai/capabilities/function_calling/)
- Pricing: [Mistral pricing](https://mistral.ai/pricing)

| Model | SDK surface | Model documentation | Pricing documentation |
| --- | --- | --- | --- |
| `mistral-medium-2508` | `MistralModel`, `MistralToolModel` | [Mistral models](https://docs.mistral.ai/models) | [Mistral pricing](https://mistral.ai/pricing) |
| `magistral-medium-2507` | `MistralModel` | [Mistral models](https://docs.mistral.ai/models) | [Mistral pricing](https://mistral.ai/pricing) |
| `codestral-2508` | `MistralModel`, `MistralToolModel` | [Mistral models](https://docs.mistral.ai/models) | [Mistral pricing](https://mistral.ai/pricing) |
| `devstral-medium-2507` | `MistralModel`, `MistralToolModel` | [Mistral models](https://docs.mistral.ai/models) | [Mistral pricing](https://mistral.ai/pricing) |
| `mistral-ocr-2505` | `MistralModel`, `MistralToolModel` | [Mistral models](https://docs.mistral.ai/models) | [Mistral pricing](https://mistral.ai/pricing) |
| `magistral-medium-2506` | `MistralModel` | [Mistral models](https://docs.mistral.ai/models) | [Mistral pricing](https://mistral.ai/pricing) |
| `ministral-8b-2410` | `MistralModel`, `MistralToolModel` | [Mistral models](https://docs.mistral.ai/models) | [Mistral pricing](https://mistral.ai/pricing) |
| `mistral-medium-2505` | `MistralModel`, `MistralToolModel` | [Mistral models](https://docs.mistral.ai/models) | [Mistral pricing](https://mistral.ai/pricing) |
| `codestral-2501` | `MistralModel`, `MistralToolModel` | [Mistral models](https://docs.mistral.ai/models) | [Mistral pricing](https://mistral.ai/pricing) |
| `mistral-large-2411` | `MistralModel`, `MistralToolModel` | [Mistral models](https://docs.mistral.ai/models) | [Mistral pricing](https://mistral.ai/pricing) |
| `pixtral-large-2411` | `MistralModel`, `MistralToolModel` | [Mistral models](https://docs.mistral.ai/models) | [Mistral pricing](https://mistral.ai/pricing) |
| `mistral-small-2407` | `MistralModel`, `MistralToolModel` | [Mistral models](https://docs.mistral.ai/models) | [Mistral pricing](https://mistral.ai/pricing) |
| `mistral-embed` | `MistralModel`, `MistralToolModel` | [Mistral models](https://docs.mistral.ai/models) | [Mistral pricing](https://mistral.ai/pricing) |
| `codestral-embed` | `MistralModel`, `MistralToolModel` | [Mistral models](https://docs.mistral.ai/models) | [Mistral pricing](https://mistral.ai/pricing) |
| `mistral-moderation-2411` | `MistralModel`, `MistralToolModel` | [Mistral models](https://docs.mistral.ai/models) | [Mistral pricing](https://mistral.ai/pricing) |
| `magistral-small-2507` | `MistralModel` | [Mistral models](https://docs.mistral.ai/models) | [Mistral pricing](https://mistral.ai/pricing) |
| `mistral-small-2506` | `MistralModel`, `MistralToolModel` | [Mistral models](https://docs.mistral.ai/models) | [Mistral pricing](https://mistral.ai/pricing) |
| `magistral-small-2506` | `MistralModel` | [Mistral models](https://docs.mistral.ai/models) | [Mistral pricing](https://mistral.ai/pricing) |
| `devstral-small-2507` | `MistralModel`, `MistralToolModel` | [Mistral models](https://docs.mistral.ai/models) | [Mistral pricing](https://mistral.ai/pricing) |
| `mistral-small-2501` | `MistralModel`, `MistralToolModel` | [Mistral models](https://docs.mistral.ai/models) | [Mistral pricing](https://mistral.ai/pricing) |
| `devstral-small-2505` | `MistralModel`, `MistralToolModel` | [Mistral models](https://docs.mistral.ai/models) | [Mistral pricing](https://mistral.ai/pricing) |
| `pixtral-12b-2409` | `MistralModel`, `MistralToolModel` | [Mistral models](https://docs.mistral.ai/models) | [Mistral pricing](https://mistral.ai/pricing) |
| `open-mistral-nemo` | `MistralModel`, `MistralToolModel` | [Mistral models](https://docs.mistral.ai/models) | [Mistral pricing](https://mistral.ai/pricing) |

## OpenAI

Provider links:

- Models: [OpenAI models](https://platform.openai.com/docs/models)
- Function calling: [OpenAI function calling](https://platform.openai.com/docs/guides/function-calling)
- Audio transcription: [OpenAI audio transcription](https://platform.openai.com/docs/api-reference/audio/createTranscription)
- Text to speech: [OpenAI text to speech](https://platform.openai.com/docs/guides/text-to-speech)
- Pricing: [OpenAI API pricing](https://openai.com/api/pricing/)

| Model | SDK surface | Model documentation | Pricing documentation |
| --- | --- | --- | --- |
| `gpt-5.5` | `OpenAIModel`, `OpenAIToolModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `gpt-5.5-2026-04-23` | `OpenAIModel`, `OpenAIToolModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `gpt-5.4` | `OpenAIModel`, `OpenAIToolModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `gpt-5.4-mini` | `OpenAIModel`, `OpenAIToolModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `gpt-5.4-nano` | `OpenAIModel`, `OpenAIToolModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `gpt-5.2` | `OpenAIModel`, `OpenAIToolModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `gpt-5.2-chat-latest` | `OpenAIModel`, `OpenAIToolModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `gpt-5.1` | `OpenAIModel`, `OpenAIToolModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `gpt-5.1-chat-latest` | `OpenAIModel`, `OpenAIToolModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `gpt-5` | `OpenAIModel`, `OpenAIToolModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `gpt-5-2025-08-07` | `OpenAIModel`, `OpenAIToolModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `gpt-5-mini` | `OpenAIModel`, `OpenAIToolModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `gpt-5-mini-2025-08-07` | `OpenAIModel`, `OpenAIToolModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `gpt-5-nano` | `OpenAIModel`, `OpenAIToolModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `gpt-5-nano-2025-08-07` | `OpenAIModel`, `OpenAIToolModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `gpt-4.1` | `OpenAIModel`, `OpenAIToolModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `gpt-4.1-2025-04-14` | `OpenAIModel`, `OpenAIToolModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `gpt-4.1-mini` | `OpenAIModel`, `OpenAIToolModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `gpt-4.1-nano` | `OpenAIModel`, `OpenAIToolModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `gpt-oss-20b` | `OpenAIModel`, `OpenAIToolModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `gpt-oss-120b` | `OpenAIModel`, `OpenAIToolModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `gpt-4o` | `OpenAIModel`, `OpenAIToolModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `gpt-4o-2024-08-06` | `OpenAIModel`, `OpenAIToolModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `gpt-4o-mini` | `OpenAIModel`, `OpenAIToolModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `gpt-4o-mini-2024-07-18` | `OpenAIModel`, `OpenAIToolModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `gpt-4-turbo` | `OpenAIModel`, `OpenAIToolModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `gpt-4-turbo-2024-04-09` | `OpenAIModel`, `OpenAIToolModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `o3-deep-research` | `OpenAIReasonModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `o3-deep-research-2025-06-26` | `OpenAIReasonModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `o4-mini-deep-research` | `OpenAIReasonModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `o4-mini-deep-research-2025-06-26` | `OpenAIReasonModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `o3-pro` | `OpenAIReasonModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `o3-pro-2025-06-10` | `OpenAIReasonModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `o3` | `OpenAIReasonModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `o3-2025-04-16` | `OpenAIReasonModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `o4-mini` | `OpenAIReasonModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `o4-mini-2025-04-16` | `OpenAIReasonModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `o1-pro` | `OpenAIReasonModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `o1-pro-2025-03-19` | `OpenAIReasonModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `o1` | `OpenAIReasonModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `o1-2024-12-17` | `OpenAIReasonModel` | [OpenAI models](https://platform.openai.com/docs/models) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `whisper-1` | `OpenAIAudio` | [Audio transcription](https://platform.openai.com/docs/api-reference/audio/createTranscription) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `gpt-4o-transcribe` | `OpenAIAudio` | [Audio transcription](https://platform.openai.com/docs/api-reference/audio/createTranscription) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `gpt-4o-mini-transcribe` | `OpenAIAudio` | [Audio transcription](https://platform.openai.com/docs/api-reference/audio/createTranscription) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `tts-1` | `OpenAIAudioTTS` | [Text to speech](https://platform.openai.com/docs/guides/text-to-speech) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `tts-1-hd` | `OpenAIAudioTTS` | [Text to speech](https://platform.openai.com/docs/guides/text-to-speech) | [OpenAI pricing](https://openai.com/api/pricing/) |
| `gpt-4o-mini-tts` | `OpenAIAudioTTS` | [Text to speech](https://platform.openai.com/docs/guides/text-to-speech) | [OpenAI pricing](https://openai.com/api/pricing/) |

## Perplexity

Provider links:

- Model cards: [Perplexity model cards](https://docs.perplexity.ai/guides/model-cards)
- Pricing: [Perplexity pricing](https://docs.perplexity.ai/docs/getting-started/pricing)

| Model | SDK surface | Model documentation | Pricing documentation |
| --- | --- | --- | --- |
| `sonar-deep-research` | `PerplexityModel` | [Model cards](https://docs.perplexity.ai/guides/model-cards) | [Pricing](https://docs.perplexity.ai/docs/getting-started/pricing) |
| `sonar-reasoning-pro` | `PerplexityModel` | [Model cards](https://docs.perplexity.ai/guides/model-cards) | [Pricing](https://docs.perplexity.ai/docs/getting-started/pricing) |
| `sonar-reasoning` | `PerplexityModel` | [Model cards](https://docs.perplexity.ai/guides/model-cards) | [Pricing](https://docs.perplexity.ai/docs/getting-started/pricing) |
| `sonar-pro` | `PerplexityModel` | [Model cards](https://docs.perplexity.ai/guides/model-cards) | [Pricing](https://docs.perplexity.ai/docs/getting-started/pricing) |
| `sonar` | `PerplexityModel` | [Model cards](https://docs.perplexity.ai/guides/model-cards) | [Pricing](https://docs.perplexity.ai/docs/getting-started/pricing) |
| `r1-1776` | `PerplexityModel` | [Model cards](https://docs.perplexity.ai/guides/model-cards) | [Pricing](https://docs.perplexity.ai/docs/getting-started/pricing) |

## PlayHT

Provider links:

- API reference: [PlayHT API docs](https://docs.play.ht/)
- OpenAPI reference: [PlayHT generated API reference](https://playht.github.io/api-docs-generator/)
- Pricing: [PlayHT pricing](https://play.ht/pricing/)

| Model | SDK surface | Model documentation | Pricing documentation |
| --- | --- | --- | --- |
| `PlayDialog` | `PlayhtTTS` | [PlayHT API docs](https://docs.play.ht/) | [PlayHT pricing](https://play.ht/pricing/) |
| `Play3.0-mini` | `PlayHTModel`, `PlayhtTTS` | [PlayHT API docs](https://docs.play.ht/) | [PlayHT pricing](https://play.ht/pricing/) |
| `PlayHT2.0-turbo` | `PlayHTModel`, `PlayhtTTS` | [PlayHT API docs](https://docs.play.ht/) | [PlayHT pricing](https://play.ht/pricing/) |
| `PlayHT1.0` | `PlayHTModel`, `PlayhtTTS` | [PlayHT API docs](https://docs.play.ht/) | [PlayHT pricing](https://play.ht/pricing/) |
| `PlayHT2.0` | `PlayHTModel`, `PlayhtTTS` | [PlayHT API docs](https://docs.play.ht/) | [PlayHT pricing](https://play.ht/pricing/) |

## PyTesseract

Provider links:

- Runtime: [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- Python wrapper: [pytesseract](https://pypi.org/project/pytesseract/)
- Pricing: no hosted provider pricing; cost depends on local hardware or the user's chosen hosting environment.

| Model | SDK surface | Model documentation | Pricing documentation |
| --- | --- | --- | --- |
| Local Tesseract OCR installation | `PytesseractOCR` | [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) | Not applicable |
