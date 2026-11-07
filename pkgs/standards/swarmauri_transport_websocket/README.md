![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![PyPI version](https://img.shields.io/pypi/v/swarmauri_transport_websocket.svg)](https://pypi.org/project/swarmauri_transport_websocket/) [![Python](https://img.shields.io/pypi/pyversions/swarmauri_transport_websocket.svg)](https://pypi.org/project/swarmauri_transport_websocket/) [![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE) [![Downloads](https://static.pepy.tech/badge/swarmauri_transport_websocket)](https://pepy.tech/project/swarmauri_transport_websocket) [![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/)

# swarmauri_transport_websocket

## Features

- Separate synchronous and asynchronous connection paths.
- Bidirectional text and binary messages.
- Context-independent ping, receive iteration, and deterministic close.

## Installation

```bash
uv add swarmauri_transport_websocket
pip install swarmauri_transport_websocket
```

## Usage

Create a `WebSocketClient`, call `connect` or `aconnect`, and use the matching send/receive methods. This package does not claim logical-channel multiplexing.
