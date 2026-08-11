![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![PyPI version](https://img.shields.io/pypi/v/swarmauri_provider_openrouter.svg)](https://pypi.org/project/swarmauri_provider_openrouter/) [![Python versions](https://img.shields.io/pypi/pyversions/swarmauri_provider_openrouter.svg)](https://pypi.org/project/swarmauri_provider_openrouter/) [![Downloads](https://static.pepy.tech/badge/swarmauri_provider_openrouter/month)](https://pepy.tech/project/swarmauri_provider_openrouter) [![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_provider_openrouter.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_provider_openrouter/) [![License](https://img.shields.io/pypi/l/swarmauri_provider_openrouter.svg)](https://pypi.org/project/swarmauri_provider_openrouter/)

# swarmauri_provider_openrouter

`swarmauri_provider_openrouter` describes OpenRouter authentication, endpoints,
model metadata, routing preferences, provider errors, and tool schemas without
owning an HTTP implementation.

## Features

- Bearer authentication with optional application attribution headers.
- Capability-based resolution for chat, catalog, and image-generation APIs.
- Provider routing, fallback, data-collection, and ZDR preferences.
- Mutable provider catalog populated by an injected model client.
- OpenRouter-compatible function-tool schema conversion.
- Serializable connection configurations that exclude credentials.

## Installation

```bash
uv add swarmauri_provider_openrouter
```

```bash
pip install swarmauri_provider_openrouter
```

## Usage

```python
from swarmauri_provider_openrouter import (
    OpenRouterProvider,
    OpenRouterProviderPreferences,
)

provider = OpenRouterProvider(
    api_key="...",
    site_url="https://example.com",
    app_name="My application",
)
config = provider.connection_config(
    "chat.completions",
    model="openai/gpt-4o-mini",
)
headers = provider.authorize(config)
routing = OpenRouterProviderPreferences(order=["OpenAI"])
```

Pass the provider and routing preferences to a compatible model package. The
provider returns connection configuration; a Swarmauri transport such as
`swarmauri_transport_httpx` performs the request.

## Project links

- [Swarmauri SDK](https://github.com/swarmauri/swarmauri-sdk)
- [OpenRouter documentation](https://openrouter.ai/docs)
