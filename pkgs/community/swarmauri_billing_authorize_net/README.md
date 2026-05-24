![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_billing_authorize_net/">
        <img src="https://static.pepy.tech/badge/swarmauri_billing_authorize_net/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_authorize_net/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_authorize_net.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_authorize_net/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue" alt="Supported Python Versions"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_authorize_net/">
        <img src="https://img.shields.io/pypi/l/swarmauri_billing_authorize_net" alt="License"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_authorize_net/">
        <img src="https://img.shields.io/pypi/v/swarmauri_billing_authorize_net?label=swarmauri_billing_authorize_net&color=green" alt="Release Version"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a>
</p>

# Swarmauri Billing Authorize Net

Authorize.Net JSON API backed Swarmauri billing provider for transactions, captures, voids, refunds, customer profiles, and webhook validation.

## Features

- Authorize.Net JSON API backed Swarmauri billing provider for transactions, captures, voids, refunds, customer profiles, and webhook validation.
- Exposes discoverable runtime entry points for `swarmauri.billing_providers` so the package can be wired into Swarmauri or Tigrbl workflows.
- Lives in the community package lane for optional integrations that extend the main Swarmauri SDK surface.

## Installation

Install this package with `uv` or `pip`.

```bash
uv add swarmauri_billing_authorize_net
```

```bash
pip install swarmauri_billing_authorize_net
```

## Usage

Start by importing the public package surface, then configure the exported type or callable inside the workflow that consumes it.

```python
from swarmauri_billing_authorize_net import AuthorizeNetBillingProvider

exports = ['AuthorizeNetBillingProvider']
print(exports)
```

After import, pass the exported objects into the surrounding Swarmauri or Tigrbl code that owns configuration, credentials, transport, or storage details.

License: Apache-2.0. See `LICENSE`.
