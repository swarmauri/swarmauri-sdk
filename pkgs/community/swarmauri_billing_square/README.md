![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_billing_square/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_billing_square" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_square/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_square.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_square/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_billing_square" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_square/">
        <img src="https://img.shields.io/pypi/l/swarmauri_billing_square" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_square/">
        <img src="https://img.shields.io/pypi/v/swarmauri_billing_square?label=swarmauri_billing_square&color=green" alt="PyPI - swarmauri_billing_square"/></a>
</p>

---

# Swarmauri Billing Square

The **Swarmauri Billing Square** package delivers a Square-backed billing provider that speaks the Swarmauri billing interfaces. It uses the official Square Python SDK to manage catalog items, hosted checkout links, card-not-present payments, subscriptions, and invoices.

## Features

- ✅ Turns Square catalog items and variations into Swarmauri product and price references.
- ✅ Generates hosted checkout links through the Payments API Link service.
- ✅ Supports payment intents, captures, and cancellations using Square's server APIs.
- ✅ Manages subscriptions and invoices, including publishing and cancellation flows.
- ✅ Surfaces marketplace fee splits and dispute listings for downstream automation.

## Installation

```bash
pip install swarmauri_billing_square
```

```bash
uv add swarmauri_billing_square
```

## Usage

```python
from swarmauri_billing_square import SquareBillingProvider
from swarmauri_base.billing import CheckoutRequest, PriceSpec, ProductSpec

provider = SquareBillingProvider(
    access_token="sq0atp-...",
    location_id="L8899XYZ",
)

product = provider.create_product(
    ProductSpec(name="Digital Membership", description="Premium access"),
    idempotency_key="prod-square-001",
)

price = provider.create_price(
    product,
    PriceSpec(currency="USD", unit_amount_minor=2500, nickname="Monthly"),
    idempotency_key="price-square-001",
)

checkout = provider.create_checkout(
    price,
    CheckoutRequest(
        quantity=1,
        success_url="https://merchant.example/success",
        cancel_url="https://merchant.example/cancel",
        idempotency_key="checkout-square-001",
    ),
)

print(product.id, price.id, checkout.url)
```

## Capability Mapping

Square capabilities advertised by this provider map to `swarmauri_core.billing.Capability`. Use `capabilities_to_tigrbl` to translate capabilities to the tigrbl billing vocabulary when required.

## Contributing

Community improvements are welcome! Enhancements that broaden Square API coverage or harden error handling are greatly appreciated.
