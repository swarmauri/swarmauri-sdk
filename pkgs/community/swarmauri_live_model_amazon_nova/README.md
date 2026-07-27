![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![PyPI](https://img.shields.io/pypi/v/swarmauri_live_model_amazon_nova.svg)](https://pypi.org/project/swarmauri_live_model_amazon_nova/) [![Python](https://img.shields.io/pypi/pyversions/swarmauri_live_model_amazon_nova.svg)](https://pypi.org/project/swarmauri_live_model_amazon_nova/) [![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE) [![Downloads](https://static.pepy.tech/badge/swarmauri_live_model_amazon_nova)](https://pepy.tech/project/swarmauri_live_model_amazon_nova) [![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/)

# swarmauri_live_model_amazon_nova

## Features

- Nova Sonic text/audio sessions over an injected bidirectional HTTP/2 transport.
- Typed audio, text, tool, usage, completion, and error events.

## Installation

`uv add swarmauri_live_model_amazon_nova` or `pip install swarmauri_live_model_amazon_nova`.

## Usage

Inject `AmazonNovaProvider` and an `IBidirectionalStreamClient` into `NovaSonicLiveModel`.
