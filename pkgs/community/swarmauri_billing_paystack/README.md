![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_billing_paystack/">
        <img src="https://static.pepy.tech/badge/swarmauri_billing_paystack/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_paystack/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_paystack.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_paystack/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_paystack/">
        <img src="https://img.shields.io/pypi/l/swarmauri_billing_paystack" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_paystack/">
        <img src="https://img.shields.io/pypi/v/swarmauri_billing_paystack?label=swarmauri_billing_paystack&color=green" alt="PyPI - swarmauri_billing_paystack"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Billing Paystack

`swarmauri_billing_paystack` provides a Paystack-backed billing provider for the Swarmauri SDK. It connects Swarmauri billing interfaces to the `paystackapi` SDK for products, price-like product codes, hosted checkout, payment initialization, subscriptions, invoices, refunds, marketplace splits, split charges, disputes, and Paystack webhook HMAC verification.

## Why Swarmauri Billing Paystack?

Use `swarmauri_billing_paystack` when a Swarmauri application needs Paystack payment flows without coupling business logic directly to Paystack SDK calls. The provider keeps Paystack products, transactions, subscriptions, invoices, refunds, splits, and risk checks behind the same Swarmauri billing interfaces used by other billing providers.

## FAQ

### Q: Does this package call live Paystack APIs?

A: Yes. The provider imports `paystackapi`, sets `Paystack.SECRET_KEY`, and calls SDK classes such as `Transaction`, `Product`, `Subscription`, `Invoice`, `TransactionSplit`, `Refund`, and `Dispute`.

### Q: Which Swarmauri billing flows does it support?

A: It supports product creation, price-like product creation, hosted checkout, payment initialization, subscription create/cancel, invoice create/finalize/archive/uncollectible flows, refund create/fetch, marketplace split creation, split charges, dispute listing, and webhook signature verification.

### Q: What credential does it need?

A: Pass a Paystack secret key through `secret_key`. Tests and examples use sandbox-style keys such as `sk_test_...`; production deployments should load secrets from a secure environment or vault.

## Features

- Paystack-backed provider class registered as `PaystackBillingProvider`.
- Product and price workflows built on Paystack product APIs.
- Hosted checkout and payment intent initialization through Paystack transactions.
- Subscription lifecycle methods for creating and disabling subscriptions.
- Invoice creation and notification-oriented invoice actions.
- Refund creation and lookup through Paystack refund APIs.
- Marketplace split creation and split-charge initialization.
- Paystack webhook signature verification with `X-Paystack-Signature` and HMAC-SHA512.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

## Installation

Install with `uv`:

```bash
uv add swarmauri_billing_paystack
```

Install with `pip`:

```bash
pip install swarmauri_billing_paystack
```

## Usage

Create a product, price, and Paystack checkout session:

```python
from swarmauri_billing_paystack import PaystackBillingProvider
from swarmauri_base.billing import CheckoutRequest, PriceSpec, ProductSpec

provider = PaystackBillingProvider(
    api_key="paystack",
    secret_key="sk_test_xxxxx",
)

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

Initialize a Paystack payment intent:

```python
from swarmauri_billing_paystack import PaystackBillingProvider
from swarmauri_base.billing import PaymentIntentRequest

provider = PaystackBillingProvider(
    api_key="paystack",
    secret_key="sk_test_xxxxx",
)

payment = provider.create_payment_intent(
    PaymentIntentRequest(
        amount_minor=500000,
        currency="NGN",
        idempotency_key="paystack-payment-001",
        metadata={"order_id": "order-1001"},
    )
)

print(payment.id, payment.status)
```

Verify a Paystack webhook signature:

```python
from swarmauri_billing_paystack import PaystackBillingProvider

provider = PaystackBillingProvider(
    api_key="paystack",
    secret_key="sk_test_xxxxx",
)

is_valid = provider.verify_webhook_signature(
    raw_body=b'{"event":"charge.success"}',
    headers={"X-Paystack-Signature": "expected-hmac"},
    secret="sk_test_xxxxx",
)

print(is_valid)
```

## Important Scope Notes

This package uses Paystack SDK calls for provider operations. Network access, Paystack credentials, API availability, account configuration, and Paystack response formats affect runtime behavior. Use sandbox keys for development and isolate live credentials through deployment secrets.

## Entry Point

The package exposes a Swarmauri billing provider entry point:

```toml
[project.entry-points.'swarmauri.billing_providers']
PaystackBillingProvider = "swarmauri_billing_paystack.provider:PaystackBillingProvider"
```

## Related Packages

Billing provider packages:

- [swarmauri_billing_adyen](https://pypi.org/project/swarmauri_billing_adyen/)
- [swarmauri_billing_authorize_net](https://pypi.org/project/swarmauri_billing_authorize_net/)
- [swarmauri_billing_braintree](https://pypi.org/project/swarmauri_billing_braintree/)
- [swarmauri_billing_mock](https://pypi.org/project/swarmauri_billing_mock/)
- [swarmauri_billing_paypal](https://pypi.org/project/swarmauri_billing_paypal/)
- [swarmauri_billing_razorpay](https://pypi.org/project/swarmauri_billing_razorpay/)
- [swarmauri_billing_square](https://pypi.org/project/swarmauri_billing_square/)
- [swarmauri_billing_stripe](https://pypi.org/project/swarmauri_billing_stripe/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines billing capabilities and interfaces.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides billing specs, refs, mixins, and `BillingProviderBase`.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

## Documentation

- [Paystack provider source](swarmauri_billing_paystack/provider.py)
- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)
- [Paystack API documentation](https://paystack.com/docs/api/)

## License

Apache-2.0

## Contributing

Contributions that expand Paystack coverage or improve resiliency are welcome. Include request and response traces with secrets redacted, update usage examples, and add tests for each billing capability you change.


