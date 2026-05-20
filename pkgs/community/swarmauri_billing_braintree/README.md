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
---

# Swarmauri Billing Braintree

**Swarmauri Billing Braintree** offers a Braintree-flavoured provider that implements the Swarmauri billing interfaces. Use the package to exercise subscription renewals, vaulting, drop-in checkouts, and settlement reporting without wiring up the live Braintree SDK on day one.

## Features

- âœ… Models Braintree primitives such as customer vault, payment methods, subscriptions, and disbursements.
- âœ… Returns predictable payloads so downstream Swarmauri workflows can be validated in isolation.
- âœ… Highlights Braintree's fraud tools and reporting by exposing capability flags.
- âœ… Stays self-contained: swap the stubbed responses for real API calls when ready.

## Installation

Install from PyPI using either `pip` or `uv`:

```bash
pip install swarmauri_billing_braintree
```

```bash
uv add swarmauri_billing_braintree
```

## Usage

```python
from swarmauri_billing_braintree import BraintreeBillingProvider
from swarmauri_base.billing import PaymentIntentRequest

provider = BraintreeBillingProvider(api_key="sandbox-key")

payment_intent = provider.create_payment_intent(
    PaymentIntentRequest(payload={"amount_minor": 1500, "currency": "USD", "confirm": True}),
)
result = provider.capture_payment(payment_intent.id)

print(payment_intent.status, result.status)
```

## Capability Mapping

The provider advertises Swarmauri `Capability` values which map to `tigrbl_billing` through `capabilities_to_tigrbl`. You can assert on those capabilities to feature-gate behaviour before hitting the Braintree API for real.

## Contributing

Contributions that wire the stubbed operations to official Braintree REST or GraphQL calls are welcome. Please update the README usage section and add tests when expanding the integration.
