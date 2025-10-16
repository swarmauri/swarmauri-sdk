![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_billing_paystack/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_billing_paystack" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_paystack/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_paystack.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_paystack/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_billing_paystack" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_paystack/">
        <img src="https://img.shields.io/pypi/l/swarmauri_billing_paystack" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_paystack/">
        <img src="https://img.shields.io/pypi/v/swarmauri_billing_paystack?label=swarmauri_billing_paystack&color=green" alt="PyPI - swarmauri_billing_paystack"/></a>
</p>

---

# Swarmauri Billing Paystack

The **Swarmauri Billing Paystack** package provides an integration between the Paystack API and the Swarmauri billing interfaces. It exposes product, price, hosted checkout, payment intent, subscription, invoice, and split operations powered by the `paystackapi` SDK.

## Features

- ✅ Manages Paystack products and price codes with Swarmauri references.
- ✅ Initializes hosted checkout sessions and card-not-present payments.
- ✅ Integrates Paystack's subscription lifecycle endpoints.
- ✅ Issues invoices and forwards notifications as required.
- ✅ Configures split codes and marketplace charges while validating webhooks.

## Installation

```bash
pip install swarmauri_billing_paystack
```

```bash
uv add swarmauri_billing_paystack
```

## Usage

```python
from swarmauri_billing_paystack import PaystackBillingProvider
from swarmauri_base.billing import CheckoutRequest, PriceSpec, ProductSpec

provider = PaystackBillingProvider(secret_key="sk_test_xxxxx")

product = provider.create_product(
    ProductSpec(name="Learning Portal", description="Online academy access"),
    idempotency_key="paystack-prod-001",
)

price = provider.create_price(
    product,
    PriceSpec(currency="NGN", unit_amount_minor=150000, nickname="Annual"),
    idempotency_key="paystack-price-001",
)

checkout = provider.create_checkout(
    price,
    CheckoutRequest(
        quantity=1,
        success_url="https://merchant.example/paystack/callback",
        customer_email="learner@example.com",
        idempotency_key="paystack-checkout-001",
    ),
)

print(product.id, price.id, checkout.url)
```

## Capability Mapping

All Paystack features surfaced here align with `swarmauri_core.billing.Capability`. Translate them to tigrbl using `capabilities_to_tigrbl` when coordinating with legacy services.

## Contributing

Contributions that expand Paystack coverage or improve resiliency are appreciated. Please include request/response traces (with secrets redacted) when filing bugs.
