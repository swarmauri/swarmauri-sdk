# swarmauri_billing_braintree

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_billing_braintree</strong></p>
<p align="center">Braintree SDK backed Swarmauri billing provider for transactions, settlement, voids, refunds, subscriptions, customers, payment methods, disputes, and webhooks.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_billing_braintree/"><img alt="pypi: swarmauri_billing_braintree" src="https://img.shields.io/pypi/v/swarmauri_billing_braintree"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_braintree/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_braintree/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_braintree/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_braintree/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_braintree/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_braintree/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_billing_braintree/"><img alt="Monthly PyPI downloads: swarmauri_billing_braintree" src="https://img.shields.io/pypi/dm/swarmauri_billing_braintree"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_braintree/README.md"><img alt="README hits: swarmauri_billing_braintree" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_billing_braintree/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_braintree/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_braintree/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_billing_braintree` provides a Braintree SDK backed billing provider for Swarmauri checkout, payment, subscription, refund, customer-vault, reporting, risk, and webhook workflows. It connects Swarmauri billing interfaces to Braintree transactions, settlement submission, voids, refunds, customers, payment methods, subscriptions, disputes, and webhook notifications.

### Why This Package

`swarmauri_billing_braintree` gives billing integrators Braintree payment runtime behavior behind Swarmauri billing interfaces. Applications can create transactions, submit authorized payments for settlement, void transactions, refund payments, manage customer vault records, create subscriptions, and parse Braintree webhooks without hard-coding Braintree SDK calls throughout the codebase.

### When to Use

Choose `swarmauri_billing_braintree` when your integration needs braintree SDK backed Swarmauri billing provider for transactions, settlement, voids, refunds, subscriptions, customers, payment methods, disputes, and webhooks. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Braintree provider class registered as `BraintreeBillingProvider`.
- Transaction sale, submit-for-settlement, void, and refund support.
- Customer creation and lookup through the Braintree customer vault.
- Payment method create/delete support.
- Subscription create/cancel support.
- Dispute search support.
- Webhook parsing and signature validation through Braintree SDK helpers.
- Compatibility placeholders for product, price, hosted-checkout, and report methods that do not map directly to Braintree SDK resources.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

`swarmauri_billing_braintree` owns braintree SDK backed Swarmauri billing provider for transactions, settlement, voids, refunds, subscriptions, customers, payment methods, disputes, and webhooks. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_braintree/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `braintree`. Read the example’s inputs and service requirements before execution.

### Installation

Install with `uv`:

```bash
uv add swarmauri_billing_braintree
```

Install with `pip`:

```bash
pip install swarmauri_billing_braintree
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_billing_braintree
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_billing_braintree
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_billing_braintree
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_braintree/docs/readme/quick_start.py).

```python
from swarmauri_billing_braintree import BraintreeBillingProvider
from swarmauri_base.billing import PaymentIntentRequest

provider = BraintreeBillingProvider(
    api_key="braintree",
    merchant_id="merchant-id",
    public_key="public-key",
    private_key="private-key",
)

payment = provider.create_payment_intent(
    PaymentIntentRequest(
        amount_minor=1500,
        currency="USD",
        confirm=True,
    )
)
captured = provider.capture_payment(payment.id, idempotency_key="capture-bt-1")

print(payment.status, captured.status)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_billing_braintree` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_braintree/docs/readme/usage.py).

```python
from swarmauri_billing_braintree import BraintreeBillingProvider
from swarmauri_base.billing import PaymentIntentRequest

provider = BraintreeBillingProvider(
    api_key="braintree",
    merchant_id="merchant-id",
    public_key="public-key",
    private_key="private-key",
)

payment = provider.create_payment_intent(
    PaymentIntentRequest(
        amount_minor=1500,
        currency="USD",
        confirm=True,
    )
)
captured = provider.capture_payment(payment.id, idempotency_key="capture-bt-1")

print(payment.status, captured.status)
```
<!-- readme-standards:end example.usage -->

Authorize and capture a Braintree-style payment:


Create a plan, price, and checkout session:

```python
from swarmauri_billing_braintree import BraintreeBillingProvider
from swarmauri_base.billing import CheckoutRequest, PriceSpec, ProductSpec

provider = BraintreeBillingProvider(
    api_key="braintree",
    merchant_id="merchant-id",
    public_key="public-key",
    private_key="private-key",
)

