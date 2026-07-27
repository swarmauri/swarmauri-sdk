![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

# swarmauri_llm_openrouter

[![PyPI version](https://img.shields.io/pypi/v/swarmauri_llm_openrouter.svg)](https://pypi.org/project/swarmauri_llm_openrouter/)
[![Python versions](https://img.shields.io/pypi/pyversions/swarmauri_llm_openrouter.svg)](https://pypi.org/project/swarmauri_llm_openrouter/)
[![Downloads](https://static.pepy.tech/badge/swarmauri_llm_openrouter/month)](https://pepy.tech/project/swarmauri_llm_openrouter)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_openrouter.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_llm_openrouter/)
[![License](https://img.shields.io/pypi/l/swarmauri_llm_openrouter.svg)](https://github.com/swarmauri/swarmauri-sdk/blob/master/LICENSE)

Use OpenRouter's unified APIs through Swarmauri's native LLM, tool-LLM,
vision-language, and image-generation contracts.

## Features

- Text, reasoning, structured-output, streaming, and batch workflows.
- Client-side Swarmauri toolkit execution through OpenRouter tool calling.
- URL and base64 image inputs without flattening multimodal messages.
- Dedicated image generation with binary results.
- Provider ordering, fallback, parameter, data-collection, and ZDR controls.
- Explicit live model discovery without constructor-time network requests.

## Installation

Install with `uv`:

```bash
uv add swarmauri_llm_openrouter
```

Install with `pip`:

```bash
pip install swarmauri_llm_openrouter
```

## Usage

### Chat

```python
from swarmauri_llm_openrouter import OpenRouterModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="Explain provider routing."))
model = OpenRouterModel(
    api_key="...",
    name="openai/gpt-4o-mini",
    allowed_models=["openai/gpt-4o-mini"],
    app_name="My Swarmauri application",
)
model.predict(conversation, temperature=0.2)
print(conversation.get_last().content)
```

### Vision

```python
from swarmauri_llm_openrouter import OpenRouterVLM

vlm = OpenRouterVLM(
    api_key="...",
    name="openai/gpt-4o-mini",
    allowed_models=["openai/**"],
)
# Add a HumanMessage whose content contains text and image_url items, then:
vlm.predict_vision(conversation)
```

### Image generation

```python
from swarmauri_llm_openrouter import OpenRouterImgGenModel

image_model = OpenRouterImgGenModel(
    api_key="...",
    name="openai/gpt-image-1",
    allowed_models=["openai/gpt-image-1"],
)
image_bytes = image_model.generate_image(
    "A geometric tiger rendered as stained glass",
    size="1024x1024",
    output_format="png",
)
```

### Model discovery

```python
from swarmauri_llm_openrouter import OpenRouterModel, OpenRouterModelCatalog

catalog = OpenRouterModelCatalog.from_api_key("...")
available_models = catalog.list_model_ids(output_modalities="text")
model = OpenRouterModel(
    api_key="...",
    name="openai/gpt-4o-mini",
    allowed_models=available_models,
)
```

`allowed_models` is an inherited policy, not a provider catalog. An empty list
denies every model, exact IDs allow only those models, provider patterns such as
`["anthropic/**"]` allow matching namespaces, and `["*"]` explicitly permits
all names. Model availability changes independently of package releases, so use
the OpenRouter catalog when a concrete policy should mirror currently available
models.

## Project links

- [Swarmauri SDK](https://github.com/swarmauri/swarmauri-sdk)
- [OpenRouter documentation](https://openrouter.ai/docs)
- [Contributing guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
