![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

# Swarmauri WIMSE Research Agent

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_agent_wimse)](https://pepy.tech/project/swarmauri-agent-wimse)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_agent_wimse.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_agent_wimse/)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_agent_wimse)](https://www.python.org/)
[![License](https://img.shields.io/pypi/l/swarmauri_agent_wimse)](https://www.apache.org/licenses/LICENSE-2.0)
[![Version](https://img.shields.io/pypi/v/swarmauri_agent_wimse?label=swarmauri_agent_wimse&color=green)](https://pypi.org/project/swarmauri-agent-wimse/)

Deployable HTTP endpoints for WIMSE workflow admission, research, and delegated file reads.

## Features

- Workflow ingress verifies the caller's signed request and bound transaction, then checks the caller's grant for the requested workflow.
- Research verifies the Coordinator's signed HTTP request and bound transaction, exchanges the transaction for read-only delegation, and runs a ToolAgent with a request-bound file tool that invokes the file service with a fresh WPT.
- The File Tool verifies the WIT, proof, exact audience, replay protection and delegated file before reading.
- The endpoints take workload trust, issuer trust and audience configuration from the host. The host provisions the Research WIT and signer.
- The HTTP endpoints use the bare audience configured for this reference profile. The package couples its HTTP signature adapter to the pinned TbA implementation.

## Installation

Requires Python 3.10 through 3.12.

Install from the workspace checkout with either command.

```sh
uv pip install ./pkgs/standards/swarmauri_agent_wimse
pip install ./pkgs/standards/swarmauri_agent_wimse
```

## Usage

```python
from http.server import ThreadingHTTPServer
from swarmauri_agent_wimse import FileToolEndpoint, TransactionPolicy, http_handler

def file_server(files, workload_trust, transaction_keys):
    endpoint = FileToolEndpoint(
        tool=dict(files).__getitem__,
        audience="http://rich.ietf127.example:5063",
        trust=workload_trust,
        transaction=TransactionPolicy(
            issuer="http://rich.ietf127.example:5061",
            audience="rich.ietf127.example",
            keys=tuple(transaction_keys),
        ),
        research_subject="wimse://rich.ietf127.example/agent/research",
    )
    return ThreadingHTTPServer(("127.0.0.1", 5063), http_handler(endpoint))
```

Construct `ResearchAgentEndpoint` with trusted issuer keys, the expected
Coordinator and Research identity URIs, a provisioned WIT and TbA signer, the
issuer and file URLs, the exact file audience, and a tool-capable model. Serve
it with the same `http_handler` factory. Each authorized request gets a
`WimseResearchAgent` with a fresh conversation and a `Toolkit` containing
its bound `WimseFileTool`. The model sees the file argument and the tool result.
The host owns the workload and transaction credentials.

`WimseIngressEndpoint` accepts signed POST requests at
`/workflows/{workflow}/executions`. Register each workflow by name with a
callable that accepts the JSON `inputs` object and returns a JSON-serializable
result. Supply a set of `(workload_subject, workflow_name)` grants and a
`TransactionPolicy` for the ingress token issuer, audience, and verification
keys. Use the same `http_handler` factory to serve the endpoint.

The HTTP fixture binds to loopback. For deployment, supply HTTPS transport and
a replay store shared across workers. Keep the file mapping under the host's
control and provision separate workload proof keys.

## Native nine-hop verification

Run this command from the package directory.

```sh
uv run --package swarmauri_agent_wimse pytest tests/unit/test_nine_hop_native.py
```

The test runs a Swarmauri agent behind `WimseIngressEndpoint` at hop 2 and
dispatches all nine requests in process with fresh keys and real TbA proof
checks. One case pairs the SDK research agent with a fixture file service.
The other pairs a fixture
research peer with the SDK file service. The suite also checks that wrong
audience, missing proof, a different file, and replay cause zero additional
reads and that a valid workload without the workflow grant cannot invoke
the agent. It needs no external runtime or live model credentials.
