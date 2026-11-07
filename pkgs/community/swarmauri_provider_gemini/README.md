![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![PyPI](https://img.shields.io/pypi/v/swarmauri_provider_gemini.svg)](https://pypi.org/project/swarmauri_provider_gemini/) [![Python](https://img.shields.io/pypi/pyversions/swarmauri_provider_gemini.svg)](https://pypi.org/project/swarmauri_provider_gemini/) [![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE) [![Downloads](https://static.pepy.tech/badge/swarmauri_provider_gemini)](https://pepy.tech/project/swarmauri_provider_gemini) [![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/)

# swarmauri_provider_gemini

## Features

- Gemini credentials and endpoint configuration.
- Shared model catalog, error mapping, and tool schema conversion.
- Reusable by LLM, VLM, and LiveModel packages.

## Installation

`uv add swarmauri_provider_gemini` or `pip install swarmauri_provider_gemini`.

## Usage

Construct `GeminiProvider(api_key=...)` and inject it into a Gemini model adapter.
