![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_billing_adyen/">
        <img src="https://static.pepy.tech/badge/swarmauri_billing_adyen/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_adyen/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_adyen.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_adyen/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_adyen/">
        <img src="https://img.shields.io/pypi/l/swarmauri_billing_adyen" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_adyen/">
        <img src="https://img.shields.io/pypi/v/swarmauri_billing_adyen?label=swarmauri_billing_adyen&color=green" alt="PyPI - swarmauri_billing_adyen"/></a>
</p>
---

# Swarmauri Billing Adyen

The **Swarmauri Billing Adyen** package provides an Adyen-style billing provider that adheres to the Swarmauri billing interfaces. It mirrors the behaviours of Adyen's platform while returning Pydantic models for simple serialization and testing.

## Features

- âœ… Simulates all Swarmauri billing capabilities for an Adyen-like provider.
- âœ… Generates deterministic webhook events and dispute lists for integration testing.
- âœ… Makes it easy to evaluate tigrbl strategy coverage by mapping `Capability` values.
- âœ… Ships as a ready-made baseline for extending into production-grade Adyen clients.

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
