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

`swarmauri_billing_adyen` provides an Adyen Checkout API backed billing provider for the Swarmauri SDK. It connects Swarmauri billing interfaces to Adyen hosted sessions, `/payments`, captures, cancels, refunds, notification parsing, and HMAC webhook validation.

## Why Swarmauri Billing Adyen?

`swarmauri_billing_adyen` gives billing integrators an Adyen payment provider behind Swarmauri billing interfaces. Applications can create Adyen Checkout Sessions, submit payment requests, capture or cancel authorized payments, refund payments, and validate Adyen notifications without coupling the rest of the codebase to Adyen request payloads.

## FAQ

### Q: Does this package call Adyen APIs?

A: Yes for payment-oriented flows. Checkout sessions, payments, captures, cancels, and refunds call Adyen Checkout API endpoints using `X-API-Key` authentication. Some non-payment Swarmauri mixins remain local placeholders where Adyen has no direct one-to-one Checkout API object.

### Q: Which capabilities does it advertise?

A: The runtime-backed paths cover hosted checkout, online payments, capture, cancel, refunds, notification parsing, and webhook HMAC validation. The package still exposes the broader Swarmauri billing surface for compatibility.

### Q: When should I use this package?

A: Use it when a Swarmauri application needs Adyen Checkout payment flows while preserving provider-neutral billing interfaces.

## Features

- Adyen provider class registered as `AdyenBillingProvider`.
- Hosted Checkout Session creation through Adyen `/sessions`.
- Payment submission through Adyen `/payments`.
- Capture, cancel, and refund calls through Adyen payment modification endpoints.
- Adyen notification parsing for `notificationItems` payloads.
- HMAC webhook verification using Adyen notification signing fields.
- Compatibility placeholders for Swarmauri billing mixins that do not have direct Adyen Checkout API equivalents.
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

provider = AdyenBillingProvider(
    api_key="adyen-test-key",
    merchant_account="YourMerchantAccount",
)

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

This package uses live Adyen Checkout API calls for payment-oriented workflows. Product, price, subscription, invoice, customer, payout, report, coupon, and promotion methods remain compatibility placeholders where Adyen Checkout does not expose a direct object matching the Swarmauri billing interface. Production use requires a valid `merchant_account`, an Adyen API key, correct test/live environment selection, and a live URL prefix for production.

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
