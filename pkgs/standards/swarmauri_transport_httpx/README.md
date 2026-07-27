![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![PyPI version](https://img.shields.io/pypi/v/swarmauri_transport_httpx.svg)](https://pypi.org/project/swarmauri_transport_httpx/) [![Python](https://img.shields.io/pypi/pyversions/swarmauri_transport_httpx.svg)](https://pypi.org/project/swarmauri_transport_httpx/) [![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE) [![Downloads](https://static.pepy.tech/badge/swarmauri_transport_httpx)](https://pepy.tech/project/swarmauri_transport_httpx) [![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/)

# swarmauri_transport_httpx

## Features

- Synchronous and asynchronous buffered requests.
- Genuine synchronous and asynchronous streaming contexts.
- Provider-neutral Swarmauri HTTP interfaces.

## Installation

```bash
uv add swarmauri_transport_httpx
pip install swarmauri_transport_httpx
```

## Usage

Use `HttpxClient.request`/`arequest` for buffered responses and `stream`/`astream` for incremental response processing.
