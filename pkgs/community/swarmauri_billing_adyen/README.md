# swarmauri_billing_adyen

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_billing_adyen</strong></p>
<p align="center">Adyen Checkout API backed Swarmauri billing provider for hosted sessions, payments, captures, cancels, refunds, and webhook validation.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_billing_adyen/"><img alt="pypi: swarmauri_billing_adyen" src="https://img.shields.io/pypi/v/swarmauri_billing_adyen"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_adyen/pyproject.toml"><img alt="Source version: 0.11.0.dev4" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev4&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_adyen/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_adyen/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_adyen/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_adyen/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_adyen/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_billing_adyen/"><img alt="Monthly PyPI downloads: swarmauri_billing_adyen" src="https://img.shields.io/pypi/dm/swarmauri_billing_adyen"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_adyen/README.md"><img alt="README hits: swarmauri_billing_adyen" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/community/swarmauri_billing_adyen/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_adyen/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_adyen/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_billing_adyen` provides an Adyen Checkout API backed billing provider for the Swarmauri SDK. It connects Swarmauri billing interfaces to Adyen hosted sessions, `/payments`, captures, cancels, refunds, notification parsing, and HMAC webhook validation.

### Why This Package

`swarmauri_billing_adyen` gives billing integrators an Adyen payment provider behind Swarmauri billing interfaces. Applications can create Adyen Checkout Sessions, submit payment requests, capture or cancel authorized payments, refund payments, and validate Adyen notifications without coupling the rest of the codebase to Adyen request payloads.

### When to Use

Choose `swarmauri_billing_adyen` when your integration needs adyen Checkout API backed Swarmauri billing provider for hosted sessions, payments, captures, cancels, refunds, and webhook validation. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Adyen provider class registered as `AdyenBillingProvider`.
- Hosted Checkout Session creation through Adyen `/sessions`.
- Payment submission through Adyen `/payments`.
- Capture, cancel, and refund calls through Adyen payment modification endpoints.
- Adyen notification parsing for `notificationItems` payloads.
- HMAC webhook verification using Adyen notification signing fields.
- Compatibility placeholders for Swarmauri billing mixins that do not have direct Adyen Checkout API equivalents.
- Supports serialization through `swarmauri_base.billing.BillingProviderBase`.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

`swarmauri_billing_adyen` owns adyen Checkout API backed Swarmauri billing provider for hosted sessions, payments, captures, cancels, refunds, and webhook validation. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_adyen/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `httpx`. Read the example’s inputs and service requirements before execution.

### Installation

Install with `uv`:

```bash
uv add swarmauri_billing_adyen
```

Install with `pip`:

```bash
pip install swarmauri_billing_adyen
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_billing_adyen
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_billing_adyen
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_billing_adyen
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_adyen/docs/readme/quick_start.py).

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
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_billing_adyen` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_adyen/docs/readme/usage.py).

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
<!-- readme-standards:end example.usage -->

Create a product, price, and hosted checkout session:


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

### Configuration

Configure `swarmauri_billing_adyen` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_adyen/swarmauri_billing_adyen/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_adyen/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_billing_adyen` source raises `RuntimeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_billing_adyen` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `AdyenBillingProvider`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_billing_adyen` is located in `community` and owns adyen Checkout API backed Swarmauri billing provider for hosted sessions, payments, captures, cancels, refunds, and webhook validation. Source-declared APIs include `AdyenBillingProvider`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_adyen/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_billing_adyen`.

Source-declared exports or types: `AdyenBillingProvider`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_adyen/swarmauri_billing_adyen/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.billing_providers` → `AdyenBillingProvider` → `swarmauri_billing_adyen.provider:AdyenBillingProvider`
<!-- readme-standards:end entry-points -->

The package exposes a Swarmauri billing provider entry point:

```toml
[project.entry-points.'swarmauri.billing_providers']
AdyenBillingProvider = "swarmauri_billing_adyen.provider:AdyenBillingProvider"
```

### Injected Dependencies

The direct installation dependencies of `swarmauri_billing_adyen` are `swarmauri-core`, `swarmauri-base`, `httpx`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_adyen/swarmauri_billing_adyen/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_billing_adyen` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_billing_adyen`, use the source-declared public interfaces (`AdyenBillingProvider`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_billing_adyen` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_adyen/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_billing_adyen`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_adyen/swarmauri_billing_adyen/__init__.py). The `swarmauri_billing_adyen` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_billing_adyen` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_billing_adyen` package directory for the maintained example source checks (Python compilation and non-Python file presence). Behavioral tests may live in the repository’s shared suites; the new README syntax test is not presented as runtime coverage for adyen Checkout API backed Swarmauri billing provider for hosted sessions, payments, captures, cancels, refunds, and webhook validation.

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_billing_adyen` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_adyen/swarmauri_billing_adyen/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Q: Does this package call Adyen APIs?**

A: Yes for payment-oriented flows. Checkout sessions, payments, captures, cancels, and refunds call Adyen Checkout API endpoints using `X-API-Key` authentication. Some non-payment Swarmauri mixins remain local placeholders where Adyen has no direct one-to-one Checkout API object.

**Q: Which capabilities does it advertise?**

A: The runtime-backed paths cover hosted checkout, online payments, capture, cancel, refunds, notification parsing, and webhook HMAC validation. The package still exposes the broader Swarmauri billing surface for compatibility.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_billing_adyen`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_adyen/swarmauri_billing_adyen/__init__.py) for the exact types and signatures involved.

### When

**Q: When should I use this package?**

A: Use it when a Swarmauri application needs Adyen Checkout payment flows while preserving provider-neutral billing interfaces.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_adyen/swarmauri_billing_adyen/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_adyen/pyproject.toml) provide the supporting context for `swarmauri_billing_adyen`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

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

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_billing_adyen](https://pypi.org/project/swarmauri_billing_adyen/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Community contributions are welcome. Keep behavior deterministic unless adding an explicitly documented live-client mode, preserve the Swarmauri billing interfaces, and add tests for new billing capability methods.

### Development Setup

Work from the `pkgs/community/swarmauri_billing_adyen` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Important Scope Notes**

This package uses live Adyen Checkout API calls for payment-oriented workflows. Product, price, subscription, invoice, customer, payout, report, coupon, and promotion methods remain compatibility placeholders where Adyen Checkout does not expose a direct object matching the Swarmauri billing interface. Production use requires a valid `merchant_account`, an Adyen API key, correct test/live environment selection, and a live URL prefix for production.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_billing_adyen` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_adyen/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_billing_adyen` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_billing_adyen` source version is `0.11.0.dev4`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_adyen/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_billing_adyen/NOTICE) for attribution.
<!-- readme-standards:end notices -->
