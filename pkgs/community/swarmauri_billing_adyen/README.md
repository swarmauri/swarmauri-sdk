# Swarmauri Billing Adyen

![Swarmauri Branding](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

![Downloads](https://img.shields.io/badge/downloads-community-blue)
![Hits](https://img.shields.io/badge/hits-active-green)
![Python Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)
![License](https://img.shields.io/badge/license-Apache%202.0-orange)
![Release](https://img.shields.io/badge/release-0.1.0.dev0-informational)

`swarmauri_billing_adyen` supplies a community stub for the Adyen billing provider built from the shared billing abstractions.

## Features

- ✅ Deterministic `_dispatch` stub for documentation and demos.
- ✅ Uses the shared mixins providing a familiar Swarmauri billing API.
- ✅ Simple payload echoes make experimentation straightforward.

## Installation

### Using `uv`

```bash
uv add swarmauri_billing_adyen
```

### Using `pip`

```bash
pip install swarmauri_billing_adyen
```

## Usage

```python
from swarmauri_billing_adyen import AdyenBillingProvider

provider = AdyenBillingProvider(api_key="test")
payment = provider.create_payment_intent({"amount_minor": 5000, "currency": "eur"})
```

Community packages are a launchpad for building fully featured integrations.
