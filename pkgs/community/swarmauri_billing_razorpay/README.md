![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_billing_razorpay/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_billing_razorpay" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_razorpay/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_razorpay.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_razorpay/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_billing_razorpay" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_razorpay/">
        <img src="https://img.shields.io/pypi/l/swarmauri_billing_razorpay" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_razorpay/">
        <img src="https://img.shields.io/pypi/v/swarmauri_billing_razorpay?label=swarmauri_billing_razorpay&color=green" alt="PyPI - swarmauri_billing_razorpay"/></a>
</p>

---

# Swarmauri Billing Razorpay

The **Swarmauri Billing Razorpay** package integrates the Razorpay Python SDK into the Swarmauri billing ecosystem. It offers high-fidelity wrappers for Razorpay items, payment links, orders, subscriptions, invoices, and webhook verification routines.

## Features

- ✅ Creates products and prices using Razorpay items and catalog metadata.
- ✅ Generates payment links for hosted checkout flows.
- ✅ Manages orders for online payments, capture, and cancellation workflows.
- ✅ Handles Razorpay subscriptions and invoice issuance APIs.
- ✅ Supports Route marketplace transfers and secure webhook signature validation.

## Installation

```bash
pip install swarmauri_billing_razorpay
```

```bash
uv add swarmauri_billing_razorpay
```

## Usage

```python
from swarmauri_billing_razorpay import RazorpayBillingProvider
from swarmauri_base.billing import CheckoutRequest, PriceSpec, ProductSpec

provider = RazorpayBillingProvider(
    key_id="rzp_test_xxxxx",
    key_secret="test_secret",
)

product = provider.create_product(
    ProductSpec(name="Analytics Plan", description="Advanced dashboards"),
    idempotency_key="razorpay-prod-001",
)

price = provider.create_price(
    product,
    PriceSpec(currency="INR", unit_amount_minor=49900, nickname="Quarterly"),
    idempotency_key="razorpay-price-001",
)

checkout = provider.create_checkout(
    price,
    CheckoutRequest(
        quantity=1,
        success_url="https://merchant.example/razorpay/callback",
        idempotency_key="razorpay-checkout-001",
    ),
)

print(product.id, price.id, checkout.url)
```

## Capability Mapping

Razorpay operations surfaced by this provider emit `Capability` enums that can be translated to tigrbl billing capabilities using `capabilities_to_tigrbl`.

## Contributing

Bug fixes and new Razorpay API coverage are very welcome. Please share reproducible examples when reporting issues so we can iterate quickly.
