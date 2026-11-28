# swarmauri_billing_paystack

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_billing_paystack</strong></p>
<p align="center">Paystack-backed Swarmauri billing provider for checkout, payment initialization, subscriptions, invoices, refunds, splits, and webhook verification.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_billing_paystack/"><img alt="pypi: swarmauri_billing_paystack" src="https://img.shields.io/pypi/v/swarmauri_billing_paystack?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paystack/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paystack/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paystack/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paystack/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paystack/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paystack/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_billing_paystack/"><img alt="Monthly PyPI downloads: swarmauri_billing_paystack" src="https://img.shields.io/pypi/dm/swarmauri_billing_paystack?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paystack/README.md"><img alt="README hits: swarmauri_billing_paystack" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_billing_paystack/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paystack/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paystack/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_billing_paystack` provides a Paystack-backed billing provider for the Swarmauri SDK. It connects Swarmauri billing interfaces to the `paystackapi` SDK for products, price-like product codes, hosted checkout, payment initialization, subscriptions, invoices, refunds, marketplace splits, split charges, disputes, and Paystack webhook HMAC verification.

### Why This Package

Use `swarmauri_billing_paystack` when a Swarmauri application needs Paystack payment flows without coupling business logic directly to Paystack SDK calls. The provider keeps Paystack products, transactions, subscriptions, invoices, refunds, splits, and risk checks behind the same Swarmauri billing interfaces used by other billing providers.

### When to Use

Choose `swarmauri_billing_paystack` when your integration needs paystack-backed Swarmauri billing provider for checkout, payment initialization, subscriptions, invoices, refunds, splits, and webhook verification. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Paystack-backed provider class registered as `PaystackBillingProvider`.
- Product and price workflows built on Paystack product APIs.
- Hosted checkout and payment intent initialization through Paystack transactions.
- Subscription lifecycle methods for creating and disabling subscriptions.
- Invoice creation and notification-oriented invoice actions.
- Refund creation and lookup through Paystack refund APIs.
- Marketplace split creation and split-charge initialization.
- Paystack webhook signature verification with `X-Paystack-Signature` and HMAC-SHA512.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

`swarmauri_billing_paystack` owns paystack-backed Swarmauri billing provider for checkout, payment initialization, subscriptions, invoices, refunds, splits, and webhook verification. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paystack/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `paystackapi`. Read the example’s inputs and service requirements before execution.

### Installation

Install with `uv`:

```bash
uv add swarmauri_billing_paystack
```

Install with `pip`:

```bash
pip install swarmauri_billing_paystack
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_billing_paystack
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_billing_paystack
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_billing_paystack
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paystack/docs/readme/quick_start.py).

```python
from swarmauri_billing_paystack import PaystackBillingProvider
from swarmauri_base.billing import CheckoutRequest, PriceSpec, ProductSpec

provider = PaystackBillingProvider(
    api_key="paystack",
    secret_key="sk_test_xxxxx",
)

product = provider.create_product(
    ProductSpec(name="Learning Portal", description="Online academy access"),
    idempotency_key="paystack-prod-001",
)

price = provider.create_price(
    product,
    PriceSpec(currency="NGN", unit_amount_minor=150000, nickname="Annual"),
    idempotency_key="paystack-price-001",
)

checkout = provider.create_checkout(
    price,
    CheckoutRequest(
        quantity=1,
        success_url="https://merchant.example/paystack/callback",
        customer_email="learner@example.com",
        idempotency_key="paystack-checkout-001",
    ),
)

print(product.id, price.id, checkout.url)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_billing_paystack` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paystack/docs/readme/usage.py).

```python
from swarmauri_billing_paystack import PaystackBillingProvider
from swarmauri_base.billing import CheckoutRequest, PriceSpec, ProductSpec

provider = PaystackBillingProvider(
    api_key="paystack",
    secret_key="sk_test_xxxxx",
)

product = provider.create_product(
    ProductSpec(name="Learning Portal", description="Online academy access"),
    idempotency_key="paystack-prod-001",
)

price = provider.create_price(
    product,
    PriceSpec(currency="NGN", unit_amount_minor=150000, nickname="Annual"),
    idempotency_key="paystack-price-001",
)

checkout = provider.create_checkout(
    price,
    CheckoutRequest(
        quantity=1,
        success_url="https://merchant.example/paystack/callback",
        customer_email="learner@example.com",
        idempotency_key="paystack-checkout-001",
    ),
)

print(product.id, price.id, checkout.url)
```
<!-- readme-standards:end example.usage -->

Create a product, price, and Paystack checkout session:


Initialize a Paystack payment intent:

```python
from swarmauri_billing_paystack import PaystackBillingProvider
from swarmauri_base.billing import PaymentIntentRequest

provider = PaystackBillingProvider(
    api_key="paystack",
    secret_key="sk_test_xxxxx",
)

payment = provider.create_payment_intent(
    PaymentIntentRequest(
        amount_minor=500000,
        currency="NGN",
        idempotency_key="paystack-payment-001",
        metadata={"order_id": "order-1001"},
    )
)

