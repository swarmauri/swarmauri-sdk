![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_billing_paypal/">
        <img src="https://static.pepy.tech/badge/swarmauri_billing_paypal/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_paypal/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_paypal.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_paypal/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_paypal/">
        <img src="https://img.shields.io/pypi/l/swarmauri_billing_paypal" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_paypal/">
        <img src="https://img.shields.io/pypi/v/swarmauri_billing_paypal?label=swarmauri_billing_paypal&color=green" alt="PyPI - swarmauri_billing_paypal"/></a>
</p>

# Swarmauri Billing PayPal

`swarmauri_billing_paypal` provides a PayPal-shaped billing provider for Swarmauri checkout, payment, subscription, invoicing, refund, customer, payout, reporting, and webhook workflows. It is a deterministic stub provider for local development, integration tests, provider-contract validation, and PayPal-style billing examples.

## Why Swarmauri Billing PayPal?

`swarmauri_billing_paypal` lets Swarmauri billing workflows use PayPal-like IDs, statuses, checkout URLs, invoice refs, payout refs, and webhook payloads without requiring live PayPal credentials. It is useful when application code needs to exercise the same Swarmauri billing interfaces that a production PayPal provider would implement.

## FAQ

### Q: Does this package call live PayPal APIs?

A: No. It returns deterministic PayPal-shaped responses and does not call PayPal REST, GraphQL, checkout, payout, or webhook verification services.

### Q: Which Swarmauri billing capabilities does it cover?

A: It covers products, prices, hosted checkout, online payments, subscriptions, invoicing, refunds, customers, payment methods, payouts, reports, and webhooks.

### Q: When should I use this package?

A: Use it for local billing workflows, provider strategy tests, documentation examples, and contract tests that need PayPal-style behavior through Swarmauri billing abstractions.

## Features

- PayPal-style provider class registered as `PayPalBillingProvider`.
- Supports products, prices, hosted checkout, online payments, subscriptions, invoicing, refunds, customers, payment methods, payouts, reports, and webhooks.
- Returns deterministic provider-shaped payloads and Swarmauri billing refs for repeatable tests.
- Models PayPal-like payment statuses such as `CREATED`, `APPROVED`, `COMPLETED`, and `CANCELED`.
- Provides invoice status transitions such as `DRAFT`, `SENT`, `VOIDED`, and `BAD_DEBT`.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

## Installation

Install with `uv`:

```bash
uv add swarmauri_billing_paypal
```

Install with `pip`:

```bash
pip install swarmauri_billing_paypal
```

## Usage

Create a product, price, and PayPal-style checkout session:

```python
from swarmauri_billing_paypal import PayPalBillingProvider
from swarmauri_base.billing import CheckoutRequest, PriceSpec, ProductSpec

provider = PayPalBillingProvider(api_key="paypal-sandbox-secret")

product = provider.create_product(
    ProductSpec(name="Workspace"),
    idempotency_key="paypal-prod-1",
)
price = provider.create_price(
    product,
    PriceSpec(currency="USD", unit_amount_minor=2500),
    idempotency_key="paypal-price-1",
)
checkout = provider.create_checkout(
    price,
    CheckoutRequest(success_url="https://example.com/return"),
)

print(product.id, price.id, checkout.url)
```

Create and capture a PayPal-style payment:

```python
from swarmauri_billing_paypal import PayPalBillingProvider
from swarmauri_base.billing import PaymentIntentRequest

provider = PayPalBillingProvider(api_key="paypal-sandbox-secret")

payment = provider.create_payment_intent(
    PaymentIntentRequest(amount_minor=1500, currency="USD", confirm=True)
)
captured = provider.capture_payment(payment.id, idempotency_key="paypal-capture-1")

print(payment.status, captured.status)
```

## Important Scope Notes

This package is a Swarmauri billing provider stub. It does not process real payments, create live PayPal checkout sessions, move payout funds, validate production webhook signatures, or reconcile balances with PayPal. Use it for tests, examples, strategy validation, and as a starting point for a live PayPal provider.

## Entry Point

The package exposes a Swarmauri billing provider entry point:

```toml
[project.entry-points.'swarmauri.billing_providers']
PayPalBillingProvider = "swarmauri_billing_paypal.provider:PayPalBillingProvider"
```

## Related Packages

Billing provider packages:

- [swarmauri_billing_adyen](https://pypi.org/project/swarmauri_billing_adyen/)
- [swarmauri_billing_authorize_net](https://pypi.org/project/swarmauri_billing_authorize_net/)
- [swarmauri_billing_braintree](https://pypi.org/project/swarmauri_billing_braintree/)
- [swarmauri_billing_mock](https://pypi.org/project/swarmauri_billing_mock/)
- [swarmauri_billing_paystack](https://pypi.org/project/swarmauri_billing_paystack/)
- [swarmauri_billing_razorpay](https://pypi.org/project/swarmauri_billing_razorpay/)
- [swarmauri_billing_square](https://pypi.org/project/swarmauri_billing_square/)
- [swarmauri_billing_stripe](https://pypi.org/project/swarmauri_billing_stripe/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines billing capabilities and interfaces.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides billing specs, refs, mixins, and `BillingProviderBase`.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

## License

Apache-2.0

## Contributing

If you connect this provider to live PayPal APIs, preserve deterministic tests, document required credentials and webhook behavior, and add coverage for each supported billing capability.
