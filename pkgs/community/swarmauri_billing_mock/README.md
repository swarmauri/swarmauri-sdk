# Swarmauri Billing Mock

![Swarmauri Branding](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

![Downloads](https://img.shields.io/badge/downloads-community-blue)
![Hits](https://img.shields.io/badge/hits-active-green)
![Python Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)
![License](https://img.shields.io/badge/license-Apache%202.0-orange)
![Release](https://img.shields.io/badge/release-0.1.0.dev0-informational)

`swarmauri_billing_mock` supplies a deterministic mock billing provider ideal for tests and rapid prototyping.

## Features

- ✅ Fully deterministic responses for repeatable scenarios.
- ✅ Covers the entire capability surface exposed by the shared mixins.
- ✅ Perfect for verifying orchestration logic without external dependencies.

## Installation

### Using `uv`

```bash
uv add swarmauri_billing_mock
```

### Using `pip`

```bash
pip install swarmauri_billing_mock
```

## Usage

```python
from swarmauri_billing_mock import MockBillingProvider

provider = MockBillingProvider()
refund = provider.create_refund({"id": "pay_1"}, {"amount_minor": 500}, idempotency_key="refund-1")
```

Community packages provide reference implementations that you can extend to meet your needs.
