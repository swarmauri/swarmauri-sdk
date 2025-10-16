# Swarmauri Billing Stripe

![Swarmauri Branding](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

![Downloads](https://img.shields.io/badge/downloads-stable-blue)
![Hits](https://img.shields.io/badge/hits-active-green)
![Python Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)
![License](https://img.shields.io/badge/license-Apache%202.0-orange)
![Release](https://img.shields.io/badge/release-0.1.0.dev0-informational)

`swarmauri_billing_stripe` provides a standards-track billing provider implementation for Stripe built on top of the Swarmauri billing abstractions.

## Features

- ✅ Provider implementation built from the shared Swarmauri billing mixins.
- ✅ Simple `_dispatch` stub that demonstrates the request flow without live network dependencies.
- ✅ Full compatibility with the shared `Capability` and `Operation` metadata for introspection.

## Installation

### Using `uv`

```bash
uv add swarmauri_billing_stripe
```

### Using `pip`

```bash
pip install swarmauri_billing_stripe
```

## Usage

```python
from swarmauri_billing_stripe import StripeBillingProvider

provider = StripeBillingProvider(api_key="sk_test")
product = provider.create_product({"name": "Example"}, idempotency_key="prod-1")
price = provider.create_price(product, {"currency": "usd", "unit_amount_minor": 1000}, idempotency_key="price-1")
checkout = provider.create_checkout(price, {"success_url": "https://example.com", "cancel_url": "https://example.com/cancel"})
```

This package adheres to the Swarmauri standards programme and is maintained by the Swarmauri team.
