![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_billing_square/">
        <img src="https://static.pepy.tech/badge/swarmauri_billing_square/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_square/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_square.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_square/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_square/">
        <img src="https://img.shields.io/pypi/l/swarmauri_billing_square" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_square/">
        <img src="https://img.shields.io/pypi/v/swarmauri_billing_square?label=swarmauri_billing_square&color=green" alt="PyPI - swarmauri_billing_square"/></a>
</p>

# Swarmauri Billing Square

`swarmauri_billing_square` provides a Square-backed billing provider for the Swarmauri SDK. It connects Swarmauri billing interfaces to the current Square Python SDK for catalog items, item variations, payment links, payments, captures, cancellations, refunds, subscriptions, invoices, application-fee payments, disputes, and webhook signature verification.

## Why Swarmauri Billing Square?

Use `swarmauri_billing_square` when a Swarmauri application needs Square commerce workflows behind provider-neutral billing interfaces. The provider maps Square Catalog, Checkout Payment Links, Payments, Refunds, Subscriptions, Invoices, and Disputes into Swarmauri billing refs so application code can share one billing abstraction across providers.

## FAQ

### Q: Does this package call live Square APIs?

A: Yes. It creates a `Square` SDK client with an access token and environment, then calls resources such as `catalog`, `checkout.payment_links`, `payments`, `refunds`, `subscriptions`, `invoices`, and `disputes`.

### Q: Which Square APIs are used?

A: Products and prices use Catalog objects, hosted checkout uses Payment Links, online payments use Payments, refunds use Refunds, subscription flows use Subscriptions, invoices use Invoices, split-like platform-fee workflows use Payments with `app_fee_money`, and risk checks use webhook signature verification and dispute listing.

### Q: What configuration is required?

A: Pass `access_token`, `location_id`, and optionally `environment="sandbox"` or `environment="production"`. Use sandbox credentials for development and secure production access tokens through deployment secrets.

## Features

- Square-backed provider class registered as `SquareBillingProvider`.
- Catalog item and item variation creation for product and price references.
- Payment Link checkout sessions with redirect URL and buyer email support.
- Payment creation, completion, and cancellation through the Payments API.
- Refund creation and lookup through the Refunds API.
- Subscription create/cancel support.
- Invoice create, publish, and cancel support using Square invoice versions.
- Application-fee payment support for marketplace-style platform fees.
- Square webhook verification through `square.utils.webhooks_helper.verify_signature`.
- Dispute listing for operational review workflows.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

## Installation

Install with `uv`:

```bash
uv add swarmauri_billing_square
```

Install with `pip`:

```bash
pip install swarmauri_billing_square
```

## Usage

Create a catalog item, item variation, and Square payment link:

```python
from swarmauri_billing_square import SquareBillingProvider
from swarmauri_base.billing import CheckoutRequest, PriceSpec, ProductSpec

provider = SquareBillingProvider(
    api_key="square",
    access_token="sq0atp-...",
    location_id="L8899XYZ",
    environment="sandbox",
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
        customer_email="buyer@example.com",
        idempotency_key="checkout-square-001",
    ),
)

print(product.id, price.id, checkout.url)
```

Create and complete a Square payment:

```python
from swarmauri_billing_square import SquareBillingProvider
from swarmauri_base.billing import PaymentIntentRequest

provider = SquareBillingProvider(
    api_key="square",
    access_token="sq0atp-...",
    location_id="L8899XYZ",
)

payment = provider.create_payment_intent(
    PaymentIntentRequest(
        amount_minor=2500,
        currency="USD",
        payment_method_id="cnon:card-nonce-ok",
        capture=False,
        idempotency_key="payment-square-001",
    )
)
captured = provider.capture_payment(payment.id)

print(payment.status, captured.status)
```

Verify a Square webhook signature:

```python
from swarmauri_billing_square import SquareBillingProvider

provider = SquareBillingProvider(
    api_key="square",
    access_token="sq0atp-...",
    location_id="L8899XYZ",
)

valid = provider.verify_webhook_signature(
    raw_body=b'{"merchant_id":"ML123"}',
    headers={
        "X-Square-Hmacsha256-Signature": "signature-from-square",
        "X-Square-Notification-Url": "https://merchant.example/webhooks/square",
    },
    secret="webhook-signature-key",
)

print(valid)
```

## Important Scope Notes

This package uses live Square SDK calls. Runtime behavior depends on Square account configuration, enabled APIs, access-token permissions, valid `location_id` values, catalog object state, invoice versions, and payment status.

## Entry Point

The package exposes a Swarmauri billing provider entry point:

```toml
[project.entry-points.'swarmauri.billing_providers']
SquareBillingProvider = "swarmauri_billing_square.provider:SquareBillingProvider"
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
- [swarmauri_billing_stripe](https://pypi.org/project/swarmauri_billing_stripe/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines billing capabilities and interfaces.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides billing specs, refs, mixins, and `BillingProviderBase`.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

## Documentation

- [Square provider source](swarmauri_billing_square/provider.py)
- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)
- [Square API documentation](https://developer.squareup.com/reference/square)

## License

Apache-2.0

## Contributing

When expanding Square coverage, align each method with the current Square Python SDK, document required permissions and account settings, and add tests for each changed runtime path.