print(payment.id, payment.status)
```

Verify a Paystack webhook signature:

```python
from swarmauri_billing_paystack import PaystackBillingProvider

provider = PaystackBillingProvider(
    api_key="paystack",
    secret_key="sk_test_xxxxx",
)

is_valid = provider.verify_webhook_signature(
    raw_body=b'{"event":"charge.success"}',
    headers={"X-Paystack-Signature": "expected-hmac"},
    secret="sk_test_xxxxx",
)

print(is_valid)
```

### Configuration

Configure `swarmauri_billing_paystack` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paystack/swarmauri_billing_paystack/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paystack/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_billing_paystack` source raises `RuntimeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_billing_paystack` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `PaystackBillingProvider`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_billing_paystack` is located in `community` and owns paystack-backed Swarmauri billing provider for checkout, payment initialization, subscriptions, invoices, refunds, splits, and webhook verification. Source-declared APIs include `PaystackBillingProvider`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paystack/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_billing_paystack`.

Source-declared exports or types: `PaystackBillingProvider`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paystack/swarmauri_billing_paystack/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.billing_providers` → `PaystackBillingProvider` → `swarmauri_billing_paystack.provider:PaystackBillingProvider`
<!-- readme-standards:end entry-points -->

The package exposes a Swarmauri billing provider entry point:

```toml
[project.entry-points.'swarmauri.billing_providers']
PaystackBillingProvider = "swarmauri_billing_paystack.provider:PaystackBillingProvider"
```

### Injected Dependencies

The direct installation dependencies of `swarmauri_billing_paystack` are `swarmauri-core`, `swarmauri-base`, `paystackapi`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paystack/swarmauri_billing_paystack/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_billing_paystack` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_billing_paystack`, use the source-declared public interfaces (`PaystackBillingProvider`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_billing_paystack` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paystack/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_billing_paystack`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paystack/swarmauri_billing_paystack/__init__.py). The `swarmauri_billing_paystack` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_billing_paystack` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_billing_paystack` package directory for the maintained example source checks (Python compilation and non-Python file presence). Behavioral tests may live in the repository’s shared suites; the new README syntax test is not presented as runtime coverage for paystack-backed Swarmauri billing provider for checkout, payment initialization, subscriptions, invoices, refunds, splits, and webhook verification.

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_billing_paystack` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paystack/swarmauri_billing_paystack/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Q: Does this package call live Paystack APIs?**

A: Yes. The provider imports `paystackapi`, sets `Paystack.SECRET_KEY`, and calls SDK classes such as `Transaction`, `Product`, `Subscription`, `Invoice`, `TransactionSplit`, `Refund`, and `Dispute`.

**Q: Which Swarmauri billing flows does it support?**

A: It supports product creation, price-like product creation, hosted checkout, payment initialization, subscription create/cancel, invoice create/finalize/archive/uncollectible flows, refund create/fetch, marketplace split creation, split charges, dispute listing, and webhook signature verification.

**Q: What credential does it need?**

A: Pass a Paystack secret key through `secret_key`. Tests and examples use sandbox-style keys such as `sk_test_...`; production deployments should load secrets from a secure environment or vault.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_billing_paystack`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paystack/swarmauri_billing_paystack/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_billing_paystack` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

- [Paystack provider source](swarmauri_billing_paystack/provider.py)
- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)
- [Paystack API documentation](https://paystack.com/docs/api/)

### Related Packages

Billing provider packages:

- [swarmauri_billing_adyen](https://pypi.org/project/swarmauri_billing_adyen/)
- [swarmauri_billing_authorize_net](https://pypi.org/project/swarmauri_billing_authorize_net/)
- [swarmauri_billing_braintree](https://pypi.org/project/swarmauri_billing_braintree/)
- [swarmauri_billing_mock](https://pypi.org/project/swarmauri_billing_mock/)
- [swarmauri_billing_paypal](https://pypi.org/project/swarmauri_billing_paypal/)
- [swarmauri_billing_razorpay](https://pypi.org/project/swarmauri_billing_razorpay/)
- [swarmauri_billing_square](https://pypi.org/project/swarmauri_billing_square/)
- [swarmauri_billing_stripe](https://pypi.org/project/swarmauri_billing_stripe/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines billing capabilities and interfaces.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides billing specs, refs, mixins, and `BillingProviderBase`.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_billing_paystack](https://pypi.org/project/swarmauri_billing_paystack/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Contributions that expand Paystack coverage or improve resiliency are welcome. Include request and response traces with secrets redacted, update usage examples, and add tests for each billing capability you change.

### Development Setup

Work from the `pkgs/50-community/swarmauri_billing_paystack` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Important Scope Notes**

This package uses Paystack SDK calls for provider operations. Network access, Paystack credentials, API availability, account configuration, and Paystack response formats affect runtime behavior. Use sandbox keys for development and isolate live credentials through deployment secrets.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_billing_paystack` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paystack/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_billing_paystack` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_billing_paystack` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paystack/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_billing_paystack/NOTICE) for attribution.
<!-- readme-standards:end notices -->
