![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![PyPI](https://img.shields.io/pypi/v/swarmauri_provider_amazon_nova.svg)](https://pypi.org/project/swarmauri_provider_amazon_nova/) [![Python](https://img.shields.io/pypi/pyversions/swarmauri_provider_amazon_nova.svg)](https://pypi.org/project/swarmauri_provider_amazon_nova/) [![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE) [![Downloads](https://static.pepy.tech/badge/swarmauri_provider_amazon_nova)](https://pepy.tech/project/swarmauri_provider_amazon_nova) [![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/)

# swarmauri_provider_amazon_nova

## Features

- AWS identity, region, Bedrock endpoint, catalog, error, and schema resources.
- Shared provider resource for Amazon Nova model families.

## Installation

`uv add swarmauri_provider_amazon_nova` or `pip install swarmauri_provider_amazon_nova`.

## Usage

Inject `AmazonNovaProvider(region=...)` into a Nova model adapter.
