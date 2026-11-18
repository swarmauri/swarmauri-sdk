![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

# swarmauri_workflow_documentassistant

[![Downloads](https://static.pepy.tech/badge/swarmauri_workflow_documentassistant/month)](https://pepy.tech/project/swarmauri_workflow_documentassistant)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_workflow_documentassistant.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_workflow_documentassistant)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://pypi.org/project/swarmauri_workflow_documentassistant)
[![License](https://img.shields.io/pypi/l/swarmauri_workflow_documentassistant)](LICENSE)
[![Version](https://img.shields.io/pypi/v/swarmauri_workflow_documentassistant)](https://pypi.org/project/swarmauri_workflow_documentassistant)

Runnable reference composition built from injectable Swarmauri factors.

## Features

- Export `DocumentAssistantWorkflow` with SDK interface/base-class inheritance and entry-point discovery.
- Keep user authority, workload identity, lifecycle and delivery dependencies explicit.
- Reuse existing service registries, transports, checkpoints and token providers.
- Support Python 3.10, 3.11 and 3.12.

## Installation

These packages introduce unreleased core/base APIs. Install the matching workspace revision together; do not combine with older published core/base releases. Release validation must publish compatible dependency versions first.

```sh
uv pip install ./pkgs/standards/swarmauri_workflow_documentassistant
pip install ./pkgs/standards/swarmauri_workflow_documentassistant
```

## Usage

The following is composition code. Injected dependency names are host configuration, not bundled mock providers. Async statements run inside an async function.

```python
# Explicit offline mode: scripted model and host-admitted demo identity.
# Real local keys, JWT verification, SQLite records and authority checks.
# No live IdP or model provider is impersonated.
# Run the installed reference command:
# swarmauri-workflow-documentassistant

from swarmauri_workflow_documentassistant import DocumentAssistantWorkflow

workflow = DocumentAssistantWorkflow.create(
    directory, tokens=token_service, kid=signing_key_id, issuer=issuer,
    model_factory=model_factory, authorize=authorize_user_resource,
    documents=document_repository, permission=document_permission,
)
# subject comes from a verified host session, e.g. OIDCAdmission.complete().
result = await workflow.run(authenticated_subject)
```

See [the complete architecture and deployment guide](../../../docs/examples/composable-execution/README.md) for concrete local commands, live OIDC integration, HTTP hosting, lifecycle semantics and failure recovery.

## Verification

From `pkgs/`, with the workspace dependencies installed:

```sh
uv run --package swarmauri_workflow_documentassistant --directory standards/swarmauri_workflow_documentassistant pytest
uv run --package swarmauri_workflow_documentassistant --directory standards/swarmauri_workflow_documentassistant ruff check .
```

Tests use real signing and stores where applicable; scripted models are explicitly identified fixtures. No live provider interoperability is claimed by offline tests.

## Contributing

Follow the repository [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/AGENTS.md).
