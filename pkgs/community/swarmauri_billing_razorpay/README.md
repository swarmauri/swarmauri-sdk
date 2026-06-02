![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_billing_razorpay/">
        <img src="https://static.pepy.tech/badge/swarmauri_billing_razorpay/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_razorpay/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_razorpay.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_razorpay/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_razorpay/">
        <img src="https://img.shields.io/pypi/l/swarmauri_billing_razorpay" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_razorpay/">
        <img src="https://img.shields.io/pypi/v/swarmauri_billing_razorpay?label=swarmauri_billing_razorpay&color=green" alt="PyPI - swarmauri_billing_razorpay"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Billing Razorpay

`swarmauri_billing_razorpay` provides a Razorpay-backed billing provider for the Swarmauri SDK. It connects Swarmauri billing interfaces to the Razorpay Python SDK for items, payment links, orders, payment capture, refunds, subscriptions, invoices, Route transfers, disputes, and webhook signature verification.

## Why Swarmauri Billing Razorpay?

Use `swarmauri_billing_razorpay` when a Swarmauri application needs Razorpay payment flows while keeping application code behind provider-neutral Swarmauri billing interfaces. The provider lets payment links, orders, subscriptions, invoices, refunds, Route transfers, and dispute checks share the same calling style as other Swarmauri billing providers.

## FAQ

### Q: Does this package call live Razorpay APIs?

A: Yes. The provider creates a `razorpay.Client` with `key_id` and `key_secret`, then calls SDK resources such as `item`, `payment_link`, `order`, `payment`, `subscription`, `invoice`, `refund`, and `dispute`.

### Q: Which Razorpay products map to Swarmauri billing flows?

A: Products and prices use Razorpay Items, hosted checkout uses Payment Links, payment intents use Orders, capture/refund use Payments and Refunds APIs, subscription flows use Subscriptions, invoicing uses Invoices, marketplace transfer flows use Route payment transfers, and risk checks use webhook signatures and disputes.

### Q: What credentials are required?

A: Pass Razorpay API credentials as `key_id` and `key_secret`. Use test mode keys for development and load production keys from secure deployment secrets.

## Features

- Razorpay-backed provider class registered as `RazorpayBillingProvider`.
- Item-based product and price creation.
- Payment Link checkout sessions with customer email support.
- Order creation for online payment initialization.
- Payment capture that fetches the authorized payment amount before calling Razorpay capture.
- Refund creation and refund lookup through Razorpay refund APIs.
- Subscription create/cancel support.
- Invoice create, issue, and cancel operations.
- Route transfer support for split-payment workflows.
- Webhook signature verification with `X-Razorpay-Signature` and HMAC-SHA256.
- Dispute listing through Razorpay disputes.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

## Installation

Install with `uv`:

```bash
uv add swarmauri_billing_razorpay
```

Install with `pip`:

```bash
pip install swarmauri_billing_razorpay
```

## Usage

Create a product, price, and Razorpay payment link:

```python
from swarmauri_billing_razorpay import RazorpayBillingProvider
from swarmauri_base.billing import CheckoutRequest, PriceSpec, ProductSpec

provider = RazorpayBillingProvider(
    api_key="razorpay",
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
        customer_email="buyer@example.com",
        idempotency_key="razorpay-checkout-001",
    ),
)

print(product.id, price.id, checkout.url)
```

Create an order-backed payment intent:

```python
from swarmauri_billing_razorpay import RazorpayBillingProvider
from swarmauri_base.billing import PaymentIntentRequest

provider = RazorpayBillingProvider(
    api_key="razorpay",
    key_id="rzp_test_xxxxx",
    key_secret="test_secret",
)

payment = provider.create_payment_intent(
    PaymentIntentRequest(
        amount_minor=49900,
        currency="INR",
        idempotency_key="receipt-1001",
    )
)

print(payment.id, payment.status)
```

Create a partial refund:

```python
from swarmauri_billing_razorpay import RazorpayBillingProvider
from swarmauri_base.billing import PaymentRef, RefundRequest

provider = RazorpayBillingProvider(
    api_key="razorpay",
    key_id="rzp_test_xxxxx",
    key_secret="test_secret",
)

refund = provider.create_refund(
    PaymentRef(id="pay_123", provider="razorpay"),
    RefundRequest(amount_minor=1000, reason="Customer request"),
    idempotency_key="refund-1001",
)

print(refund["id"], refund["status"])
```

## Important Scope Notes

This package uses live Razorpay SDK calls. Runtime behavior depends on Razorpay account settings, enabled products, API credentials, dashboard capture settings, and the status of each payment, order, invoice, subscription, or Route transfer.

## Entry Point

The package exposes a Swarmauri billing provider entry point:

```toml
[project.entry-points.'swarmauri.billing_providers']
RazorpayBillingProvider = "swarmauri_billing_razorpay.provider:RazorpayBillingProvider"
```

## Related Packages

Billing provider packages:

- [swarmauri_billing_adyen](https://pypi.org/project/swarmauri_billing_adyen/)
- [swarmauri_billing_authorize_net](https://pypi.org/project/swarmauri_billing_authorize_net/)
- [swarmauri_billing_braintree](https://pypi.org/project/swarmauri_billing_braintree/)
- [swarmauri_billing_mock](https://pypi.org/project/swarmauri_billing_mock/)
- [swarmauri_billing_paypal](https://pypi.org/project/swarmauri_billing_paypal/)
- [swarmauri_billing_paystack](https://pypi.org/project/swarmauri_billing_paystack/)
- [swarmauri_billing_square](https://pypi.org/project/swarmauri_billing_square/)
- [swarmauri_billing_stripe](https://pypi.org/project/swarmauri_billing_stripe/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines billing capabilities and interfaces.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides billing specs, refs, mixins, and `BillingProviderBase`.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

## Documentation

- [Razorpay provider source](swarmauri_billing_razorpay/provider.py)
- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)
- [Razorpay API documentation](https://razorpay.com/docs/api/)

## License

Apache-2.0

## Contributing

When expanding Razorpay coverage, keep each Swarmauri billing method aligned with the corresponding Razorpay SDK resource, document required credentials and account configuration, and add tests for each changed runtime path.


