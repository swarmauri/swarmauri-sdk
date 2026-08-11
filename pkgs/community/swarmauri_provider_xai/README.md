![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![PyPI](https://img.shields.io/pypi/v/swarmauri_provider_xai.svg)](https://pypi.org/project/swarmauri_provider_xai/) [![Python](https://img.shields.io/pypi/pyversions/swarmauri_provider_xai.svg)](https://pypi.org/project/swarmauri_provider_xai/) [![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE) [![Downloads](https://static.pepy.tech/badge/swarmauri_provider_xai)](https://pepy.tech/project/swarmauri_provider_xai) [![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/)

# swarmauri_provider_xai

## Features

- xAI authentication, endpoints, catalogs, errors, and tool schemas.
- Capability-aware chat, model-listing, and realtime connection configs.
- Runtime authorization with credentials excluded from serialized configs.
- Shared provider resource for xAI model families.

## Installation

`uv add swarmauri_provider_xai` or `pip install swarmauri_provider_xai`.

## Usage

```python
from swarmauri_provider_xai import XAIProvider

provider = XAIProvider(api_key="...")
config = provider.connection_config("chat.completions", model="grok-4.3")
headers = provider.authorize(config)
```

Inject the provider into an xAI model adapter; the provider describes the connection but never performs network I/O.
