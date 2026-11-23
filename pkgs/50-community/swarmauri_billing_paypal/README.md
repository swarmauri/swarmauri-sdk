# swarmauri_billing_paypal

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_billing_paypal</strong></p>
<p align="center">PayPal REST backed Swarmauri billing provider for products, plans, orders, captures, refunds, subscriptions, invoices, payouts, disputes, and webhooks.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_billing_paypal/"><img alt="pypi: swarmauri_billing_paypal" src="https://img.shields.io/pypi/v/swarmauri_billing_paypal?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paypal/pyproject.toml"><img alt="Source version: 0.11.0.dev4" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev4&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paypal/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paypal/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paypal/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paypal/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paypal/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_billing_paypal/"><img alt="Monthly PyPI downloads: swarmauri_billing_paypal" src="https://img.shields.io/pypi/dm/swarmauri_billing_paypal?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paypal/README.md"><img alt="README hits: swarmauri_billing_paypal" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_billing_paypal/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paypal/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paypal/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_billing_paypal` provides a PayPal REST backed billing provider for Swarmauri checkout, payment, subscription, invoicing, refund, payout, reporting, dispute, and webhook workflows. It connects Swarmauri billing interfaces to PayPal products, billing plans, Checkout Orders, captures, authorisation voids, refunds, subscriptions, invoices, payouts, customer disputes, webhook signature verification, and webhook event parsing.

### Why This Package

`swarmauri_billing_paypal` lets Swarmauri billing workflows use PayPal REST APIs behind provider-neutral billing interfaces. Application code can create orders, capture payments, refund captures, send invoices, start payouts, verify webhook signatures, list customer disputes, and parse webhook events without hard-coding PayPal REST payloads throughout the codebase.

### When to Use

Choose `swarmauri_billing_paypal` when your integration needs payPal REST backed Swarmauri billing provider for products, plans, orders, captures, refunds, subscriptions, invoices, payouts, disputes, and webhooks. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- PayPal provider class registered as `PayPalBillingProvider`.
- OAuth client credentials authentication for sandbox or production.
- Product and billing-plan creation.
- Checkout Order creation with approval URL extraction.
- Order capture and authorization void support.
- Refund creation and lookup.
- Subscription create/cancel support.
- Invoice create/send/cancel support.
- Payout batch creation.
- Customer dispute listing through PayPal's customer disputes API.
- PayPal webhook signature verification through PayPal's verification endpoint.
- PayPal webhook JSON event parsing.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

`swarmauri_billing_paypal` owns payPal REST backed Swarmauri billing provider for products, plans, orders, captures, refunds, subscriptions, invoices, payouts, disputes, and webhooks. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paypal/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `httpx`. Read the example’s inputs and service requirements before execution.

### Installation

Install with `uv`:

```bash
uv add swarmauri_billing_paypal
```

Install with `pip`:

```bash
pip install swarmauri_billing_paypal
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_billing_paypal
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_billing_paypal
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_billing_paypal
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paypal/docs/readme/quick_start.py).

```python
from swarmauri_billing_paypal import PayPalBillingProvider
from swarmauri_base.billing import CheckoutRequest, PriceSpec, ProductSpec

provider = PayPalBillingProvider(
    api_key="paypal",
    client_id="paypal-client-id",
    client_secret="paypal-client-secret",
)

product = provider.create_product(
    ProductSpec(name="Workspace"),
    idempotency_key="paypal-prod-1",
)
price = provider.create_price(
    product,
    PriceSpec(currency="USD", unit_amount_minor=2500),
    idempotency_key="paypal-price-1",
)
checkout = provider.create_checkout(
    price,
    CheckoutRequest(success_url="https://example.com/return"),
)

print(product.id, price.id, checkout.url)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_billing_paypal` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paypal/docs/readme/usage.py).

```python
from swarmauri_billing_paypal import PayPalBillingProvider
from swarmauri_base.billing import CheckoutRequest, PriceSpec, ProductSpec

provider = PayPalBillingProvider(
    api_key="paypal",
    client_id="paypal-client-id",
    client_secret="paypal-client-secret",
)

product = provider.create_product(
    ProductSpec(name="Workspace"),
    idempotency_key="paypal-prod-1",
)
price = provider.create_price(
    product,
    PriceSpec(currency="USD", unit_amount_minor=2500),
    idempotency_key="paypal-price-1",
)
checkout = provider.create_checkout(
    price,
    CheckoutRequest(success_url="https://example.com/return"),
)

print(product.id, price.id, checkout.url)
```
<!-- readme-standards:end example.usage -->

Create a product, price, and PayPal-style checkout session:


Create and capture a PayPal-style payment:

```python
from swarmauri_billing_paypal import PayPalBillingProvider
from swarmauri_base.billing import PaymentIntentRequest

provider = PayPalBillingProvider(
    api_key="paypal",
    client_id="paypal-client-id",
    client_secret="paypal-client-secret",
)

