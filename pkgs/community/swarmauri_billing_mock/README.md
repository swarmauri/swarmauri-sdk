![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_billing_mock/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_billing_mock" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_mock/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_mock.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_mock/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_billing_mock" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_mock/">
        <img src="https://img.shields.io/pypi/l/swarmauri_billing_mock" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_mock/">
        <img src="https://img.shields.io/pypi/v/swarmauri_billing_mock?label=swarmauri_billing_mock&color=green" alt="PyPI - swarmauri_billing_mock"/></a>
</p>

---

# Swarmauri Billing Mock

The **Swarmauri Billing Mock** package delivers a deterministic billing provider ideal for unit tests. It implements the full Swarmauri billing surface, echoing payloads to keep validation straightforward.

## Features

- ✅ Implements all billing mixins with predictable outputs.
- ✅ Perfect for test suites where deterministic responses are essential.
- ✅ Provides fast feedback without network calls.
- ✅ Demonstrates how to subclass `BillingProviderBase` for custom flows.

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
