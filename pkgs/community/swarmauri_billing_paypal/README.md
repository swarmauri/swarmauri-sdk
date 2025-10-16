![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_billing_paypal/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_billing_paypal" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_paypal/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_paypal.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_paypal/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_billing_paypal" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_paypal/">
        <img src="https://img.shields.io/pypi/l/swarmauri_billing_paypal" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_paypal/">
        <img src="https://img.shields.io/pypi/v/swarmauri_billing_paypal?label=swarmauri_billing_paypal&color=green" alt="PyPI - swarmauri_billing_paypal"/></a>
</p>

---

# Swarmauri Billing PayPal

The **Swarmauri Billing PayPal** package delivers a PayPal-oriented billing provider that complies with Swarmauri's billing abstractions. It focuses on hosted checkout, direct captures, subscriptions, invoicing, payouts, and webhook parsing so PayPal integrations can be developed without re-learning the Swarmauri interfaces.

## Features

- ✅ Generates deterministic IDs and payload echoes to keep local testing predictable.
- ✅ Covers PayPal's core primitives: products, plans, hosted checkout sessions, invoices, refunds, customers, payment methods, payouts, and reports.
- ✅ Returns serializable dictionaries that map cleanly onto Swarmauri billing references and capability checks.
- ✅ Ships as a standalone package that can be swapped for real PayPal SDK logic when you are production ready.

## Installation

Install from PyPI using either `pip` or `uv`:

```bash
pip install swarmauri_billing_paypal
```

```bash
uv add swarmauri_billing_paypal
```

## Usage

```python
from swarmauri_billing_paypal import PayPalBillingProvider
from swarmauri_base.billing import CheckoutRequest, ProductSpec, PriceSpec

provider = PayPalBillingProvider(api_key="sandbox-secret")

product = provider.create_product(
    ProductSpec(payload={"name": "Workspace"}),
    idempotency_key="paypal-prod-1",
)
price = provider.create_price(
    product,
    PriceSpec(payload={"currency": "USD", "unit_amount_minor": 2500}),
    idempotency_key="paypal-price-1",
)
checkout = provider.create_checkout(
    price,
    CheckoutRequest(payload={"success_url": "https://example.com/return"}),
)

print(product.id, price.id, checkout.url)
```

## Capability Mapping

Capabilities reported by the provider are translated to `tigrbl_billing` semantics with `swarmauri_core.billing.capabilities_to_tigrbl`. This allows the stub to coexist with production-grade PayPal SDK implementations while sharing tests and feature flags.

## Contributing

Pull requests that replace the stubbed responses with actual PayPal REST API calls are encouraged. Please include reproducible examples and documentation updates when expanding functionality.
