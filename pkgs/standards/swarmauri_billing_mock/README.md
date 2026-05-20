![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_billing_mock/">
        <img src="https://static.pepy.tech/badge/swarmauri_billing_mock/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_billing_mock/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_billing_mock.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_mock/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_mock/">
        <img src="https://img.shields.io/pypi/l/swarmauri_billing_mock" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_mock/">
        <img src="https://img.shields.io/pypi/v/swarmauri_billing_mock?label=swarmauri_billing_mock&color=green" alt="PyPI - swarmauri_billing_mock"/></a>
</p>

# Swarmauri Billing Mock

The **Swarmauri Billing Mock** package delivers a deterministic billing provider ideal for unit tests. It implements the full Swarmauri billing surface, echoing payloads to keep validation straightforward.

## Features

- âœ… Implements all billing mixins with predictable outputs.
- âœ… Perfect for test suites where deterministic responses are essential.
- âœ… Provides fast feedback without network calls.
- âœ… Demonstrates how to subclass `BillingProviderBase` for custom flows.

## Installation

```bash
pip install swarmauri_billing_mock
```

```bash
uv add swarmauri_billing_mock
```

## Usage

```python
from swarmauri_billing_mock import MockBillingProvider
from swarmauri_base.billing import ProductSpec

provider = MockBillingProvider(api_key="mock-key")
product = provider.create_product(ProductSpec(payload={"name": "Test"}), idempotency_key="mock-prod-1")
print(product.raw)
```

## Capability Mapping

The mock provider advertises every `Capability` and therefore maps to the entire set of `tigrbl_billing` capabilities when using `capabilities_to_tigrbl`.

## Contributing

Need additional fixtures? Contributions that expand deterministic behaviours are encouraged.
