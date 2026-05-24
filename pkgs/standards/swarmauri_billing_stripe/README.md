![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_billing_stripe/">
        <img src="https://static.pepy.tech/badge/swarmauri_billing_stripe/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_billing_stripe/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_billing_stripe.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_stripe/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_stripe/">
        <img src="https://img.shields.io/pypi/l/swarmauri_billing_stripe" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_stripe/">
        <img src="https://img.shields.io/pypi/v/swarmauri_billing_stripe?label=swarmauri_billing_stripe&color=green" alt="PyPI - swarmauri_billing_stripe"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Billing Stripe

`swarmauri_billing_stripe` provides a Stripe-backed billing provider for the Swarmauri SDK. It connects Swarmauri billing interfaces to the official Stripe Python SDK for products, prices, Checkout Sessions, Payment Intents, captures, cancellations, refunds, subscriptions, invoices, Stripe Connect destination charges, disputes, and webhook signature verification.

## Why Swarmauri Billing Stripe?

Use `swarmauri_billing_stripe` when a Swarmauri application needs production Stripe billing workflows while keeping application code behind provider-neutral billing interfaces. The provider maps Stripe Billing, Checkout, Payment Intents, Refunds, Invoicing, Subscriptions, Connect, and Disputes into Swarmauri refs and specs.

## FAQ

### Q: Does this package call live Stripe APIs?

A: Yes. The provider configures the official `stripe` Python SDK with `api_key` and calls Stripe resources such as `Product`, `Price`, `checkout.Session`, `PaymentIntent`, `Refund`, `Subscription`, `Invoice`, and `Dispute`.

### Q: Which Stripe workflows are supported?

A: It supports product and price creation, hosted checkout, payment intent creation, manual capture, payment intent cancellation, refund create/retrieve, subscription create/cancel, invoice create/finalize/void/mark-uncollectible, Connect destination charges with application fees, webhook signature validation, and dispute listing.

### Q: What credential is required?

A: Pass a Stripe secret key as `api_key`, such as a test key beginning with `sk_test_`. Production keys should be provided through secure deployment secrets.

## Features

- Stripe-backed provider class registered as `StripeBillingProvider`.
- Product and price creation with metadata support.
- Hosted Checkout Session creation for one-time payments.
- Payment Intent creation with automatic or manual capture.
- Payment capture and cancellation through Stripe Payment Intents.
- Refund creation and lookup through Stripe Refunds.
- Subscription creation and cancellation with Stripe prices.
- Invoice item creation plus invoice lifecycle operations.
- Stripe Connect destination-charge support with application fees.
- Webhook signature verification through `stripe.Webhook.construct_event`.
- Dispute listing for operational review workflows.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

## Installation

Install with `uv`:

```bash
uv add swarmauri_billing_stripe
```

Install with `pip`:

```bash
pip install swarmauri_billing_stripe
```

## Usage

Create a product, price, and Stripe Checkout Session:

```python
from swarmauri_billing_stripe import StripeBillingProvider
from swarmauri_base.billing import CheckoutRequest, PriceSpec, ProductSpec

provider = StripeBillingProvider(api_key="sk_test_123")

product = provider.create_product(
    ProductSpec(name="Starter", description="Starter subscription"),
    idempotency_key="stripe-prod-001",
)
price = provider.create_price(
    product,
    PriceSpec(currency="USD", unit_amount_minor=1000, nickname="Starter monthly"),
    idempotency_key="stripe-price-001",
)
checkout = provider.create_checkout(
    price,
    CheckoutRequest(
        quantity=1,
        success_url="https://example.com/success",
        cancel_url="https://example.com/cancel",
        customer_email="buyer@example.com",
        idempotency_key="stripe-checkout-001",
    ),
)

print(product.id, price.id, checkout.url)
```

Create and capture a manual Payment Intent:

```python
from swarmauri_billing_stripe import StripeBillingProvider
from swarmauri_base.billing import PaymentIntentRequest

provider = StripeBillingProvider(api_key="sk_test_123")

payment = provider.create_payment_intent(
    PaymentIntentRequest(
        amount_minor=2500,
        currency="USD",
        payment_method_id="pm_card_visa",
        confirm=True,
        capture=False,
        idempotency_key="stripe-payment-001",
    )
)
captured = provider.capture_payment(payment.id, idempotency_key="stripe-capture-001")

print(payment.status, captured.status)
```

Verify a Stripe webhook signature:

```python
from swarmauri_billing_stripe import StripeBillingProvider

provider = StripeBillingProvider(api_key="sk_test_123")

valid = provider.verify_webhook_signature(
    raw_body=b'{"id":"evt_test","object":"event"}',
    headers={"Stripe-Signature": "t=...,v1=..."},
    secret="whsec_...",
)

print(valid)
```

## Important Scope Notes

This package uses live Stripe SDK calls. Runtime behavior depends on Stripe account settings, API version, enabled payment methods, test or live mode, Checkout configuration, Connect account setup, and webhook endpoint secrets.

## Entry Point

The package exposes a Swarmauri billing provider entry point:

```toml
[project.entry-points.'swarmauri.billing_providers']
StripeBillingProvider = "swarmauri_billing_stripe.provider:StripeBillingProvider"
```

## Related Packages

Billing provider packages:

- [swarmauri_billing_adyen](https://pypi.org/project/swarmauri_billing_adyen/)
- [swarmauri_billing_authorize_net](https://pypi.org/project/swarmauri_billing_authorize_net/)
- [swarmauri_billing_braintree](https://pypi.org/project/swarmauri_billing_braintree/)
- [swarmauri_billing_mock](https://pypi.org/project/swarmauri_billing_mock/)
- [swarmauri_billing_paypal](https://pypi.org/project/swarmauri_billing_paypal/)
- [swarmauri_billing_paystack](https://pypi.org/project/swarmauri_billing_paystack/)
- [swarmauri_billing_razorpay](https://pypi.org/project/swarmauri_billing_razorpay/)
- [swarmauri_billing_square](https://pypi.org/project/swarmauri_billing_square/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines billing capabilities and interfaces.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides billing specs, refs, mixins, and `BillingProviderBase`.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

## Documentation

- [Stripe provider source](swarmauri_billing_stripe/provider.py)
- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)
- [Stripe API documentation](https://docs.stripe.com/api)

## License

Apache-2.0

## Contributing

When expanding Stripe coverage, keep each Swarmauri billing method aligned with the official Stripe Python SDK, document required Stripe account configuration, and add tests for each changed runtime path.


