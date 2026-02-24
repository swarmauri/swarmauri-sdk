![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_billing_adyen/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_billing_adyen" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_adyen/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_adyen.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_adyen/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_billing_adyen" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_adyen/">
        <img src="https://img.shields.io/pypi/l/swarmauri_billing_adyen" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_adyen/">
        <img src="https://img.shields.io/pypi/v/swarmauri_billing_adyen?label=swarmauri_billing_adyen&color=green" alt="PyPI - swarmauri_billing_adyen"/></a>
</p>

---

# Swarmauri Billing Adyen

The **Swarmauri Billing Adyen** package provides an Adyen-style billing provider that adheres to the Swarmauri billing interfaces. It mirrors the behaviours of Adyen's platform while returning Pydantic models for simple serialization and testing.

## Features

- ✅ Simulates all Swarmauri billing capabilities for an Adyen-like provider.
- ✅ Generates deterministic webhook events and dispute lists for integration testing.
- ✅ Makes it easy to evaluate tigrbl strategy coverage by mapping `Capability` values.
- ✅ Ships as a ready-made baseline for extending into production-grade Adyen clients.

## Installation

```bash
pip install swarmauri_billing_adyen
```

```bash
uv add swarmauri_billing_adyen
```

## Usage

```python
from swarmauri_billing_adyen import AdyenBillingProvider
from swarmauri_base.billing import CheckoutRequest, ProductSpec

provider = AdyenBillingProvider(api_key="ady_test_123")
product = provider.create_product(ProductSpec(payload={"name": "Enterprise"}), idempotency_key="prod-ady-1")
checkout = provider.create_checkout(product, CheckoutRequest(payload={"return_url": "https://merchant.example"}))

print(product.id, checkout.id)
```

## Capability Mapping

All advertised capabilities come directly from `swarmauri_core.billing.Capability` and can be translated to `tigrbl_billing` requirements via `capabilities_to_tigrbl`.

## Contributing

Community contributions are welcome! Share improvements that better reflect Adyen's API surface or add additional fixtures.
