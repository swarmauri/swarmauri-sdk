![Swarmauri](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

[![PyPI version](https://img.shields.io/pypi/v/swarmauri_transport_aws_eventstream.svg)](https://pypi.org/project/swarmauri_transport_aws_eventstream/) [![Python](https://img.shields.io/pypi/pyversions/swarmauri_transport_aws_eventstream.svg)](https://pypi.org/project/swarmauri_transport_aws_eventstream/) [![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE) [![Downloads](https://static.pepy.tech/badge/swarmauri_transport_aws_eventstream)](https://pepy.tech/project/swarmauri_transport_aws_eventstream) [![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk.svg?path=pkgs%2Fstandards%2Fswarmauri_transport_aws_eventstream)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/)

# swarmauri_transport_aws_eventstream

`swarmauri_transport_aws_eventstream` adapts Amazon Bedrock's Smithy
bidirectional EventStream operation to Swarmauri's
`IBidirectionalStreamClient` and `IBidirectionalStreamConnection` contracts.
The AWS SDK owns HTTP/2 framing, credential-chain resolution, and SigV4 request
and message signing; this package owns the Swarmauri lifecycle and JSON event
mapping.

## Features

- Sends and receives JSON events over `InvokeModelWithBidirectionalStream`.
- Supports explicit temporary credentials, the default AWS credential chain,
  and named profiles.
- Exposes synchronous and asynchronous Swarmauri connection APIs.
- Converts AWS stream exception events into `AwsEventStreamError`.
- Keeps credentials out of serialized component state.

The codec and package metadata support Python 3.10 through 3.12. Amazon's
official `aws-sdk-bedrock-runtime` currently requires Python 3.12, so opening a
live Bedrock connection requires Python 3.12.

## Installation

```bash
uv add swarmauri_transport_aws_eventstream
```

```bash
pip install swarmauri_transport_aws_eventstream
```

## Usage

Use the client directly when you already have a Bedrock model ID:

```python
from swarmauri_transport_aws_eventstream import AwsEventStreamClient

client = AwsEventStreamClient(region="us-east-1")
connection = await client.aconnect(
    "https://bedrock-runtime.us-east-1.amazonaws.com",
    model_id="amazon.nova-sonic-v1:0",
)

await connection.asend({"event": {"sessionStart": {}}})
async for event in connection.aiter_events():
    print(event)
await connection.aclose()
```

`NovaSonicLiveModel` configures this transport automatically. Pass an
`AmazonNovaProvider` when you need a named profile, explicit temporary
credentials, a different region, or a custom Bedrock runtime endpoint.
