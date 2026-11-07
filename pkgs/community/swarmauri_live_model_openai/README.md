![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![PyPI](https://img.shields.io/pypi/v/swarmauri_live_model_openai.svg)](https://pypi.org/project/swarmauri_live_model_openai/) [![Python](https://img.shields.io/pypi/pyversions/swarmauri_live_model_openai.svg)](https://pypi.org/project/swarmauri_live_model_openai/) [![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE) [![Downloads](https://static.pepy.tech/badge/swarmauri_live_model_openai)](https://pepy.tech/project/swarmauri_live_model_openai) [![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/)

# swarmauri_live_model_openai

## Features

- OpenAI Realtime multimodal conversations over WebSocket.
- Persistent Responses WebSocket adapter.
- Typed text, audio, transcripts, tools, interruption, and usage events.

## Installation

`uv add swarmauri_live_model_openai` or `pip install swarmauri_live_model_openai`.

## Usage

Inject an `OpenAIProvider`, connect with `LiveConfigBase`, send typed inputs, and consume the session event stream.
