![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_billing_mock/">
        <img src="https://static.pepy.tech/badge/swarmauri_billing_mock/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_billing_mock/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_billing_mock.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_mock/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_mock/">
        <img src="https://img.shields.io/pypi/l/swarmauri_billing_mock" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_mock/">
        <img src="https://img.shields.io/pypi/v/swarmauri_billing_mock?label=swarmauri_billing_mock&color=green" alt="PyPI - swarmauri_billing_mock"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Billing Mock

`swarmauri_billing_mock` provides a deterministic in-memory billing provider for Swarmauri test suites, examples, and provider contract checks. It implements the full Swarmauri billing surface without network calls so applications can exercise products, prices, checkout, payments, subscriptions, invoices, refunds, customers, payment methods, payouts, transfers, reports, webhooks, coupons, and promotions through one predictable provider.

## Why Swarmauri Billing Mock?

Use this package when billing code needs repeatable behavior without a real payment processor. It is useful for unit tests, documentation examples, local development, and compatibility checks for code that targets `BillingProviderBase` and the Swarmauri billing mixins.

## FAQ

### Q: Does this package call a live billing API?

A: No. The mock provider is intentionally local and deterministic. It returns Swarmauri-shaped billing payloads and never reaches external payment networks.

### Q: Which billing capabilities does it advertise?

A: It advertises every Swarmauri billing capability through `ALL_CAPABILITIES`, including checkout, online payments, subscriptions, invoices, marketplace splits, refunds, customers, payment methods, payouts, balance transfers, reports, webhooks, coupons, and promotions.

### Q: When should I use it instead of a real provider?

A: Use it in tests, examples, local workflows, and provider-neutral integration checks. Use Stripe, PayPal, Square, Braintree, Adyen, Authorize.Net, Paystack, or Razorpay packages when code needs a live provider API.

## Features

- Implements all billing mixins with predictable outputs.
- Provides fast billing feedback without network calls.
- Supports tests that need all Swarmauri billing capabilities available.
- Demonstrates how to subclass `BillingProviderBase` for custom billing flows.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

Install with `uv`:

```bash
uv add swarmauri_billing_mock
```

Install with `pip`:

```bash
pip install swarmauri_billing_mock
```

## Usage

```python
from swarmauri_billing_mock import MockBillingProvider
from swarmauri_base.billing import ProductSpec

provider = MockBillingProvider(api_key="mock-key")
product = provider.create_product(
    ProductSpec(payload={"name": "Test"}),
    idempotency_key="mock-prod-1",
)

print(product.raw)
```

## Capability Mapping

The mock provider advertises every `Capability` and therefore maps to the entire set of `tigrbl_billing` capabilities when using `capabilities_to_tigrbl`.

## Related Packages

Billing provider packages:

- [swarmauri_billing_adyen](https://pypi.org/project/swarmauri_billing_adyen/)
- [swarmauri_billing_authorize_net](https://pypi.org/project/swarmauri_billing_authorize_net/)
- [swarmauri_billing_braintree](https://pypi.org/project/swarmauri_billing_braintree/)
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

Need additional fixtures? Contributions that expand deterministic behavior are encouraged.