plan = provider.create_product(
    ProductSpec(name="SaaS Plan"),
    idempotency_key="plan-bt-1",
)
price = provider.create_price(
    plan,
    PriceSpec(currency="USD", unit_amount_minor=2900),
    idempotency_key="price-bt-1",
)
checkout = provider.create_checkout(price, CheckoutRequest(quantity=1))

print(checkout.url)
```

### Configuration

Configure `swarmauri_billing_braintree` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_braintree/swarmauri_billing_braintree/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_braintree/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_billing_braintree` source raises `RuntimeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_billing_braintree` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `BraintreeBillingProvider`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_billing_braintree` is located in `community` and owns braintree SDK backed Swarmauri billing provider for transactions, settlement, voids, refunds, subscriptions, customers, payment methods, disputes, and webhooks. Source-declared APIs include `BraintreeBillingProvider`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_braintree/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_billing_braintree`.

Source-declared exports or types: `BraintreeBillingProvider`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_braintree/swarmauri_billing_braintree/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.billing_providers` → `BraintreeBillingProvider` → `swarmauri_billing_braintree.provider:BraintreeBillingProvider`
<!-- readme-standards:end entry-points -->

The package exposes a Swarmauri billing provider entry point:

```toml
[project.entry-points.'swarmauri.billing_providers']
BraintreeBillingProvider = "swarmauri_billing_braintree.provider:BraintreeBillingProvider"
```

### Injected Dependencies

The direct installation dependencies of `swarmauri_billing_braintree` are `swarmauri-core`, `swarmauri-base`, `braintree`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_braintree/swarmauri_billing_braintree/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_billing_braintree` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_billing_braintree`, use the source-declared public interfaces (`BraintreeBillingProvider`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_billing_braintree` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_braintree/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_billing_braintree`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_braintree/swarmauri_billing_braintree/__init__.py). The `swarmauri_billing_braintree` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_billing_braintree` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_billing_braintree` package directory for the maintained example source checks (Python compilation and non-Python file presence). Behavioral tests may live in the repository’s shared suites; the new README syntax test is not presented as runtime coverage for braintree SDK backed Swarmauri billing provider for transactions, settlement, voids, refunds, subscriptions, customers, payment methods, disputes, and webhooks.

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_billing_braintree` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_braintree/swarmauri_billing_braintree/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Q: Does this package call live Braintree APIs?**

A: Yes. It creates a `braintree.BraintreeGateway` from merchant credentials and calls Braintree SDK resources for transactions, customers, payment methods, subscriptions, disputes, and webhooks.

**Q: Which Swarmauri billing flows does it cover?**

A: It covers online payments, settlement capture, voids, refunds, customers, payment methods, subscriptions, dispute listing, and webhook parsing. Product, price, hosted-checkout, and report helpers remain compatibility placeholders where Braintree does not expose direct matching objects through the same API shape.

**Q: Why use this instead of swarmauri_billing_mock?**

A: Use this package when you want Braintree-shaped IDs, statuses, checkout URLs, and webhook headers. Use a generic mock when gateway-specific behavior is not relevant.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_billing_braintree`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_braintree/swarmauri_billing_braintree/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_billing_braintree` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_braintree/swarmauri_billing_braintree/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_braintree/pyproject.toml) provide the supporting context for `swarmauri_billing_braintree`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

Billing provider packages:

- [swarmauri_billing_adyen](https://pypi.org/project/swarmauri_billing_adyen/)
- [swarmauri_billing_authorize_net](https://pypi.org/project/swarmauri_billing_authorize_net/)
- [swarmauri_billing_mock](https://pypi.org/project/swarmauri_billing_mock/)
- [swarmauri_billing_paypal](https://pypi.org/project/swarmauri_billing_paypal/)
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
- [pypi: swarmauri_billing_braintree](https://pypi.org/project/swarmauri_billing_braintree/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you connect this provider to live Braintree APIs, preserve deterministic tests, document required credentials and webhook behavior, and add coverage for each supported billing capability.

### Development Setup

Work from the `pkgs/50-community/swarmauri_billing_braintree` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Important Scope Notes**

This package uses live Braintree SDK calls for payment, customer, payment-method, subscription, dispute, and webhook workflows. Production use requires valid Braintree merchant credentials and tokenized payment-method nonces or vaulted payment method tokens.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_billing_braintree` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_braintree/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_billing_braintree` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_billing_braintree` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_braintree/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_braintree/NOTICE) for attribution.
<!-- readme-standards:end notices -->