payment = provider.create_payment_intent(
    PaymentIntentRequest(amount_minor=1500, currency="USD", confirm=True)
)
captured = provider.capture_payment(
    payment.id, idempotency_key="paypal-capture-1"
)

print(payment.status, captured.status)
```

### Configuration

Configure `swarmauri_billing_paypal` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paypal/swarmauri_billing_paypal/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paypal/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_billing_paypal` source raises `RuntimeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_billing_paypal` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `PayPalBillingProvider`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_billing_paypal` is located in `community` and owns payPal REST backed Swarmauri billing provider for products, plans, orders, captures, refunds, subscriptions, invoices, payouts, disputes, and webhooks. Source-declared APIs include `PayPalBillingProvider`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paypal/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_billing_paypal`.

Source-declared exports or types: `PayPalBillingProvider`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paypal/swarmauri_billing_paypal/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.billing_providers` → `PayPalBillingProvider` → `swarmauri_billing_paypal.provider:PayPalBillingProvider`
<!-- readme-standards:end entry-points -->

The package exposes a Swarmauri billing provider entry point:

```toml
[project.entry-points.'swarmauri.billing_providers']
PayPalBillingProvider = "swarmauri_billing_paypal.provider:PayPalBillingProvider"
```

### Injected Dependencies

The direct installation dependencies of `swarmauri_billing_paypal` are `swarmauri-core`, `swarmauri-base`, `httpx`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paypal/swarmauri_billing_paypal/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_billing_paypal` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_billing_paypal`, use the source-declared public interfaces (`PayPalBillingProvider`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_billing_paypal` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paypal/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_billing_paypal`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paypal/swarmauri_billing_paypal/__init__.py). The `swarmauri_billing_paypal` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_billing_paypal` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_billing_paypal` package directory for the maintained example source checks (Python compilation and non-Python file presence). Behavioral tests may live in the repository’s shared suites; the new README syntax test is not presented as runtime coverage for payPal REST backed Swarmauri billing provider for products, plans, orders, captures, refunds, subscriptions, invoices, payouts, disputes, and webhooks.

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_billing_paypal` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paypal/swarmauri_billing_paypal/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Q: Does this package call live PayPal APIs?**

A: Yes. It uses PayPal OAuth client credentials and calls PayPal REST endpoints for products, plans, orders, captures, voids, refunds, subscriptions, invoices, and payouts.

**Q: Which Swarmauri billing capabilities does it cover?**

A: It covers products, plan-like prices, hosted checkout orders, online orders, capture, authorization void, subscriptions, invoicing, refunds, payouts, customer dispute listing, PayPal webhook signature verification, and webhook event parsing. Customer, payment-method, balance, and report helpers remain compatibility placeholders where PayPal does not expose the same direct Swarmauri object shape.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_billing_paypal`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paypal/swarmauri_billing_paypal/__init__.py) for the exact types and signatures involved.

### When

**Q: When should I use this package?**

A: Use it for local billing workflows, provider strategy tests, documentation examples, and contract tests that need PayPal-style behavior through Swarmauri billing abstractions.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paypal/swarmauri_billing_paypal/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paypal/pyproject.toml) provide the supporting context for `swarmauri_billing_paypal`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

Billing provider packages:

- [swarmauri_billing_adyen](https://pypi.org/project/swarmauri_billing_adyen/)
- [swarmauri_billing_authorize_net](https://pypi.org/project/swarmauri_billing_authorize_net/)
- [swarmauri_billing_braintree](https://pypi.org/project/swarmauri_billing_braintree/)
- [swarmauri_billing_mock](https://pypi.org/project/swarmauri_billing_mock/)
- [swarmauri_billing_paystack](https://pypi.org/project/swarmauri_billing_paystack/)
- [swarmauri_billing_razorpay](https://pypi.org/project/swarmauri_billing_razorpay/)
- [swarmauri_billing_square](https://pypi.org/project/swarmauri_billing_square/)
- [swarmauri_billing_stripe](https://pypi.org/project/swarmauri_billing_stripe/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines billing capabilities and interfaces.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides billing specs, refs, mixins, and `BillingProviderBase`.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_billing_paypal](https://pypi.org/project/swarmauri_billing_paypal/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you connect this provider to live PayPal APIs, preserve deterministic tests, document required credentials and webhook behavior, and add coverage for each supported billing capability.

### Development Setup

Work from the `pkgs/50-community/swarmauri_billing_paypal` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Important Scope Notes**

This package uses live PayPal REST API calls for products, plans, orders, captures, voids, refunds, subscriptions, invoices, payouts, customer disputes, webhook signature verification, and webhook parsing. Production use requires PayPal REST app credentials, correct sandbox or production environment selection, a configured PayPal webhook ID for signature verification, and account permissions for each enabled PayPal product.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_billing_paypal` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paypal/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_billing_paypal` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_billing_paypal` source version is `0.11.0.dev4`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paypal/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paypal/NOTICE) for attribution.
<!-- readme-standards:end notices -->
