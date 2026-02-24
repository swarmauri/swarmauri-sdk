![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_billing_stripe/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_billing_stripe" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_billing_stripe/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_billing_stripe.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_stripe/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_billing_stripe" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_stripe/">
        <img src="https://img.shields.io/pypi/l/swarmauri_billing_stripe" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_stripe/">
        <img src="https://img.shields.io/pypi/v/swarmauri_billing_stripe?label=swarmauri_billing_stripe&color=green" alt="PyPI - swarmauri_billing_stripe"/></a>
</p>

---

# Swarmauri Billing Stripe

The **Swarmauri Billing Stripe** package provides a Stripe-aligned billing provider that plugs into the Swarmauri billing interfaces. It offers a consistent API surface across hosted checkout, invoicing, subscriptions, promotions, and more while keeping responses serializable via Pydantic models.

## Features

- ✅ Implements every Swarmauri billing capability for a Stripe-style provider stub.
- ✅ Returns strongly-typed Pydantic models for references, specs, and webhook events.
- ✅ Maps Swarmauri capabilities to the `tigrbl_billing` strategy catalog for easier interoperability.
- ✅ Serves as a ready-to-extend template for production-grade Stripe integrations.

## Installation

Install from PyPI using either `pip` or `uv`:

```bash
pip install swarmauri_billing_stripe
```

```bash
uv add swarmauri_billing_stripe
```

## Usage

```python
from swarmauri_billing_stripe import StripeBillingProvider
from swarmauri_base.billing import CheckoutRequest, ProductSpec, PriceSpec

provider = StripeBillingProvider(api_key="sk_test_123")

product_ref = provider.create_product(ProductSpec(payload={"name": "Starter"}), idempotency_key="prod-1")
price_ref = provider.create_price(product_ref, PriceSpec(payload={"unit_amount": 1000, "currency": "USD"}), idempotency_key="price-1")
checkout = provider.create_checkout(price_ref, CheckoutRequest(payload={"success_url": "https://example.com/success"}))

print(product_ref.id, price_ref.id, checkout.id)
```

## Capability Mapping

The provider exposes [`Capability`](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/core/swarmauri_core/billing/enums.py) identifiers that translate into `tigrbl_billing` API capabilities using `swarmauri_core.billing.capabilities_to_tigrbl`. This makes it straightforward to reason about downstream platform coverage.

## Contributing

We welcome enhancements that bring this stub closer to real Stripe HTTP workflows. Please open an issue or submit a pull request with reproducible examples.
