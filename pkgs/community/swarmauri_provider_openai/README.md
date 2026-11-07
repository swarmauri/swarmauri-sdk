![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![PyPI](https://img.shields.io/pypi/v/swarmauri_provider_openai.svg)](https://pypi.org/project/swarmauri_provider_openai/) [![Python](https://img.shields.io/pypi/pyversions/swarmauri_provider_openai.svg)](https://pypi.org/project/swarmauri_provider_openai/) [![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE) [![Downloads](https://static.pepy.tech/badge/swarmauri_provider_openai)](https://pepy.tech/project/swarmauri_provider_openai) [![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/)

# swarmauri_provider_openai

## Features

- Shared OpenAI credentials, endpoints, catalogs, errors, and tool schemas.
- Reusable across request/response and realtime model families.

## Installation

`uv add swarmauri_provider_openai` or `pip install swarmauri_provider_openai`.

## Usage

Construct `OpenAIProvider(api_key=...)` and inject it into an OpenAI model.
