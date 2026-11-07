![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![PyPI](https://img.shields.io/pypi/v/swarmauri_agent_realtime.svg)](https://pypi.org/project/swarmauri_agent_realtime/) [![Python](https://img.shields.io/pypi/pyversions/swarmauri_agent_realtime.svg)](https://pypi.org/project/swarmauri_agent_realtime/) [![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE) [![Downloads](https://static.pepy.tech/badge/swarmauri_agent_realtime)](https://pepy.tech/project/swarmauri_agent_realtime) [![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/)

# swarmauri_agent_realtime

## Features

- Provider-neutral live-model orchestration.
- Conversation bridging, function calls, interruption, and typed events.
- One provider connection per conversation through `LiveSessionPool`.

## Installation

`uv add swarmauri_agent_realtime` or `pip install swarmauri_agent_realtime`.

## Usage

Construct `RealtimeAgent(live_model=...)`, send typed live inputs, and consume events or use `run`/`arun` for one completed turn.
