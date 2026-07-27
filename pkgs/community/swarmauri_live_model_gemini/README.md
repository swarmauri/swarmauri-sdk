![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![PyPI](https://img.shields.io/pypi/v/swarmauri_live_model_gemini.svg)](https://pypi.org/project/swarmauri_live_model_gemini/) [![Python](https://img.shields.io/pypi/pyversions/swarmauri_live_model_gemini.svg)](https://pypi.org/project/swarmauri_live_model_gemini/) [![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE) [![Downloads](https://static.pepy.tech/badge/swarmauri_live_model_gemini)](https://pepy.tech/project/swarmauri_live_model_gemini) [![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/)

# swarmauri_live_model_gemini

## Features

- Text, audio, image, and video input.
- Audio and transcript output as independent event streams.
- Function calls, VAD/interruption events, usage, and session resumption.
- Synchronous façade and canonical asynchronous WebSocket session.

## Installation

`uv add swarmauri_live_model_gemini` or `pip install swarmauri_live_model_gemini`.

## Usage

Create `GeminiLiveModel(provider=GeminiProvider(api_key=...))`, connect with `LiveConfigBase`, send typed inputs, and consume typed events.
