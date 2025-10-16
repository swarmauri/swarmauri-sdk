# Swarmauri Billing Paystack

![Swarmauri Branding](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

![Downloads](https://img.shields.io/badge/downloads-community-blue)
![Hits](https://img.shields.io/badge/hits-active-green)
![Python Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)
![License](https://img.shields.io/badge/license-Apache%202.0-orange)
![Release](https://img.shields.io/badge/release-0.1.0.dev0-informational)

`swarmauri_billing_paystack` offers a Paystack billing provider stub that aligns with the shared billing contracts.

## Features

- ✅ Demonstrates Paystack-style payloads without real network calls.
- ✅ Implements the common Swarmauri billing mixins for consistency.
- ✅ Deterministic responses for reliable tests and documentation.

## Installation

### Using `uv`

```bash
uv add swarmauri_billing_paystack
```

### Using `pip`

```bash
pip install swarmauri_billing_paystack
```

## Usage

```python
from swarmauri_billing_paystack import PaystackBillingProvider

provider = PaystackBillingProvider(secret_key="sk_test")
checkout = provider.create_checkout({"id": "price"}, {"success_url": "https://example.com", "cancel_url": "https://example.com/cancel"})
```

Community packages highlight integration best practices for downstream customisation.
