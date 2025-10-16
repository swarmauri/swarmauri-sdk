# Swarmauri Billing Square

![Swarmauri Branding](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

![Downloads](https://img.shields.io/badge/downloads-community-blue)
![Hits](https://img.shields.io/badge/hits-active-green)
![Python Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)
![License](https://img.shields.io/badge/license-Apache%202.0-orange)
![Release](https://img.shields.io/badge/release-0.1.0.dev0-informational)

`swarmauri_billing_square` delivers a community maintained Square billing provider built from the shared Swarmauri billing abstractions.

## Features

- ✅ Minimal `_dispatch` stub for rapid prototyping without Square credentials.
- ✅ Leverages the shared mixins for catalogue, payment, and subscription workflows.
- ✅ Emits deterministic payloads to simplify testing.

## Installation

### Using `uv`

```bash
uv add swarmauri_billing_square
```

### Using `pip`

```bash
pip install swarmauri_billing_square
```

## Usage

```python
from swarmauri_billing_square import SquareBillingProvider

provider = SquareBillingProvider(location_id="test-location")
product = provider.create_product({"name": "Example"}, idempotency_key="prod-1")
price = provider.create_price(product, {"currency": "usd", "unit_amount_minor": 1500}, idempotency_key="price-1")
```

Community packages are provided as-is and are great starting points for bespoke integrations.
