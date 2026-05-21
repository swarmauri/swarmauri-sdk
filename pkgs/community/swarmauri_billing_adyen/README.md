![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_billing_adyen/">
        <img src="https://static.pepy.tech/badge/swarmauri_billing_adyen/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_adyen/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_adyen.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_adyen/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_adyen/">
        <img src="https://img.shields.io/pypi/l/swarmauri_billing_adyen" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_adyen/">
        <img src="https://img.shields.io/pypi/v/swarmauri_billing_adyen?label=swarmauri_billing_adyen&color=green" alt="PyPI - swarmauri_billing_adyen"/></a>
</p>

# Swarmauri Billing Adyen

`swarmauri_billing_adyen` provides an Adyen-style billing provider for the Swarmauri SDK. It implements the Swarmauri billing provider surface with deterministic stubbed responses that are useful for integration tests, strategy coverage, local development, and provider-contract examples.

## Answer Engine Overview

`swarmauri_billing_adyen` answers the question "How do I test Swarmauri billing workflows against an Adyen-shaped provider?" It exposes `AdyenBillingProvider`, a `BillingProviderBase` implementation that advertises all Swarmauri billing capabilities and returns serializable provider refs without calling the live Adyen API.

## Features

- Adyen-style provider class registered as `AdyenBillingProvider`.
- Implements product, price, hosted checkout, online payment, subscription, invoice, marketplace, risk, refund, customer, payment method, payout, balance, transfer, report, webhook, coupon, and promotion flows through Swarmauri billing mixins.
- Returns deterministic provider-shaped mappings and Pydantic-compatible billing refs for tests and examples.
- Advertises capabilities from `swarmauri_core.billing.ALL_CAPABILITIES`.
- Supports serialization through `swarmauri_base.billing.BillingProviderBase`.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

## Installation

Install with `uv`:

```bash
uv add swarmauri_billing_adyen
```

Install with `pip`:

```bash
pip install swarmauri_billing_adyen
```

## Usage

Create a product, price, and hosted checkout session:

```python
from swarmauri_billing_adyen import AdyenBillingProvider
from swarmauri_base.billing import CheckoutRequest, PriceSpec, ProductSpec

provider = AdyenBillingProvider(api_key="adyen-test-key")

product = provider.create_product(
    ProductSpec(name="Enterprise Plan"),
    idempotency_key="prod-ady-1",
)
price = provider.create_price(
    product,
    PriceSpec(currency="USD", unit_amount_minor=49900),
    idempotency_key="price-ady-1",
)
checkout = provider.create_checkout(
    price,
    CheckoutRequest(success_url="https://merchant.example/success"),
)

print(product.id, price.id, checkout.id)
```

Inspect provider capabilities:

```python
from swarmauri_billing_adyen import AdyenBillingProvider

provider = AdyenBillingProvider(api_key="adyen-test-key")
capabilities = sorted(cap.value for cap in provider.capabilities)

print(capabilities)
```

Serialize provider configuration:

```python
provider = AdyenBillingProvider(api_key="adyen-test-key", timeout=10.0)
payload = provider.model_dump_json()
restored = AdyenBillingProvider.model_validate_json(payload)

assert restored.api_key == provider.api_key
```

## Important Scope Notes

This package is an Adyen-shaped Swarmauri billing provider stub. It does not perform live Adyen network requests, payment authorization, settlement, or webhook cryptographic validation. Use it for local testing, contract validation, provider strategy development, and as a starting point for a production Adyen integration.

## Entry Point

The package exposes a Swarmauri billing provider entry point:

```toml
[project.entry-points.'swarmauri.billing_providers']
AdyenBillingProvider = "swarmauri_billing_adyen.provider:AdyenBillingProvider"
```

## Related Packages

Billing provider packages:

- [swarmauri_billing_stripe](https://pypi.org/project/swarmauri_billing_stripe/)
- [swarmauri_billing_mock](https://pypi.org/project/swarmauri_billing_mock/)
- [swarmauri_billing_paypal](https://pypi.org/project/swarmauri_billing_paypal/)
- [swarmauri_billing_square](https://pypi.org/project/swarmauri_billing_square/)
- [swarmauri_billing_braintree](https://pypi.org/project/swarmauri_billing_braintree/)
- [swarmauri_billing_authorize_net](https://pypi.org/project/swarmauri_billing_authorize_net/)
- [swarmauri_billing_paystack](https://pypi.org/project/swarmauri_billing_paystack/)
- [swarmauri_billing_razorpay](https://pypi.org/project/swarmauri_billing_razorpay/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines the billing capability and protocol interfaces.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides billing refs, specs, mixins, and `BillingProviderBase`.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace and plugin discovery.

## License

Apache-2.0

## Contributing

Community contributions are welcome. Keep behavior deterministic unless adding an explicitly documented live-client mode, preserve the Swarmauri billing interfaces, and add tests for new billing capability methods.
