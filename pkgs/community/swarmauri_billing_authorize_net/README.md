![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_billing_authorize_net/">
        <img src="https://static.pepy.tech/badge/swarmauri_billing_authorize_net/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_authorize_net/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_authorize_net.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_authorize_net/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_authorize_net/">
        <img src="https://img.shields.io/pypi/l/swarmauri_billing_authorize_net" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_authorize_net/">
        <img src="https://img.shields.io/pypi/v/swarmauri_billing_authorize_net?label=swarmauri_billing_authorize_net&color=green" alt="PyPI - swarmauri_billing_authorize_net"/></a>
</p>

# Swarmauri Billing Authorize.Net

`swarmauri_billing_authorize_net` provides an Authorize.Net JSON API backed billing provider for Swarmauri payment workflows. It connects Swarmauri billing interfaces to Authorize.Net transaction creation, prior-auth capture, voids, refunds, customer profiles, transaction details, webhook parsing, and HMAC-SHA512 webhook validation.

## Why Swarmauri Billing Authorize.Net?

`swarmauri_billing_authorize_net` gives billing integrators an Authorize.Net payment provider behind Swarmauri billing interfaces. Applications can authorize, capture, void, refund, create customer profiles, and validate webhook notifications without hard-coding Authorize.Net request payloads throughout the codebase.

## FAQ

### Q: Does this package call Authorize.Net APIs?

A: Yes for transaction and customer-profile workflows. It posts JSON requests to Authorize.Net sandbox or production endpoints with merchant authentication.

### Q: Which billing areas does it cover?

A: It covers online payments, prior-auth capture, voids, refunds, customer profile create/get, transaction detail lookup for refunds, webhook parsing, and HMAC-SHA512 signature validation. Some payment-method and reporting helpers remain compatibility placeholders.

### Q: What credentials are required?

A: Provide `login_id` for the API Login ID and `api_key` for the transaction key. Use `environment="sandbox"` for test accounts and `environment="production"` for live accounts.

## Features

- Authorize.Net provider class registered as `AuthorizeNetBillingProvider`.
- JSON API transaction creation for `authCaptureTransaction` and `authOnlyTransaction`.
- Prior authorization capture and void transaction support.
- Refund transaction creation and transaction detail lookup.
- Customer profile creation and retrieval.
- HMAC-SHA512 webhook signature validation using `X-ANET-Signature`.
- Webhook JSON event parsing.
- Uses Swarmauri billing specs and refs from `swarmauri_base.billing`.
- Advertises an explicit subset of `swarmauri_core.billing.Capability`.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

## Installation

Install with `uv`:

```bash
uv add swarmauri_billing_authorize_net
```

Install with `pip`:

```bash
pip install swarmauri_billing_authorize_net
```

## Usage

Create and refund an Authorize.Net-style payment:

```python
from swarmauri_billing_authorize_net import AuthorizeNetBillingProvider
from swarmauri_base.billing import PaymentIntentRequest, RefundRequest

provider = AuthorizeNetBillingProvider(
    api_key="authorize-net-transaction-key",
    login_id="authorize-net-login-id",
)

payment = provider.create_payment_intent(
    PaymentIntentRequest(
        amount_minor=4200,
        currency="USD",
        confirm=True,
        metadata={
            "opaque_data": {
                "dataDescriptor": "COMMON.ACCEPT.INAPP.PAYMENT",
                "dataValue": "opaque-payment-token",
            }
        },
    )
)
refund = provider.create_refund(
    payment,
    RefundRequest(amount_minor=4200),
    idempotency_key="refund-anet-1",
)

print(payment.status, refund["id"])
```

List payment methods for a customer reference:

```python
from swarmauri_base.billing import CustomerSpec, PaymentMethodSpec
from swarmauri_billing_authorize_net import AuthorizeNetBillingProvider

provider = AuthorizeNetBillingProvider(
    api_key="authorize-net-transaction-key",
    login_id="authorize-net-login-id",
)
customer = provider.create_customer(
    CustomerSpec(payload={"email": "buyer@example.com"}),
    idempotency_key="customer-anet-1",
)
payment_method = provider.create_payment_method(
    PaymentMethodSpec(payload={"type": "credit_card"}),
    idempotency_key="pm-anet-1",
)

provider.attach_payment_method_to_customer(customer, payment_method)
methods = provider.list_payment_methods(customer, type="credit_card")

print(customer.id, len(methods))
```

## Important Scope Notes

This package uses live Authorize.Net JSON API calls for transaction and customer-profile workflows. Payment data should be supplied through Accept.js opaque data or other compliant tokenized payloads. Do not place raw card data in application code unless your environment is explicitly PCI scoped.

## Entry Point

The package exposes a Swarmauri billing provider entry point:

```toml
[project.entry-points.'swarmauri.billing_providers']
AuthorizeNetBillingProvider = "swarmauri_billing_authorize_net.provider:AuthorizeNetBillingProvider"
```

## Related Packages

Billing provider packages:

- [swarmauri_billing_adyen](https://pypi.org/project/swarmauri_billing_adyen/)
- [swarmauri_billing_braintree](https://pypi.org/project/swarmauri_billing_braintree/)
- [swarmauri_billing_mock](https://pypi.org/project/swarmauri_billing_mock/)
- [swarmauri_billing_paypal](https://pypi.org/project/swarmauri_billing_paypal/)
- [swarmauri_billing_paystack](https://pypi.org/project/swarmauri_billing_paystack/)
- [swarmauri_billing_razorpay](https://pypi.org/project/swarmauri_billing_razorpay/)
- [swarmauri_billing_square](https://pypi.org/project/swarmauri_billing_square/)
- [swarmauri_billing_stripe](https://pypi.org/project/swarmauri_billing_stripe/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines billing capabilities and provider interfaces.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides billing specs, refs, mixins, and `BillingProviderBase`.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

## License

Apache-2.0

## Contributing

If you connect this provider to live Authorize.Net APIs, keep the stub behavior separately testable, document required credentials and webhook behavior, and add tests for every supported billing capability.
