![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_billing_authorize_net/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_billing_authorize_net" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_authorize_net/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_billing_authorize_net.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_authorize_net/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_billing_authorize_net" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_authorize_net/">
        <img src="https://img.shields.io/pypi/l/swarmauri_billing_authorize_net" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_billing_authorize_net/">
        <img src="https://img.shields.io/pypi/v/swarmauri_billing_authorize_net?label=swarmauri_billing_authorize_net&color=green" alt="PyPI - swarmauri_billing_authorize_net"/></a>
</p>

---

# Swarmauri Billing Authorize.Net

The **Swarmauri Billing Authorize.Net** package exposes a payments-first provider that mirrors the Authorize.Net API surface inside the Swarmauri SDK. Use it to validate card-not-present flows, refunds, and customer profile operations before you integrate the official SDK.

## Features

- ✅ Focuses on the Authorize.Net core: transactions, refunds, customer profiles, and reporting.
- ✅ Emits deterministic payloads keyed by the provider namespace for straightforward assertions.
- ✅ Provides webhook parsing hooks for signature verification and fraud review flows.
- ✅ Designed as a drop-in replacement that can later call the Authorize.Net XML/JSON APIs.

## Installation

Install from PyPI using either `pip` or `uv`:

```bash
pip install swarmauri_billing_authorize_net
```

```bash
uv add swarmauri_billing_authorize_net
```

## Usage

```python
from swarmauri_billing_authorize_net import AuthorizeNetBillingProvider
from swarmauri_base.billing import PaymentIntentRequest, RefundRequest

provider = AuthorizeNetBillingProvider(api_key="test-key")

payment_intent = provider.create_payment_intent(
    PaymentIntentRequest(payload={"amount_minor": 4200, "currency": "USD", "confirm": True}),
)
refund = provider.create_refund(
    payment_intent,
    RefundRequest(payload={"amount_minor": 4200}),
)

print(payment_intent.status, refund["status"])
```

## Capability Mapping

Capability metadata maps to `tigrbl_billing` identifiers via `capabilities_to_tigrbl`. That ensures your feature toggles and documentation stay aligned when swapping between this stub and a real Authorize.Net integration.

## Contributing

If you connect the stub to the live Authorize.Net API, please share integration notes, test coverage, and examples in the README to help the community adopt the changes.
