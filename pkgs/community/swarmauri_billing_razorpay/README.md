# Swarmauri Billing Razorpay

![Swarmauri Branding](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

![Downloads](https://img.shields.io/badge/downloads-community-blue)
![Hits](https://img.shields.io/badge/hits-active-green)
![Python Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)
![License](https://img.shields.io/badge/license-Apache%202.0-orange)
![Release](https://img.shields.io/badge/release-0.1.0.dev0-informational)

`swarmauri_billing_razorpay` publishes a Razorpay billing provider stub aligned with the Swarmauri billing contracts.

## Features

- ✅ Stubbed `_dispatch` layer mirroring Razorpay workflow expectations.
- ✅ Shares the Swarmauri billing mixins to provide a consistent API surface.
- ✅ Deterministic payloads ideal for tests and documentation examples.

## Installation

### Using `uv`

```bash
uv add swarmauri_billing_razorpay
```

### Using `pip`

```bash
pip install swarmauri_billing_razorpay
```

## Usage

```python
from swarmauri_billing_razorpay import RazorpayBillingProvider

provider = RazorpayBillingProvider(key_id="test", key_secret="secret")
subscription = provider.create_subscription({"customer_id": "cust_1", "items": []}, idempotency_key="sub-1")
```

Community packages showcase implementation patterns and can be extended for production deployments.
