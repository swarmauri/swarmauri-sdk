![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_billing_braintree/">
        <img src="https://static.pepy.tech/badge/swarmauri_billing_braintree/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_braintree/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_braintree.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_braintree/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_braintree/">
        <img src="https://img.shields.io/pypi/l/swarmauri_billing_braintree" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_braintree/">
        <img src="https://img.shields.io/pypi/v/swarmauri_billing_braintree?label=swarmauri_billing_braintree&color=green" alt="PyPI - swarmauri_billing_braintree"/></a>
</p>

# Swarmauri Billing Braintree

`swarmauri_billing_braintree` provides a Braintree-shaped billing provider for Swarmauri checkout, payment, subscription, refund, customer-vault, reporting, risk, and webhook workflows. It is a deterministic stub provider for local development, tests, and provider-contract validation.

## Why Swarmauri Billing Braintree?

`swarmauri_billing_braintree` gives billing integrators a Braintree-shaped provider for checkout, payment, subscription, refund, customer-vault, reporting, risk, and webhook tests. It keeps Braintree-style behavior available through Swarmauri billing interfaces without requiring the live Braintree SDK.

## FAQ

### Q: Does this package call live Braintree APIs?

A: No. It is a deterministic stub provider for tests, examples, and provider-contract validation.

### Q: Which Swarmauri billing flows does it cover?

A: It covers products, prices, hosted checkout, online payments, subscriptions, refunds, customers, payment methods, reports, risk, and webhooks.

### Q: Why use this instead of `swarmauri_billing_mock`?

A: Use this package when you want Braintree-shaped IDs, statuses, checkout URLs, and webhook headers. Use a generic mock when gateway-specific behavior is not relevant.

## Features

- Braintree-style provider class registered as `BraintreeBillingProvider`.
- Supports products, prices, hosted checkout, online payments, subscriptions, refunds, customers, payment methods, reports, risk, and webhooks.
- Returns deterministic provider-shaped payloads and Swarmauri billing refs for repeatable assertions.
- Models Braintree-like transaction statuses such as `AUTHORIZED`, `SETTLED`, `VOIDED`, and `SUBMITTED_FOR_SETTLEMENT`.
- Provides webhook parsing and signature-check hooks for contract tests.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

## Installation

Install with `uv`:

```bash
uv add swarmauri_billing_braintree
```

Install with `pip`:

```bash
pip install swarmauri_billing_braintree
```

## Usage

Authorize and capture a Braintree-style payment:

```python
from swarmauri_billing_braintree import BraintreeBillingProvider
from swarmauri_base.billing import PaymentIntentRequest

provider = BraintreeBillingProvider(api_key="braintree-sandbox-key")

payment = provider.create_payment_intent(
    PaymentIntentRequest(
        amount_minor=1500,
        currency="USD",
        confirm=True,
    )
)
captured = provider.capture_payment(payment.id, idempotency_key="capture-bt-1")

print(payment.status, captured.status)
```

Create a plan, price, and checkout session:

```python
from swarmauri_billing_braintree import BraintreeBillingProvider
from swarmauri_base.billing import CheckoutRequest, PriceSpec, ProductSpec

provider = BraintreeBillingProvider(api_key="braintree-sandbox-key")

plan = provider.create_product(
    ProductSpec(name="SaaS Plan"),
    idempotency_key="plan-bt-1",
)
price = provider.create_price(
    plan,
    PriceSpec(currency="USD", unit_amount_minor=2900),
    idempotency_key="price-bt-1",
)
checkout = provider.create_checkout(price, CheckoutRequest(quantity=1))

print(checkout.url)
```

## Important Scope Notes

This package is a Swarmauri billing provider stub. It does not call the live Braintree REST, GraphQL, or SDK APIs, process real cards, perform settlement, or validate production webhook signatures. Use it for tests, examples, strategy validation, and as a starting point for a live Braintree provider.

## Entry Point

The package exposes a Swarmauri billing provider entry point:

```toml
[project.entry-points.'swarmauri.billing_providers']
BraintreeBillingProvider = "swarmauri_billing_braintree.provider:BraintreeBillingProvider"
```

## Related Packages

Billing provider packages:

- [swarmauri_billing_adyen](https://pypi.org/project/swarmauri_billing_adyen/)
- [swarmauri_billing_authorize_net](https://pypi.org/project/swarmauri_billing_authorize_net/)
- [swarmauri_billing_mock](https://pypi.org/project/swarmauri_billing_mock/)
- [swarmauri_billing_paypal](https://pypi.org/project/swarmauri_billing_paypal/)
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

If you connect this provider to live Braintree APIs, preserve deterministic tests, document required credentials and webhook behavior, and add coverage for each supported billing capability.
